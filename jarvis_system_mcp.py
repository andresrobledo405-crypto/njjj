import datetime
import math
import os
import platform
import re
import sqlite3
import subprocess
import threading
import time
import sys
import webbrowser
import customtkinter as ctk
import pyttsx3
import speech_recognition as sr
import tinytuya
import pyperclip
import psutil
from google import genai
from google.genai import types

if sys.stdout is None or sys.stderr is None:  # pythonw: sin consola
    _log = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "jarvis.log"), "a", encoding="utf-8", buffering=1)
    sys.stdout = sys.stdout or _log
    sys.stderr = sys.stderr or _log

# =====================================================================
# 1. BASE DE DATOS Y MEMORIA PERSISTENTE (SQLITE3)
# =====================================================================
DB_NAME = "jarvis_system.db"

def inicializar_base_datos():
    """Crea e inicializa la tabla de memoria del asistente si no existe."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS memoria (
            clave TEXT PRIMARY KEY,
            valor TEXT
        )
    """)
    conn.commit()
    conn.close()

def recordar_dato(clave: str, valor: str) -> str:
    """Guarda información contextual sobre el usuario o el entorno en la base de datos."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO memoria (clave, valor) VALUES (?, ?)", (clave.lower(), valor))
    conn.commit()
    conn.close()
    return f"He almacenado el registro en mi base de datos central: {clave} es {valor}."

def buscar_en_memoria(clave: str) -> str:
    """Recupera datos históricos guardados en la memoria persistente."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT valor FROM memoria WHERE clave = ?", (clave.lower(),))
    row = cursor.fetchone()
    conn.close()
    return f"Registros para '{clave}': {row[0]}." if row else f"No poseo registros sobre '{clave}'."

# =====================================================================
# 2. HERRAMIENTAS DE CONTROL DE HARDWARE Y SISTEMA
# =====================================================================
def diagnostico_sistema() -> str:
    """Devuelve el estado de salud actual de la computadora (CPU, RAM y Batería)."""
    cpu = psutil.cpu_percent(interval=0.5)
    ram = psutil.virtual_memory().percent
    bateria = psutil.sensors_battery()
    bat_str = f"{bateria.percent}%" if bateria else "No detectada"
    return f"Diagnóstico de Hardware: Uso de CPU al {cpu}%, Memoria RAM al {ram}%, Nivel de batería: {bat_str}."

def leer_portapapeles() -> str:
    """Lee el texto actual guardado en el portapapeles (Clipboard) de la PC."""
    texto = pyperclip.paste()
    return f"Contenido del portapapeles: '{texto}'" if texto else "El portapapeles está vacío, Señor."

def escribir_portapapeles(texto: str) -> str:
    """Inyecta un texto directamente en el portapapeles del sistema del usuario."""
    pyperclip.copy(texto)
    return "El texto ha sido copiado al portapapeles del sistema operativo, Señor."

# ---- Control de volumen del sistema operativo -----------------------
PASO_VOLUMEN = 10  # puntos porcentuales por cada "subir" / "bajar"

def _ejecutar(cmd: list) -> str:
    return subprocess.run(cmd, capture_output=True, text=True, timeout=5, check=True).stdout

def _volumen_windows(accion: str, nivel: int):
    # Requiere: pip install pycaw comtypes (solo Windows)
    from ctypes import POINTER, cast
    from comtypes import CLSCTX_ALL
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    dispositivo = AudioUtilities.GetSpeakers()
    interfaz = dispositivo.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    vol = cast(interfaz, POINTER(IAudioEndpointVolume))
    if accion == "silenciar":
        vol.SetMute(1, None)
    elif accion == "activar_sonido":
        vol.SetMute(0, None)
    elif accion in ("establecer", "subir", "bajar"):
        actual = round(vol.GetMasterVolumeLevelScalar() * 100)
        destino = {"establecer": nivel, "subir": actual + PASO_VOLUMEN, "bajar": actual - PASO_VOLUMEN}[accion]
        vol.SetMasterVolumeLevelScalar(max(0, min(100, destino)) / 100, None)
    return round(vol.GetMasterVolumeLevelScalar() * 100), bool(vol.GetMute())

def _volumen_macos(accion: str, nivel: int):
    def leer():
        return int(_ejecutar(["osascript", "-e", "output volume of (get volume settings)"]).strip())
    if accion == "silenciar":
        _ejecutar(["osascript", "-e", "set volume with output muted"])
    elif accion == "activar_sonido":
        _ejecutar(["osascript", "-e", "set volume without output muted"])
    elif accion in ("establecer", "subir", "bajar"):
        destino = {"establecer": nivel, "subir": leer() + PASO_VOLUMEN, "bajar": leer() - PASO_VOLUMEN}[accion]
        _ejecutar(["osascript", "-e", f"set volume output volume {max(0, min(100, destino))}"])
    silenciado = _ejecutar(["osascript", "-e", "output muted of (get volume settings)"]).strip() == "true"
    return leer(), silenciado

def _volumen_linux(accion: str, nivel: int):
    # Requiere pactl (PulseAudio / PipeWire)
    sink = "@DEFAULT_SINK@"
    if accion == "silenciar":
        _ejecutar(["pactl", "set-sink-mute", sink, "1"])
    elif accion == "activar_sonido":
        _ejecutar(["pactl", "set-sink-mute", sink, "0"])
    elif accion == "establecer":
        _ejecutar(["pactl", "set-sink-volume", sink, f"{nivel}%"])
    elif accion in ("subir", "bajar"):
        signo = "+" if accion == "subir" else "-"
        _ejecutar(["pactl", "set-sink-volume", sink, f"{signo}{PASO_VOLUMEN}%"])
    porcentaje = int(re.search(r"(\d+)%", _ejecutar(["pactl", "get-sink-volume", sink])).group(1))
    silenciado = "yes" in _ejecutar(["pactl", "get-sink-mute", sink]).lower()
    return porcentaje, silenciado

def controlar_volumen(accion: str, nivel: int = 0) -> str:
    """Controla el volumen del sistema operativo.
    accion: 'subir', 'bajar', 'establecer' (usa nivel 0-100), 'silenciar', 'activar_sonido' o 'consultar'.
    nivel: porcentaje de volumen 0-100, solo para la acción 'establecer'."""
    accion = accion.lower().strip()
    if accion not in ("subir", "bajar", "establecer", "silenciar", "activar_sonido", "consultar"):
        return f"Acción '{accion}' no soportada. Use: subir, bajar, establecer, silenciar, activar_sonido o consultar."
    if accion == "establecer" and not 0 <= int(nivel) <= 100:
        return "El nivel de volumen debe estar entre 0 y 100, Señor."
    sistema = platform.system()
    try:
        if sistema == "Windows":
            porcentaje, silenciado = _volumen_windows(accion, int(nivel))
        elif sistema == "Darwin":
            porcentaje, silenciado = _volumen_macos(accion, int(nivel))
        elif sistema == "Linux":
            porcentaje, silenciado = _volumen_linux(accion, int(nivel))
        else:
            return f"Sistema operativo '{sistema}' no soportado para el control de volumen."
    except ImportError:
        return "Falta la librería 'pycaw'. Ejecute: pip install pycaw comtypes"
    except (OSError, subprocess.SubprocessError, AttributeError) as e:
        return f"Fallo al acceder al subsistema de audio: {e}"
    estado = "silenciado" if silenciado else "activo"
    return f"Volumen del sistema al {porcentaje}% (audio {estado})."

# =====================================================================
# 3. INTERFAZ DE HARDWARE IOT (DOMÓTICA TUYA)
# =====================================================================
TUYA_DEVICE_ID = os.getenv("TUYA_DEVICE_ID", "TU_DEVICE_ID_AQUI")
TUYA_IP_ADDRESS = os.getenv("TUYA_IP_ADDRESS", "TU_IP_LOCAL_AQUI")
TUYA_LOCAL_KEY = os.getenv("TUYA_LOCAL_KEY", "TU_LOCAL_KEY_AQUI")
TUYA_VERSION = 3.3

def controlar_dispositivo_tuya(estado: str) -> str:
    """Enciende o apaga el hardware inteligente enlazado a la red local."""
    if "TU_DEVICE_ID" in TUYA_DEVICE_ID or TUYA_DEVICE_ID == "TU_DEVICE_ID_AQUI":
        return "Dispositivo Tuya Simulado: Complete las credenciales para operar hardware real."
    try:
        d = tinytuya.OutletDevice(TUYA_DEVICE_ID, TUYA_IP_ADDRESS, TUYA_LOCAL_KEY)
        d.set_version(TUYA_VERSION)
        if estado.lower() == "encender":
            d.turn_on()
            return "Matriz de energía activada para el dispositivo doméstico."
        elif estado.lower() == "apagar":
            d.turn_off()
            return "Flujo eléctrico interrumpido para el dispositivo doméstico."
        return f"Estado '{estado}' no soportado."
    except Exception as e:
        return f"Fallo en la interfaz de red IoT: {str(e)}"

# Pack de herramientas disponibles para la IA
herramientas_jarvis = [
    recordar_dato, buscar_en_memoria, diagnostico_sistema,
    leer_portapapeles, escribir_portapapeles, controlar_volumen,
    controlar_dispositivo_tuya
]

# =====================================================================
# 4. CONFIGURACIÓN DEL MOTOR DE INTELIGENCIA (GEMINI)
# =====================================================================
def inicializar_ia():
    if not os.getenv("GEMINI_API_KEY"):
        raise ValueError("Error crítico: La variable de entorno GEMINI_API_KEY no está configurada.")

    client = genai.Client()
    instrucciones_sistema = (
        "Eres J.A.R.V.I.S., el asistente de inteligencia artificial definitivo. Tu tono es formal, británico y directo. "
        "Dirígete al usuario como 'Señor'. Tienes acceso a herramientas avanzadas para leer la PC, interactuar con el portapapeles, "
        "controlar el volumen del sistema, monitorear el hardware de la máquina, consultar la base de datos local y accionar la "
        "domótica real. Usa las funciones adecuadas según las necesidades de cada instrucción."
    )
    return client.chats.create(
        model="gemini-2.5-flash",
        config=types.GenerateContentConfig(
            system_instruction=instrucciones_sistema,
            temperature=0.3,
            tools=herramientas_jarvis,
        )
    )

# =====================================================================
# 5. ENTORNO VISUAL Y CONTROL DE AUDIO (GUI)
# =====================================================================
engine = pyttsx3.init()
voices = engine.getProperty('voices')
if voices:
    engine.setProperty('voice', voices[0].id)
engine.setProperty('rate', 190)

def speak(text, gui_callback=None):
    if gui_callback:
        gui_callback(f"JARVIS: {text}")
    print(f"JARVIS: {text}")
    engine.say(text)
    engine.runAndWait()

def escuchar_comando():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source, duration=0.4)
        audio = r.listen(source)
    try:
        return r.recognize_google(audio, language='es-ES')
    except Exception:
        return None

class JarvisMasterOS(ctk.CTk):
    """Interfaz tipo asistente: orbe animado + conversación + entrada de texto."""
    BG = "#0a0f1e"
    PANEL = "#111a33"
    CIAN = "#00d2ff"
    AZUL = "#3a7bff"
    VIOLETA = "#8a5cff"
    TEXTO = "#e6f1ff"
    TENUE = "#7f93b8"
    ESTADOS = {
        "idle": ("Diga \"Jarvis\"...", "#3a7bff"),
        "listening": ("Escuchando...", "#00d2ff"),
        "thinking": ("Pensando...", "#8a5cff"),
        "speaking": ("Hablando...", "#00e5a8"),
    }

    def __init__(self):
        super().__init__()
        self.title("J.A.R.V.I.S.")
        self.geometry("460x720")
        self.minsize(380, 560)
        self.configure(fg_color=self.BG)
        ctk.set_appearance_mode("dark")

        self.running = True
        self.estado = "idle"
        self.fase = 0.0
        self.nivel = 0.0  # suavizado de la amplitud del orbe
        inicializar_base_datos()
        self.chat = inicializar_ia()

        ctk.CTkLabel(self, text="J.A.R.V.I.S.", font=("Segoe UI Light", 22), text_color=self.TEXTO).pack(pady=(18, 0))
        self.lbl_estado = ctk.CTkLabel(self, text="", font=("Segoe UI", 13), text_color=self.TENUE)
        self.lbl_estado.pack(pady=(2, 0))

        self.canvas = ctk.CTkCanvas(self, width=300, height=260, bg=self.BG, highlightthickness=0)
        self.canvas.pack(pady=(6, 0))

        self.console_output = ctk.CTkTextbox(
            self, fg_color=self.PANEL, text_color=self.TEXTO, font=("Segoe UI", 13),
            corner_radius=14, wrap="word", border_width=0)
        self.console_output.pack(fill="both", expand=True, padx=18, pady=(8, 8))
        self.console_output.tag_config("jarvis", foreground=self.CIAN)
        self.console_output.tag_config("usuario", foreground=self.TEXTO)
        self.console_output.tag_config("sistema", foreground=self.TENUE)
        self.console_output.configure(state="disabled")

        barra = ctk.CTkFrame(self, fg_color="transparent")
        barra.pack(fill="x", padx=18, pady=(0, 16))
        self.entrada = ctk.CTkEntry(
            barra, placeholder_text="Escriba una orden...", height=42, corner_radius=21,
            fg_color=self.PANEL, border_color=self.AZUL, text_color=self.TEXTO)
        self.entrada.pack(side="left", fill="x", expand=True)
        self.entrada.bind("<Return>", self.enviar_texto)
        ctk.CTkButton(barra, text="\u27a4", width=42, height=42, corner_radius=21,
                      fg_color=self.AZUL, hover_color=self.CIAN, command=self.enviar_texto
                      ).pack(side="left", padx=(8, 0))

        self.log_message("Sistemas listos. Diga \"Jarvis\" o escriba una orden.", "sistema")
        self.fijar_estado("idle")
        self.animar()

        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        threading.Thread(target=self.bucle_principal, daemon=True).start()

    # ---- estado y animación (siempre desde el hilo de la interfaz) ----
    def fijar_estado(self, estado):
        self.estado = estado
        texto, _ = self.ESTADOS[estado]
        self.after(0, lambda: self.lbl_estado.configure(text=texto))

    @staticmethod
    def _mezclar(c1, c2, t):
        a = [int(c1[k:k + 2], 16) for k in (1, 3, 5)]
        b = [int(c2[k:k + 2], 16) for k in (1, 3, 5)]
        return "#%02x%02x%02x" % tuple(int(x + (y - x) * t) for x, y in zip(a, b))

    def animar(self):
        if not self.running:
            return
        c = self.canvas
        c.delete("all")
        cx, cy = 150, 130
        self.fase += 0.06
        objetivo = {"idle": 0.15, "listening": 0.55, "thinking": 0.35, "speaking": 0.9}[self.estado]
        self.nivel += (objetivo - self.nivel) * 0.08
        color = self.ESTADOS[self.estado][1]
        respiro = (math.sin(self.fase) + 1) / 2

        # halo exterior (capas translucidas simuladas mezclando con el fondo)
        for k in range(8, 0, -1):
            r = 52 + k * 7 + self.nivel * 14 * respiro
            c.create_oval(cx - r, cy - r, cx + r, cy + r, outline="",
                          fill=self._mezclar(self.BG, color, 0.05 + 0.03 * (9 - k) * (0.5 + self.nivel)))
        # ondas al escuchar / hablar
        if self.estado in ("listening", "speaking"):
            for k in range(3):
                t = (self.fase * 0.5 + k / 3) % 1
                r = 55 + t * 60
                c.create_oval(cx - r, cy - r, cx + r, cy + r, outline=self._mezclar(self.BG, color, 1 - t), width=2)
        # anillo giratorio al pensar
        if self.estado == "thinking":
            c.create_arc(cx - 66, cy - 66, cx + 66, cy + 66, start=-self.fase * 160, extent=110,
                         style="arc", outline=self.VIOLETA, width=4)
            c.create_arc(cx - 66, cy - 66, cx + 66, cy + 66, start=-self.fase * 160 + 180, extent=60,
                         style="arc", outline=self.CIAN, width=4)
        # nucleo
        r = 44 + self.nivel * 8 * respiro
        c.create_oval(cx - r, cy - r, cx + r, cy + r, fill=self._mezclar(self.BG, color, 0.55), outline=color, width=2)
        r2 = r * 0.55
        c.create_oval(cx - r2, cy - r2, cx + r2, cy + r2, fill=self._mezclar(color, "#ffffff", 0.55), outline="")
        self.after(33, self.animar)

    # ---- conversación ----
    def log_message(self, message, etiqueta="sistema"):
        def escribir():
            self.console_output.configure(state="normal")
            hora = datetime.datetime.now().strftime("%H:%M")
            self.console_output.insert("end", f"{hora}  {message}\n\n", etiqueta)
            self.console_output.see("end")
            self.console_output.configure(state="disabled")
        self.after(0, escribir)

    def _log_jarvis(self, message):
        self.log_message(message.replace("JARVIS: ", "", 1), "jarvis")

    def on_closing(self):
        self.running = False
        self.destroy()

    def procesar_orden(self, orden):
        self.log_message(orden, "usuario")
        if any(x in orden.lower() for x in ["desconectar", "apagar", "salir"]):
            speak("Desactivando núcleos lógicos. Hasta pronto, Señor.", self._log_jarvis)
            self.after(0, self.on_closing)
            return False
        self.fijar_estado("thinking")
        try:
            response = self.chat.send_message(orden)
            self.fijar_estado("speaking")
            speak(response.text, self._log_jarvis)
        except Exception as e:
            self.log_message(f"Fallo del núcleo: {e}", "sistema")
            self.fijar_estado("speaking")
            speak("Disculpe Señor, mi canal de procesamiento ha devuelto un error.", self._log_jarvis)
        self.fijar_estado("idle")
        return True

    def enviar_texto(self, _evento=None):
        orden = self.entrada.get().strip()
        if not orden:
            return
        self.entrada.delete(0, "end")
        threading.Thread(target=self.procesar_orden, args=(orden,), daemon=True).start()

    def bucle_principal(self):
        time.sleep(1)
        self.fijar_estado("speaking")
        speak("Sistemas centrales acoplados. Listo, Señor.", self._log_jarvis)
        while self.running:
            self.fijar_estado("idle")
            palabra = escuchar_comando()
            if palabra and "jarvis" in palabra.lower():
                self.fijar_estado("speaking")
                speak("A su total disposición, Señor.", self._log_jarvis)
                self.fijar_estado("listening")
                orden = escuchar_comando()
                if orden and not self.procesar_orden(orden):
                    break

if __name__ == "__main__":
    app = JarvisMasterOS()
    app.mainloop()
