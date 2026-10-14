# Architecture

Browser → Python HTTP server → SQLite database

The API provides filtered incident rows and summary statistics. The browser requests both concurrently, then updates KPI cards, severity bars, district rankings, and the incident table. Filters are encoded as URL query parameters. POST requests are validated and persisted; DELETE removes records by numeric ID.

## Data model

`incidents(id, occurred_on, district, location, severity, category, description, latitude, longitude, created_at)`

Indexed fields: `occurred_on`, `district`. The database is created automatically at startup.

## Security considerations

- SQL parameterization for user-supplied filters and IDs
- Whitelisted severity and category values
- Date, coordinate, length and required-field validation
- HTML escaping for displayed user input
- Request body size limit on POST
- Bound to localhost by default

**Not production hardened:** no login, authorization, CSRF protection, rate limits, encryption-at-rest, or incident verification. Do not expose to the internet or process real sensitive incident reports.

## Future roadmap

- Authentication and roles
- Accessible map component
- Pagination and sort controls
- Database migrations
- Integration tests and CI
- CSV import validation
