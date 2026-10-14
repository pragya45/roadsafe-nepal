"""Dependency-free HTTP API + static UI. For local demo/development use."""
import csv
import io
import json
import re
from datetime import date
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from .db import connect, seed

WEB = Path(__file__).resolve().parent.parent / 'web'
SEVERITIES = {'Low', 'Medium', 'High', 'Critical'}
CATEGORIES = {'Collision', 'Near miss', 'Road hazard', 'Other'}
MIME = {'.html': 'text/html', '.css': 'text/css', '.js': 'application/javascript', '.svg': 'image/svg+xml'}


def validate(payload):
    if not isinstance(payload, dict):
        raise ValueError('Expected a JSON object')
    out = {}
    for key in ('occurred_on', 'district', 'location', 'severity', 'category', 'description'):
        val = payload.get(key)
        if not isinstance(val, str) or not val.strip():
            raise ValueError(f'{key} is required')
        out[key] = val.strip()
    try:
        date.fromisoformat(out['occurred_on'])
    except ValueError:
        raise ValueError('occurred_on must be a valid YYYY-MM-DD date') from None
    if len(out['occurred_on']) != 10:
        raise ValueError('occurred_on must use YYYY-MM-DD')
    if out['severity'] not in SEVERITIES or out['category'] not in CATEGORIES:
        raise ValueError('Invalid severity or category')
    if any(len(out[k]) > maxlen for k, maxlen in [('district', 80), ('location', 120), ('description', 1200)]):
        raise ValueError('A text field is too long')
    for key, lo, hi in (('latitude', -90, 90), ('longitude', -180, 180)):
        val = payload.get(key)
        if val is None or val == '':
            out[key] = None
        else:
            try:
                out[key] = float(val)
            except (TypeError, ValueError):
                raise ValueError(f'{key} must be a number') from None
            if not lo <= out[key] <= hi:
                raise ValueError(f'{key} is out of range')
    return out


def query_incidents(db, args):
    where, values = [], []
    for name in ('district', 'severity', 'category'):
        value = args.get(name, [''])[0].strip()
        if value:
            where.append(f'{name} = ?')
            values.append(value)
    search = args.get('q', [''])[0].strip()
    if search:
        where.append('(location LIKE ? OR description LIKE ? OR district LIKE ?)')
        values += [f'%{search}%'] * 3
    clause = (' WHERE ' + ' AND '.join(where)) if where else ''
    rows = db.execute('SELECT * FROM incidents' + clause + ' ORDER BY occurred_on DESC, id DESC', values).fetchall()
    return [dict(r) for r in rows]


def stats(rows):
    by_severity = {k: 0 for k in ('Low','Medium','High','Critical')}
    by_category = {k: 0 for k in ('Collision','Near miss','Road hazard','Other')}
    by_district = {}
    by_month = {}
    for row in rows:
        by_severity[row['severity']] += 1
        by_category[row['category']] += 1
        by_district[row['district']] = by_district.get(row['district'], 0) + 1
        month = row['occurred_on'][:7]
        by_month[month] = by_month.get(month, 0) + 1
    return {'total': len(rows), 'high_priority': by_severity['High'] + by_severity['Critical'],
            'districts': len(by_district), 'by_severity': by_severity,
            'by_category': by_category, 'by_district': dict(sorted(by_district.items(), key=lambda x: -x[1])),
            'by_month': dict(sorted(by_month.items()))}


class Handler(BaseHTTPRequestHandler):
    def respond(self, status, data, content_type='application/json; charset=utf-8'):
        body = json.dumps(data).encode() if content_type.startswith('application/json') else data
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(body)))
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        url = urlparse(self.path)
        if url.path.startswith('/api/'):
            with connect() as db:
                rows = query_incidents(db, parse_qs(url.query))
                if url.path == '/api/incidents':
                    return self.respond(200, {'items': rows})
                if url.path == '/api/stats':
                    return self.respond(200, stats(rows))
                if url.path == '/api/export':
                    stream = io.StringIO()
                    columns = ['id','occurred_on','district','location','severity','category','description','latitude','longitude','created_at']
                    writer = csv.DictWriter(stream, fieldnames=columns)
                    writer.writeheader()
                    writer.writerows(rows)
                    return self.respond(200, stream.getvalue().encode('utf-8-sig'), 'text/csv; charset=utf-8')
            return self.respond(404, {'error': 'Unknown API endpoint'})
        path = url.path if url.path != '/' else '/index.html'
        file = (WEB / path.lstrip('/')).resolve()
        if not file.is_relative_to(WEB.resolve()) or not file.is_file():
            return self.respond(404, {'error': 'Not found'})
        return self.respond(200, file.read_bytes(), MIME.get(file.suffix, 'application/octet-stream'))

    def do_POST(self):
        if self.path != '/api/incidents':
            return self.respond(404, {'error': 'Not found'})
        try:
            length = int(self.headers.get('Content-Length', '0'))
            if length <= 0 or length > 100_000:
                return self.respond(413, {'error': 'Invalid request size'})
            item = validate(json.loads(self.rfile.read(length)))
            keys = list(item)
            with connect() as db:
                cursor = db.execute('INSERT INTO incidents (' + ','.join(keys) + ') VALUES (' + ','.join('?' for _ in keys) + ')', list(item.values()))
                db.commit()
                item['id'] = cursor.lastrowid
            return self.respond(201, item)
        except (ValueError, json.JSONDecodeError) as e:
            return self.respond(400, {'error': str(e)})

    def do_DELETE(self):
        match = re.fullmatch(r'/api/incidents/(\d+)', self.path)
        if not match:
            return self.respond(404, {'error': 'Not found'})
        with connect() as db:
            result = db.execute('DELETE FROM incidents WHERE id = ?', (int(match.group(1)),))
            db.commit()
        return self.respond(200 if result.rowcount else 404, {'deleted': bool(result.rowcount)})


def main():
    import argparse
    parser = argparse.ArgumentParser(description='RoadSafe Nepal local demo')
    parser.add_argument('--port', type=int, default=8000)
    parser.add_argument('--host', default='127.0.0.1')
    args = parser.parse_args()
    with connect() as db:
        seed(db)
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f'RoadSafe Nepal running at http://{args.host}:{args.port}')
    print('Demo data is synthetic; this server is for local use only. Press Ctrl+C to stop.')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()

if __name__ == '__main__':
    main()
