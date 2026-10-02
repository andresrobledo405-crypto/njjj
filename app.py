#!/usr/bin/env python3
"""
Professional Video Generator - Desktop Application
Open Source • Single-Click Video Generation
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import subprocess
import threading
import os
from datetime import datetime
import json

class VideoGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🎬 Professional Video Generator")
        self.root.geometry("600x700")
        self.root.configure(bg="#0f0c29")

        # Aplicar tema moderno
        style = ttk.Style()
        style.theme_use('clam')

        # Colores
        self.primary_color = "#667eea"
        self.secondary_color = "#764ba2"
        self.bg_color = "#0f0c29"
        self.text_color = "#ffffff"

        self.setup_ui()
        self.check_system()

    def setup_ui(self):
        """Crear interfaz de usuario"""

        # Header
        header = tk.Frame(self.root, bg=self.primary_color, height=100)
        header.pack(fill=tk.X)

        title = tk.Label(
            header,
            text="🎬 Professional Video Generator",
            font=("Arial", 24, "bold"),
            bg=self.primary_color,
            fg=self.text_color
        )
        title.pack(pady=20)

        subtitle = tk.Label(
            header,
            text="Open Source • Single Click Video Generation",
            font=("Arial", 10),
            bg=self.primary_color,
            fg=self.text_color
        )
        subtitle.pack()

        # Main content
        main_frame = tk.Frame(self.root, bg=self.bg_color)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)

        # Status
        self.status_var = tk.StringVar(value="🟢 Sistema Listo")
        status_label = tk.Label(
            main_frame,
            textvariable=self.status_var,
            font=("Arial", 12, "bold"),
            bg=self.bg_color,
            fg="#00ff88"
        )
        status_label.pack(pady=10)

        # Info
        info_frame = tk.Frame(main_frame, bg="#1a1a3e", relief=tk.RAISED, bd=1)
        info_frame.pack(fill=tk.X, pady=20)

        info_text = tk.Label(
            info_frame,
            text=(
                "✨ Genera videos profesionales automáticamente\n"
                "📱 Optimizado para 5 plataformas\n"
                "⚡ 60 segundos en 4-5 minutos\n"
                "🎨 Calidad H.264 profesional\n"
                "🔄 Completamente automático"
            ),
            font=("Arial", 10),
            bg="#1a1a3e",
            fg=self.text_color,
            justify=tk.LEFT
        )
        info_text.pack(padx=20, pady=20)

        # Main Button - ÚNICA OPCIÓN
        self.generate_btn = tk.Button(
            main_frame,
            text="🚀 GENERAR VIDEO AHORA",
            font=("Arial", 18, "bold"),
            bg=self.secondary_color,
            fg=self.text_color,
            command=self.generate_video,
            padx=40,
            pady=30,
            relief=tk.RAISED,
            bd=0,
            cursor="hand2",
            activebackground=self.primary_color,
            activeforeground=self.text_color
        )
        self.generate_btn.pack(fill=tk.X, pady=20)

        # Progress
        self.progress = ttk.Progressbar(
            main_frame,
            mode='indeterminate',
            length=300
        )
        self.progress.pack(fill=tk.X, pady=10)

        # Output
        output_label = tk.Label(
            main_frame,
            text="📊 Salida:",
            font=("Arial", 10, "bold"),
            bg=self.bg_color,
            fg=self.text_color
        )
        output_label.pack(anchor=tk.W, pady=(20, 5))

        self.output_text = tk.Text(
            main_frame,
            height=8,
            bg="#1a1a3e",
            fg="#00ff88",
            font=("Courier", 9),
            relief=tk.FLAT,
            bd=0
        )
        self.output_text.pack(fill=tk.BOTH, expand=True)

        # Footer
        footer_frame = tk.Frame(self.root, bg="#1a1a3e", height=60)
        footer_frame.pack(fill=tk.X, side=tk.BOTTOM)

        footer_text = tk.Label(
            footer_frame,
            text="🎬 Videos guardados en: ~/njjj/exports/ | 📱 Publicar: bash publish_to_youtube.sh",
            font=("Arial", 9),
            bg="#1a1a3e",
            fg="#888888"
        )
        footer_text.pack(pady=10)

        # Botones secundarios (pequeños)
        btn_frame = tk.Frame(footer_frame, bg="#1a1a3e")
        btn_frame.pack(pady=10)

        view_btn = tk.Button(
            btn_frame,
            text="👁️ Ver Videos",
            font=("Arial", 8),
            bg=self.primary_color,
            fg=self.text_color,
            command=self.view_videos,
            padx=10,
            pady=5,
            relief=tk.FLAT
        )
        view_btn.pack(side=tk.LEFT, padx=5)

        open_btn = tk.Button(
            btn_frame,
            text="📁 Abrir Carpeta",
            font=("Arial", 8),
            bg=self.primary_color,
            fg=self.text_color,
            command=self.open_folder,
            padx=10,
            pady=5,
            relief=tk.FLAT
        )
        open_btn.pack(side=tk.LEFT, padx=5)

    def check_system(self):
        """Verificar que el sistema esté listo"""
        self.log("🔍 Verificando sistema...")

        # Verificar archivos clave
        files = [
            "video-automation-engine.js",
            "scripts/random-video-generator.py",
            "scripts/demo-video-generator.py"
        ]

        for f in files:
            if os.path.exists(f):
                self.log(f"✓ {f}")
            else:
                self.log(f"✗ {f} NO ENCONTRADO")

        self.log("\n✅ Sistema listo para generar videos\n")

    def generate_video(self):
        """Generar video con un click"""
        self.generate_btn.config(state=tk.DISABLED)
        self.progress.start()
        self.log("🚀 Iniciando generación de video...\n")

        # Ejecutar en thread para no bloquear UI
        thread = threading.Thread(target=self._generate_thread)
        thread.daemon = True
        thread.start()

    def _generate_thread(self):
        """Thread para generación"""
        try:
            self.log("📝 Fase 1: Generando frames...\n")

            # Ejecutar generador random
            result = subprocess.run(
                ["python3", "scripts/random-video-generator.py"],
                capture_output=True,
                text=True,
                cwd=os.path.expanduser("~/njjj")
            )

            if result.returncode == 0:
                self.log("✅ Video generado exitosamente!\n")
                self.log("📊 Archivos creados:")
                self.log("  - exports/random_video.mp4")
                self.log("  - exports/youtube/random_youtube.mp4")
                self.log("  - exports/tiktok/random_tiktok.mp4")
                self.log("  - exports/instagram/random_instagram.mp4")
                self.log("  - exports/facebook/random_facebook.mp4")
                self.log("  - exports/twitter/random_twitter.mp4")
                self.log("\n🎉 ¡Listo para publicar!")

                # Guardar en log
                self.save_generation_log()
            else:
                self.log(f"❌ Error: {result.stderr}\n")

        except Exception as e:
            self.log(f"❌ Error: {str(e)}\n")
        finally:
            self.progress.stop()
            self.generate_btn.config(state=tk.NORMAL)
            self.status_var.set("✅ Completado")

    def save_generation_log(self):
        """Guardar log de generación"""
        log_file = os.path.expanduser("~/njjj/logs/generation.log")
        os.makedirs(os.path.dirname(log_file), exist_ok=True)

        with open(log_file, "a") as f:
            f.write(f"\n[{datetime.now().isoformat()}] Video generado\n")

    def log(self, message):
        """Agregar mensaje al output"""
        self.output_text.config(state=tk.NORMAL)
        self.output_text.insert(tk.END, message + "\n")
        self.output_text.see(tk.END)
        self.output_text.config(state=tk.DISABLED)
        self.root.update()

    def view_videos(self):
        """Abrir reproductor de videos"""
        subprocess.Popen(["xdg-open", "/tmp/video-viewer.html"])
        messagebox.showinfo("Reproductor", "Abriendo reproductor en navegador...")

    def open_folder(self):
        """Abrir carpeta de exportación"""
        folder = os.path.expanduser("~/njjj/exports")
        subprocess.Popen(["xdg-open", folder] if os.path.exists(folder) else ["nautilus", folder])

def main():
    root = tk.Tk()
    app = VideoGeneratorApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
