"""Genera revision_app_gpt/codigo_kinepro.txt: el código de la app en un solo archivo para que un revisor externo (p. ej. ChatGPT) lo lea.
No incluye datos de pacientes, bases de datos, claves ni la biblioteca clínica (esa se revisa con revision_gpt/)."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FILES = ["README.md", "DEPLOY.md", "requirements.txt", "app/config.py", "app/db.py", "app/auth.py", "app/main.py", "app/kine.py",
         "app/library.py", "app/exporters.py", "app/static/index.html", "app/static/app.css", "app/static/app.js", "app/static/sw.js",
         "tests/conftest.py", "tests/test_kinepro.py", "tests/test_kine.py", "tests/test_auth_library.py", "tests/test_ask.py", "../render.yaml"]
SECRET = re.compile(r"(sk-[A-Za-z0-9]{20,}|gh[pousr]_[A-Za-z0-9]{20,}|BEGIN (RSA |EC )?PRIVATE KEY)")

out = ["# KinePro — código para revisión\n(Cada archivo empieza con una línea `===== ruta =====`.)\n"]
for rel in FILES:
    text = (ROOT / rel).read_text(encoding="utf-8")
    if SECRET.search(text):
        raise SystemExit(f"Posible secreto en {rel}; no se genera el paquete.")
    out.append(f"\n===== {Path(rel).as_posix().lstrip('./')} =====\n{text}")
target = ROOT / "revision_app_gpt" / "codigo_kinepro.txt"
target.write_text("".join(out), encoding="utf-8")
print(f"{target} · {target.stat().st_size // 1024} KB")
