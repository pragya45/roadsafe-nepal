# RoadSafe Nepal — Incident Intelligence Dashboard

A polished **full-stack portfolio demonstration** for exploring road incident reports, patterns, and district hotspots. Built with **Python (standard library), SQLite, HTML, CSS, and JavaScript**. No pip install, Node.js, or API keys required.

> **Important:** All preloaded incident records are **fictional synthetic examples**. This is an educational demonstration, not a government service, emergency response tool, official dataset, or validated traffic-risk prediction model. Do not enter personal information or use its insights for safety-critical decisions.

## Features

- Responsive dashboard with KPI cards, severity visualization, and district hotspot ranking
- Filter by severity, category, or free-text search
- Create and delete incident reports with server-side input validation
- Persistent SQLite storage, with automatically loaded synthetic demo data
- Download filtered incident records as CSV
- REST API and automated unit tests
- No external services or JavaScript dependencies

## Quick start

**Requirements:** Python 3.10 or newer.

```bash
python -m app.server
```

Open **http://127.0.0.1:8000** in your browser. To use a different port:

```bash
python -m app.server --port 8080
```

On Windows, if `python` is unavailable, try `py -m app.server`.

The first run creates `roadsafe.db` in the project directory and loads 12 fictional example incidents. To reset the demo, stop the server, delete `roadsafe.db`, and restart.

## Run tests

```bash
python -m unittest discover -s tests -v
```

## API reference

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/incidents` | List records; filters: `q`, `district`, `severity`, `category` |
| GET | `/api/stats` | Summary metrics; accepts the same filters |
| GET | `/api/export` | Download filtered CSV |
| POST | `/api/incidents` | Create an incident with JSON body |
| DELETE | `/api/incidents/{id}` | Delete an incident |

Example:

```bash
curl 'http://127.0.0.1:8000/api/stats?severity=High'
```

Example POST:

```bash
curl -X POST http://127.0.0.1:8000/api/incidents \
  -H 'Content-Type: application/json' \
  -d '{"occurred_on":"2026-10-01","district":"Kathmandu","location":"Kalanki","severity":"Medium","category":"Road hazard","description":"Synthetic test incident"}'
```

## Project structure

```text
roadsafe-nepal/
├── app/
│   ├── __init__.py
│   ├── db.py              # Database schema, connection, synthetic seed data
│   └── server.py          # HTTP routes, validation, reporting
├── web/
│   ├── index.html         # Dashboard and report form
│   ├── styles.css         # Responsive design
│   └── app.js             # Client-side API integration and charts
├── tests/
│   └── test_app.py        # Unit tests
├── docs/
│   └── ARCHITECTURE.md    # Design notes and future enhancements
├── .gitignore
├── LICENSE
└── README.md
```

## Architecture and trade-offs

The Python HTTP server handles JSON API requests and serves the frontend from the same origin. SQLite provides a simple, local persistent database; parameterized queries reduce SQL injection risk. The frontend renders aggregated statistics from the API and escapes user-provided text before inserting it into HTML.

This is designed for **local learning and demonstration**, not production deployment: it has no authentication, rate limiting, audit logs, or multi-user permissions. Do not expose it publicly without replacing the development server and adding those safeguards.

## Suggested improvements

1. Add user accounts, role-based access, and an audit log.
2. Add map visualization with a proper map provider and licensed geodata.
3. Support CSV import with data quality checks and duplicate detection.
4. Add deployment with Docker and CI testing.
5. Introduce a clearly labeled predictive model only with a real, appropriately licensed and evaluated dataset.

## Portfolio note

This repository is a **starter project created with AI assistance**. Review, run, test, and modify it before publishing. Describe your own contributions accurately rather than claiming you wrote everything independently.

## License

MIT — see [LICENSE](LICENSE).
