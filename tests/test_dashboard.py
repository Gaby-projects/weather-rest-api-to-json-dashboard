from weather_rest_api_to_json_dashboard.dashboard import (
    _compute_kpis,
    _latest_snapshot,
    _temp_bar_width,
    generate_dashboard,
)


def _record(fetched_at, city, date, temp_max, temp_min, precipitation):
    return {
        "fetched_at": fetched_at,
        "city": city,
        "date": date,
        "temp_max": temp_max,
        "temp_min": temp_min,
        "precipitation": precipitation,
        "weathercode": 0,
    }


def test_compute_kpis():
    records = [
        _record("t", "Madrid", "2026-10-12", 20.0, 10.0, 1.0),
        _record("t", "Madrid", "2026-10-13", 24.0, 12.0, 5.0),
    ]

    kpis = _compute_kpis(records)

    assert kpis["avg_max"] == 22.0
    assert kpis["avg_min"] == 11.0
    assert kpis["total_precip"] == 6.0
    assert kpis["rainiest_date"] == "2026-10-13"
    assert kpis["rainiest_amount"] == 5.0


def test_compute_kpis_ignores_null_values():
    records = [
        _record("t", "Madrid", "2026-10-12", 20.0, None, None),
        _record("t", "Madrid", "2026-10-13", None, None, None),
    ]

    kpis = _compute_kpis(records)

    assert kpis["avg_max"] == 20.0
    assert kpis["avg_min"] is None
    assert kpis["total_precip"] is None
    assert kpis["rainiest_amount"] is None


def test_latest_snapshot_keeps_only_most_recent_fetch_sorted_by_date():
    history = [
        _record("2026-10-11T10:00:00+00:00", "Madrid", "2026-10-11", 18.0, 9.0, 0.0),
        _record("2026-10-12T10:00:00+00:00", "Madrid", "2026-10-13", 21.0, 10.0, 0.0),
        _record("2026-10-12T10:00:00+00:00", "Madrid", "2026-10-12", 20.0, 10.0, 0.0),
    ]

    fetched_at, by_city = _latest_snapshot(history, ["Madrid", "Santiago"])

    assert fetched_at == "2026-10-12T10:00:00+00:00"
    assert [r["date"] for r in by_city["Madrid"]] == ["2026-10-12", "2026-10-13"]
    assert by_city["Santiago"] == []


def test_temp_bar_width_is_clamped():
    assert _temp_bar_width(-5.0) == 0.0
    assert _temp_bar_width(20.0) == 50.0
    assert _temp_bar_width(55.0) == 100.0
    assert _temp_bar_width(None) == 0.0


def test_generate_dashboard_renders_nulls_as_dash(tmp_path):
    path = tmp_path / "dashboard.html"
    history = [_record("t", "Madrid", "2026-10-12", 20.0, None, None)]

    generate_dashboard(history, path, ["Madrid"])

    html = path.read_text(encoding="utf-8")
    assert "Madrid" in html
    assert "&ndash;" in html
    assert 'name="viewport"' in html


def test_generate_dashboard_without_data(tmp_path):
    path = tmp_path / "dashboard.html"

    generate_dashboard([], path, ["Madrid"])

    assert "No data yet" in path.read_text(encoding="utf-8")
