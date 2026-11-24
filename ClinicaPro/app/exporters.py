import csv
import io
from collections.abc import Iterable
from sqlite3 import Row


def safe_cell(value):
    """Evita inyección de fórmulas en Excel: texto que empieza con = + - @ se antepone con comilla."""
    if value is None:
        return ""
    if isinstance(value, str) and value[:1] in ("=", "+", "-", "@", "\t", "\r"):
        return "'" + value
    return value


class CsvExporter:
    """Exporta filas a CSV con BOM UTF-8 para que Excel respete las tildes."""

    def export(self, rows: Iterable[Row]) -> io.StringIO:
        rows = list(rows)
        stream = io.StringIO()
        stream.write("\ufeff")
        if rows:
            writer = csv.writer(stream, delimiter=";")
            writer.writerow(rows[0].keys())
            for row in rows:
                writer.writerow([safe_cell(value) for value in tuple(row)])
        return stream
