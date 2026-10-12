import csv

from weather_rest_api_to_json_dashboard import (
    build_records,
    load_history,
    save_csv,
    save_history,
)

FORECAST_JSON = {
    "daily": {
        "time": ["2026-10-12", "2026-10-13"],
        "temperature_2m_max": [20.5, 22.0],
        "temperature_2m_min": [10.1, 11.3],
        "precipitation_sum": [0.0, 4.2],
        "weathercode": [3, 61],
    }
}


def test_build_records_flattens_daily_columns():
    records = build_records("2026-10-12T10:00:00+00:00", "Madrid", FORECAST_JSON)

    assert len(records) == 2
    assert records[1] == {
        "fetched_at": "2026-10-12T10:00:00+00:00",
        "city": "Madrid",
        "date": "2026-10-13",
        "temp_max": 22.0,
        "temp_min": 11.3,
        "precipitation": 4.2,
        "weathercode": 61,
    }


def test_load_history_returns_empty_list_when_file_missing(tmp_path):
    assert load_history(tmp_path / "missing.json") == []


def test_history_round_trip(tmp_path):
    path = tmp_path / "history.json"
    records = build_records("2026-10-12T10:00:00+00:00", "Bogotá", FORECAST_JSON)

    save_history(path, records)

    assert load_history(path) == records


def test_save_csv_writes_header_and_rows(tmp_path):
    path = tmp_path / "history.csv"
    records = build_records("2026-10-12T10:00:00+00:00", "Bogotá", FORECAST_JSON)

    save_csv(path, records)

    with path.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 2
    assert rows[0]["city"] == "Bogotá"
    assert rows[1]["precipitation"] == "4.2"
