import ast
import json
from datetime import datetime
from functools import lru_cache

from sqlalchemy import text

from app.services.database import engine


MONTHS = [
    "Januari",
    "Februari",
    "Maret",
    "April",
    "Mei",
    "Juni",
    "Juli",
    "Agustus",
    "September",
    "Oktober",
    "November",
    "Desember",
]


def parse_date(value):
    return datetime.strptime(value, "%Y-%m-%d").date()


def parse_literal(value, fallback):
    if value is None:
        return fallback

    if isinstance(value, (dict, list)):
        return value

    raw = str(value).strip()

    if not raw:
        return fallback

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass

    try:
        return ast.literal_eval(raw)
    except (SyntaxError, ValueError):
        return fallback


def format_date(value):
    if not value:
        return "-"

    year, month, day = str(value).split("-")
    return f"{day}-{month}-{year}"


def get_day_title(wewaran):
    if not isinstance(wewaran, dict):
        return "-"

    parts = [wewaran.get("saptawara"), wewaran.get("pancawara")]
    return " ".join(str(part) for part in parts if part) or "-"


def get_rule_note(rule, ceremony):
    if rule.get("rule_text_id"):
        return rule["rule_text_id"]

    return f"{rule.get('status') or 'Dewasa'} untuk {ceremony}."


def get_result_group(status):
    if status == "Baik":
        return "ayu"

    if status == "Ala-Ayu":
        return "dipakai"

    return "ala"


def build_result_item(row, rule, ceremony):
    return {
        "date": format_date(row.get("tanggal")),
        "title": rule.get("nama_entitas") or "",
        "note": get_rule_note(rule, ceremony),
    }


@lru_cache(maxsize=1)
def get_dewasa_options():
    ceremonies_by_category = {}

    with engine.connect() as conn:
        category_rows = conn.execute(
            text(r"""
                SELECT DISTINCT match[1] AS value
                FROM dewasa
                CROSS JOIN LATERAL regexp_matches(
                    dewasa,
                    '''jenis_yadnya'': ''([^'']+)''',
                    'g'
                ) AS match
                ORDER BY value
            """)
        ).mappings().all()
        ceremony_rows = conn.execute(
            text(r"""
                SELECT DISTINCT match[2] AS category, match[1] AS ceremony
                FROM dewasa
                CROSS JOIN LATERAL regexp_matches(
                    dewasa,
                    '''upacara'': ''([^'']+)'', ''jenis_yadnya'': ''([^'']+)''',
                    'g'
                ) AS match
                ORDER BY category, ceremony
            """)
        ).mappings().all()
        year_rows = conn.execute(
            text("""
                SELECT DISTINCT substring(tanggal from 1 for 4) AS year
                FROM dewasa
                ORDER BY year
            """)
        ).mappings().all()
        date_range = conn.execute(
            text("""
                SELECT MIN(tanggal) AS min_date, MAX(tanggal) AS max_date
                FROM dewasa
            """)
        ).mappings().first()

    categories = [row["value"] for row in category_rows if row.get("value")]
    ceremonies = []

    for row in ceremony_rows:
        category = row.get("category")
        ceremony = row.get("ceremony")

        if not category or not ceremony:
            continue

        ceremonies.append(ceremony)
        ceremonies_by_category.setdefault(category, []).append(ceremony)

    return {
        "categories": categories,
        "ceremonies": sorted(set(ceremonies)),
        "ceremonies_by_category": {
            category: sorted(set(values))
            for category, values in ceremonies_by_category.items()
        },
        "years": [row["year"] for row in year_rows if row.get("year")],
        "date_range": {
            "min": date_range.get("min_date") if date_range else "",
            "max": date_range.get("max_date") if date_range else "",
        },
    }


def search_dewasa(jenis_yadnya=None, upacara=None, tanggal=None, bulan=None, tahun=None):
    grouped = {
        "ayu": [],
        "dipakai": [],
        "ala": [],
    }

    params = {}
    where = []

    if tanggal:
        parse_date(tanggal)
        where.append("tanggal = :tanggal")
        params["tanggal"] = tanggal
    else:
        if tahun is None or bulan is None:
            raise ValueError("Tahun dan bulan wajib diisi untuk pencarian per bulan")

        month_number = int(bulan)

        if month_number < 1 or month_number > 12:
            raise ValueError("Bulan harus berada di antara 1 sampai 12")

        year_number = int(tahun)
        where.append("tanggal LIKE :month_prefix")
        params["month_prefix"] = f"{year_number:04d}-{month_number:02d}-%"

    with engine.connect() as conn:
        rows = conn.execute(
            text(f"""
                SELECT tanggal, wewaran, dewasa
                FROM dewasa
                WHERE {" AND ".join(where)}
                ORDER BY tanggal
            """),
            params,
        ).mappings().all()

    for row in rows:
        dewasa_items = parse_literal(row.get("dewasa"), [])

        if not isinstance(dewasa_items, list):
            continue

        for item in dewasa_items:
            item_upacara = item.get("upacara")
            if upacara and item_upacara != upacara:
                continue
            if jenis_yadnya and item.get("jenis_yadnya") != jenis_yadnya:
                continue

            rules = item.get("rules_match") or []

            for rule in rules:
                group = get_result_group(rule.get("status"))
                grouped[group].append(build_result_item(row, rule, item_upacara))

    return grouped
