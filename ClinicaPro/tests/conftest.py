import os
import tempfile

_TMP = tempfile.mkdtemp(prefix="clinicapro-test-")
os.environ["CLINICAPRO_DATA_DIR"] = _TMP

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.db import get_connection  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture()
def client():
    with TestClient(app) as c:
        yield c
        conn = get_connection()
        for table in ("payments", "consultations", "appointments", "professionals", "patients"):
            conn.execute(f"DELETE FROM {table}")
        conn.commit()
        conn.close()


@pytest.fixture()
def base(client):
    patient = client.post("/api/patients", json={"name": "Ana Soto", "rut": "12.345.678-5"}).json()
    other = client.post("/api/patients", json={"name": "Luis Pérez"}).json()
    doctor = client.post("/api/professionals", json={"name": "Dra. Rojas", "specialty": "Medicina general"}).json()
    return patient, other, doctor
