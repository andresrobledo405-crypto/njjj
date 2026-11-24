import csv
import io
from collections.abc import Iterable
from sqlite3 import Row


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
                writer.writerow(["" if value is None else value for value in tuple(row)])
        return stream
