# Weather REST API to JSON Dashboard

A small Python script that fetches the 7-day weather forecast for five cities from the
[Open-Meteo](https://open-meteo.com/) API (no API key required) and keeps an accumulating
history of every forecast it has fetched, exported as JSON, CSV and a static HTML dashboard.

![Weather forecast dashboard: KPI cards and a 7-day table per city](pics/dashboard.png)

## Features

- **Forecast history:** every run appends to the history instead of overwriting it, so you can
  compare how forecasts for the same day change over time.
- **Three outputs per run:** `weather_history.json`, `weather_history.csv` (for Excel/Sheets or
  pandas) and `dashboard.html`.
- **Static dashboard:** KPI cards per city (average max/min temperature, total precipitation,
  rainiest day) and a 7-day table, built from the latest fetch. Open it by double-clicking: no
  server or internet connection needed. Works on mobile too.
- **Works behind TLS-inspecting software:** uses the OS certificate store (`truststore`), so
  HTTPS requests don't fail when an antivirus or proxy injects its own root certificate.

## Cities

| City | Latitude | Longitude |
|---|---|---|
| Buenos Aires | -34.6037 | -58.3816 |
| Madrid | 40.4168 | -3.7038 |
| Mexico City | 19.4326 | -99.1332 |
| Bogotá | 4.7110 | -74.0721 |
| Santiago | -33.4489 | -70.6693 |

## Setup

Requires [`uv`](https://docs.astral.sh/uv/) and Python >= 3.14 (uv installs it if needed).

```bash
uv sync
```

## Usage

```bash
uv run weather-rest-api-to-json-dashboard
```

Each run prints a 7-day summary per city to the console and writes the three output files to
the current directory (they are created on the first run).

## Tests

```bash
uv run pytest
```

GitHub Actions runs `ruff` and the test suite on every push and pull request to `main`.

## Output format

Each record in `weather_history.json` (and each row in `weather_history.csv`) looks like:

```json
{
  "fetched_at": "2026-09-07T13:23:17.067568+00:00",
  "city": "Madrid",
  "date": "2026-09-07",
  "temp_max": 36.4,
  "temp_min": 20.9,
  "precipitation": 0.0,
  "weathercode": 3
}
```

- `fetched_at`: when the forecast was fetched (UTC).
- `date`: the forecast day, in the city's local time zone.
- `temp_max` / `temp_min`: °C. `precipitation`: daily total in mm.
- `weathercode`: [WMO weather code](https://open-meteo.com/en/docs#weather_variable_documentation).

If the API returns `null` for a value, it is stored as `null` and the dashboard shows a dash.

## Project structure

```
src/weather_rest_api_to_json_dashboard/
├── __init__.py   # fetch from Open-Meteo, build records, save JSON/CSV, main()
├── __main__.py   # allows `python -m weather_rest_api_to_json_dashboard`
└── dashboard.py  # renders the static HTML dashboard
tests/              # pytest suite (records, history files, dashboard KPIs)
.github/workflows/  # CI: ruff + pytest
```
