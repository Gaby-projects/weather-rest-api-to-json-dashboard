import csv
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

import requests
import truststore

from weather_rest_api_to_json_dashboard.dashboard import generate_dashboard

# Use the OS certificate store (via `truststore`) instead of the bundled
# `certifi` list: on machines where local security software (e.g. an
# antivirus doing TLS inspection) injects its own root certificate into the
# OS trust store, `certifi`'s static bundle won't know about it and every
# HTTPS request fails with CERTIFICATE_VERIFY_FAILED.
truststore.inject_into_ssl()

FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
FORECAST_DAYS = 7
REQUEST_TIMEOUT = 30  # seconds
HISTORY_FILE = Path("weather_history.json")
CSV_FILE = Path("weather_history.csv")
DASHBOARD_FILE = Path("dashboard.html")
CSV_COLUMNS = [
    "fetched_at",
    "city",
    "date",
    "temp_max",
    "temp_min",
    "precipitation",
    "weathercode",
]

CITIES = [
    {"name": "Buenos Aires", "latitude": -34.6037, "longitude": -58.3816},
    {"name": "Madrid", "latitude": 40.4168, "longitude": -3.7038},
    {"name": "Mexico City", "latitude": 19.4326, "longitude": -99.1332},
    {"name": "Bogotá", "latitude": 4.7110, "longitude": -74.0721},
    {"name": "Santiago", "latitude": -33.4489, "longitude": -70.6693},
]


def fetch_forecast(latitude: float, longitude: float) -> dict:
    response = requests.get(
        FORECAST_URL,
        params={
            "latitude": latitude,
            "longitude": longitude,
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,weathercode",
            "timezone": "auto",
            "forecast_days": FORECAST_DAYS,
        },
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()
    return response.json()


def build_records(fetched_at: str, city: str, forecast_json: dict) -> list[dict]:
    daily = forecast_json["daily"]
    return [
        {
            "fetched_at": fetched_at,
            "city": city,
            "date": date,
            "temp_max": temp_max,
            "temp_min": temp_min,
            "precipitation": precipitation,
            "weathercode": weathercode,
        }
        for date, temp_max, temp_min, precipitation, weathercode in zip(
            daily["time"],
            daily["temperature_2m_max"],
            daily["temperature_2m_min"],
            daily["precipitation_sum"],
            daily["weathercode"],
        )
    ]


def load_history(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_history(path: Path, history: list[dict]) -> None:
    with path.open("w", encoding="utf-8") as f:
        json.dump(history, f, indent=2)


def save_csv(path: Path, history: list[dict]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        writer.writerows(history)


def main() -> None:
    # On Windows, stdout may default to a legacy code page (e.g. cp1252 when
    # piped), which garbles "°" and city names like "Bogotá".
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    fetched_at = datetime.now(UTC).isoformat()
    history = load_history(HISTORY_FILE)

    for city in CITIES:
        forecast_json = fetch_forecast(city["latitude"], city["longitude"])
        records = build_records(fetched_at, city["name"], forecast_json)
        history.extend(records)

        print(f"\n{city['name']} - next {FORECAST_DAYS} days:")
        for record in records:
            print(
                f"  {record['date']}: max {record['temp_max']}°C, "
                f"min {record['temp_min']}°C, "
                f"precipitation {record['precipitation']}mm"
            )

    save_history(HISTORY_FILE, history)
    save_csv(CSV_FILE, history)
    generate_dashboard(history, DASHBOARD_FILE, [city["name"] for city in CITIES])
    print(f"\nSaved {len(history)} total records to {HISTORY_FILE} and {CSV_FILE}")
    print(f"Dashboard written to {DASHBOARD_FILE}")
