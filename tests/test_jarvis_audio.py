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



class Voz(unittest.TestCase):
    def test_speak_vuelve_y_registra_en_gui(self):
        mensajes = []
        j.speak("hola", mensajes.append)
        self.assertEqual(mensajes, ["JARVIS: hola"])



class Auditoria(unittest.TestCase):
    def test_memoria_usa_ruta_absoluta_y_persiste(self):
        import os
        import tempfile
        self.assertTrue(os.path.isabs(j.DB_NAME))
        with tempfile.TemporaryDirectory() as d, mock.patch.object(j, "DB_NAME", os.path.join(d, "t.db")):
            j.inicializar_base_datos()
            j.recordar_dato("Color", "azul")
            self.assertIn("azul", j.buscar_en_memoria("color"))
            self.assertIn("No poseo", j.buscar_en_memoria("nada"))

    def test_limpiar_markdown_para_voz(self):
        self.assertEqual(j.limpiar_para_voz("**Hola** [web](http://x.com) `ok`"), "Hola web ok")
        self.assertEqual(j.limpiar_para_voz(None), "")

    def test_volumen_nivel_invalido_no_revienta(self):
        self.assertIn("número", j.controlar_volumen("establecer", "alto"))
        self.assertIn("número", j.controlar_volumen("establecer", None))


if __name__ == "__main__":
    unittest.main()
