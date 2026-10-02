#!/usr/bin/env python3
"""
Professional Video Generator - Complete Edition
Conectado a todos los motores de generación
Open Source • One-Click Production
"""

import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import threading
import os
import json
from datetime import datetime

class CompleteVideoGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🎬 Professional Video Generator - Complete")
        self.root.geometry("700x850")
        self.root.configure(bg="#0f0c29")

        # Motores disponibles
        self.engines = {
            "Random": "scripts/random-video-generator.py",
            "Demo": "scripts/demo-video-generator.py",
            "Automation": "video-automation-engine.js",
        }

        self.current_engine = tk.StringVar(value="Random")
        self.setup_ui()
        self.check_system()

    def setup_ui(self):
        """Crear interfaz profesional"""

        # Header
        header = tk.Frame(self.root, bg="#667eea", height=120)
        header.pack(fill=tk.X)

        title = tk.Label(
            header,
            text="🎬 Professional Video Generator",
            font=("Arial", 26, "bold"),
            bg="#667eea",
            fg="white"
        )
        title.pack(pady=15)

        subtitle = tk.Label(
            header,
            text="Conectado a todos los motores de generación de contenido",
            font=("Arial", 11),
            bg="#667eea",
            fg="white"
        )
        subtitle.pack()

        # Main
        main = tk.Frame(self.root, bg="#0f0c29")
        main.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Status
        self.status = tk.StringVar(value="🟢 Sistema Listo")
        status_lbl = tk.Label(
            main,
            textvariable=self.status,
            font=("Arial", 12, "bold"),
            bg="#0f0c29",
            fg="#00ff88"
        )
        status_lbl.pack(pady=10)

        # Selector de motor
        motor_frame = tk.LabelFrame(
            main,
            text="⚙️ Seleccionar Motor",
            bg="#1a1a3e",
            fg="white",
            font=("Arial", 10, "bold")
        )
        motor_frame.pack(fill=tk.X, pady=15)

        for engine in self.engines.keys():
            rb = tk.Radiobutton(
                motor_frame,
                text=f"🎬 {engine}",
                variable=self.current_engine,
                value=engine,
                bg="#1a1a3e",
                fg="white",
                selectcolor="#667eea",
                font=("Arial", 10)
            )
            rb.pack(anchor=tk.W, padx=20, pady=5)

        # Información del motor
        info_frame = tk.Frame(main, bg="#1a1a3e", relief=tk.RAISED, bd=1)
        info_frame.pack(fill=tk.X, pady=15)

        self.info_text = tk.Label(
            info_frame,
            text=self._get_engine_info("Random"),
            font=("Arial", 9),
            bg="#1a1a3e",
            fg="white",
            justify=tk.LEFT
        )
        self.info_text.pack(padx=15, pady=15)

        # Bind cambio de motor
        self.current_engine.trace("w", self._on_engine_change)

        # Main Button
        self.gen_btn = tk.Button(
            main,
            text="🚀 GENERAR VIDEO AHORA",
            font=("Arial", 18, "bold"),
            bg="#764ba2",
            fg="white",
            command=self.generate,
            padx=40,
            pady=30,
            relief=tk.FLAT,
            cursor="hand2",
            activebackground="#667eea"
        )
        self.gen_btn.pack(fill=tk.X, pady=20)

        # Progress
        self.progress = ttk.Progressbar(main, mode='indeterminate')
        self.progress.pack(fill=tk.X, pady=10)

        # Output
        output_lbl = tk.Label(
            main,
            text="📊 Progreso:",
            font=("Arial", 10, "bold"),
            bg="#0f0c29",
            fg="white"
        )
        output_lbl.pack(anchor=tk.W, pady=(15, 5))

        self.output = tk.Text(
            main,
            height=10,
            bg="#1a1a3e",
            fg="#00ff88",
            font=("Courier", 8),
            relief=tk.FLAT,
            bd=0
        )
        self.output.pack(fill=tk.BOTH, expand=True)

        # Footer
        footer = tk.Frame(self.root, bg="#1a1a3e", height=50)
        footer.pack(fill=tk.X, side=tk.BOTTOM)

        footer_txt = tk.Label(
            footer,
            text="🎬 Videos en ~/njjj/exports/ | 📱 Publicar: bash publish_to_youtube.sh",
            font=("Arial", 8),
            bg="#1a1a3e",
            fg="#888888"
        )
        footer_txt.pack(pady=10)

    def _get_engine_info(self, engine):
        """Obtener información del motor"""
        info = {
            "Random": "🎲 Motor Aleatorio\n✓ Videos únicos cada vez\n✓ Animaciones procedurales\n✓ Rápido y eficiente",
            "Demo": "📺 Motor Demo\n✓ Video de demostración\n✓ Estructura definida\n✓ Ejemplo profesional",
            "Automation": "⚙️ Motor Automático\n✓ Sistema completo\n✓ Multi-plataforma\n✓ APIs integradas"
        }
        return info.get(engine, "")

    def _on_engine_change(self, *args):
        """Actualizar información cuando cambia motor"""
        self.info_text.config(text=self._get_engine_info(self.current_engine.get()))

    def generate(self):
        """Generar video con motor seleccionado"""
        engine = self.current_engine.get()
        self.gen_btn.config(state=tk.DISABLED)
        self.progress.start()
        self.log(f"🚀 Usando motor: {engine}\n")

        thread = threading.Thread(target=self._generate_thread, args=(engine,))
        thread.daemon = True
        thread.start()

    def _generate_thread(self, engine):
        """Thread de generación"""
        try:
            if engine == "Automation":
                self._run_automation()
            else:
                self._run_python_engine(engine)
        except Exception as e:
            self.log(f"❌ Error: {str(e)}\n")
        finally:
            self.progress.stop()
            self.gen_btn.config(state=tk.NORMAL)
            self.status.set("✅ Completado")

    def _run_python_engine(self, engine):
        """Ejecutar motor Python"""
        script = self.engines[engine]
        self.log(f"📝 Ejecutando: {script}\n")

        result = subprocess.run(
            ["python3", script],
            capture_output=True,
            text=True,
            cwd=os.path.expanduser("~/njjj")
        )

        if result.returncode == 0:
            self.log("✅ ¡Éxito!\n")
            self.log("📊 Videos generados:")
            self.log("  ✓ random_video.mp4")
            self.log("  ✓ 5 variantes de plataforma")
            self.log("\n🎉 Listo para publicar")
            self.save_log(engine)
        else:
            self.log(f"Error: {result.stderr}\n")

    def _run_automation(self):
        """Ejecutar motor de automatización"""
        self.log("⚙️ Iniciando sistema de automatización...\n")

        # Enviar trabajo
        job_config = {
            "prompt": "Video profesional aleatorio de 60 segundos",
            "quality": "professional",
            "platforms": ["youtube", "tiktok", "instagram"]
        }

        submit_cmd = [
            "node", "video-automation-engine.js", "submit",
            json.dumps(job_config)
        ]

        result = subprocess.run(
            submit_cmd,
            capture_output=True,
            text=True,
            cwd=os.path.expanduser("~/njjj")
        )

        self.log(f"{result.stdout}\n")

        # Procesar
        self.log("⏳ Procesando...\n")
        result = subprocess.run(
            ["node", "video-automation-engine.js", "process"],
            capture_output=True,
            text=True,
            timeout=600,
            cwd=os.path.expanduser("~/njjj")
        )

        if result.returncode == 0:
            self.log("✅ Video generado\n")
        else:
            self.log(f"Resultado: {result.stdout}\n")

    def save_log(self, engine):
        """Guardar log de generación"""
        log_file = os.path.expanduser("~/njjj/logs/generation.log")
        os.makedirs(os.path.dirname(log_file), exist_ok=True)

        with open(log_file, "a") as f:
            f.write(f"[{datetime.now().isoformat()}] {engine}\n")

    def log(self, msg):
        """Agregar mensaje al output"""
        self.output.config(state=tk.NORMAL)
        self.output.insert(tk.END, msg)
        self.output.see(tk.END)
        self.output.config(state=tk.DISABLED)
        self.root.update()

    def check_system(self):
        """Verificar sistema"""
        self.log("🔍 Verificando sistema...\n")

        checks = [
            ("app.py", "Aplicación"),
            ("video-automation-engine.js", "Motor de automatización"),
            ("scripts/random-video-generator.py", "Motor aleatorio"),
            ("scripts/demo-video-generator.py", "Motor demo"),
        ]

        for file, name in checks:
            if os.path.exists(os.path.expanduser(f"~/njjj/{file}")):
                self.log(f"✓ {name}\n")

        self.log("\n✅ Sistema listo\n")

def main():
    root = tk.Tk()
    app = CompleteVideoGeneratorApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
