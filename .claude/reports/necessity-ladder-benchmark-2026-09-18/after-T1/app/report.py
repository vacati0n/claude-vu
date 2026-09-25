"""Weekly sales report rendering."""
from datetime import date

from app.dates import parse_iso_date


def week_label(iso_day: str) -> str:
    """Return the ISO 8601 week label (YYYY-Www) for the given ISO date string.

    Raises ValueError on malformed input, exactly as parse_iso_date does.
    """
    d = parse_iso_date(iso_day)
    iso_year, iso_week, _ = d.isocalendar()
    return f"{iso_year}-W{iso_week:02d}"


def render_header(iso_day: str) -> str:
    d = parse_iso_date(iso_day)
    return f"Sales report for {d.isoformat()} ({week_label(iso_day)})"
