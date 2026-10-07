"""Pruebas de controlar_volumen con el subsistema de audio simulado (sin hardware)."""
import sys
import types
import unittest
from unittest import mock

# Librerías de GUI/voz/IoT no necesarias para probar la lógica de volumen.
for nombre in ["customtkinter", "pyttsx3", "speech_recognition", "tinytuya",
               "pyperclip", "psutil", "google", "google.genai", "google.genai.types"]:
    sys.modules.setdefault(nombre, mock.MagicMock())
sys.modules["google"].genai = sys.modules["google.genai"]
sys.modules["google.genai"].types = sys.modules["google.genai.types"]
sys.modules["customtkinter"].CTk = object

import jarvis_system_mcp as j  # noqa: E402


class VolumenLinux(unittest.TestCase):
    def setUp(self):
        self.estado = {"vol": 40, "mute": False}
        self.llamadas = []

        def falso(cmd):
            self.llamadas.append(cmd)
            if cmd[1] == "set-sink-volume":
                v = cmd[3]
                if v[0] in "+-":
                    self.estado["vol"] += int(v[:-1])
                else:
                    self.estado["vol"] = int(v[:-1])
            elif cmd[1] == "set-sink-mute":
                self.estado["mute"] = cmd[3] == "1"
            elif cmd[1] == "get-sink-volume":
                return f"Volume: front-left: 1 / {self.estado['vol']}% / 0 dB"
            elif cmd[1] == "get-sink-mute":
                return "Mute: " + ("yes" if self.estado["mute"] else "no")
            return ""

        p1 = mock.patch.object(j, "_ejecutar", falso)
        p2 = mock.patch.object(j.platform, "system", return_value="Linux")
        p1.start(); p2.start()
        self.addCleanup(p1.stop); self.addCleanup(p2.stop)

    def test_establecer(self):
        self.assertIn("75%", j.controlar_volumen("establecer", 75))

    def test_subir_y_bajar(self):
        self.assertIn("50%", j.controlar_volumen("subir"))
        self.assertIn("40%", j.controlar_volumen("bajar"))

    def test_silenciar(self):
        self.assertIn("silenciado", j.controlar_volumen("silenciar"))
        self.assertIn("activo", j.controlar_volumen("activar_sonido"))

    def test_consultar_no_modifica(self):
        j.controlar_volumen("consultar")
        self.assertEqual(self.estado["vol"], 40)

    def test_nivel_fuera_de_rango(self):
        self.assertIn("entre 0 y 100", j.controlar_volumen("establecer", 150))

    def test_accion_invalida(self):
        self.assertIn("no soportada", j.controlar_volumen("explotar"))

    def test_herramienta_registrada(self):
        self.assertIn(j.controlar_volumen, j.herramientas_jarvis)


if __name__ == "__main__":
    unittest.main()
