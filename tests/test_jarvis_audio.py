"""capturar_audio con un micrófono simulado: silencio -> voz -> silencio."""
import array
import sys
import unittest
from unittest import mock

for nombre in ["customtkinter", "pyttsx3", "tinytuya", "pyperclip", "psutil",
               "google", "google.genai", "google.genai.types"]:
    sys.modules.setdefault(nombre, mock.MagicMock())
sys.modules["google"].genai = sys.modules["google.genai"]
sys.modules["google.genai"].types = sys.modules["google.genai.types"]
sys.modules["customtkinter"].CTk = object
sr_falso = mock.MagicMock()
sr_falso.AudioData = lambda datos, tasa, ancho: (datos, tasa, ancho)
sys.modules["speech_recognition"] = sr_falso

import jarvis_system_mcp as j  # noqa: E402


def bloque(amplitud):
    return array.array("h", [amplitud if i % 2 else -amplitud for i in range(j.BLOQUE)]).tobytes()


class FlujoFalso:
    def __init__(self, bloques):
        self.bloques = iter(bloques)
    def __enter__(self):
        return self
    def __exit__(self, *a):
        return False
    def read(self, n):
        return (next(self.bloques, bloque(0)), False)


class CapturaAudio(unittest.TestCase):
    def capturar(self, bloques, **kw):
        sd = mock.MagicMock()
        sd.RawInputStream = lambda **_: FlujoFalso(bloques)
        with mock.patch.dict(sys.modules, {"sounddevice": sd}):
            return j.capturar_audio(**kw)

    def test_detecta_voz_y_corta_en_silencio(self):
        bloques = [bloque(50)] * 4 + [bloque(4000)] * 5 + [bloque(50)] * 12
        datos, tasa, ancho = self.capturar(bloques)
        self.assertEqual((tasa, ancho), (16000, 2))
        self.assertGreaterEqual(len(datos), 5 * j.BLOQUE * 2)

    def test_sin_voz_devuelve_none(self):
        self.assertIsNone(self.capturar([bloque(50)] * 200, espera_max=1.0))


if __name__ == "__main__":
    unittest.main()
