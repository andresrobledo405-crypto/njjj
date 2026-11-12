# china-ai — IA china unificada, sin suscripciones

Un solo cliente (`cn_ai.py`) para modelos abiertos chinos: Qwen, DeepSeek, Kimi, GLM, MiniMax.
Dos vias, usables a la vez (el cliente usa la primera disponible; fuerce con `-p`).

## 1) Local en su PC (gratis, privado, sin internet)
```bash
bash china-ai/install.sh        # Linux/macOS; en Windows use WSL o https://ollama.com/download
```
Elige modelos por RAM: <12 GB ligero (4B), 12-47 GB medio (8B), 48 GB+ potente (32B).
Fuerce con `PERFIL=potente bash china-ai/install.sh`. Con GPU NVIDIA/Apple Silicon va mucho mas rapido.

## 2) API (sin suscripcion, pago por uso, muy barata)
1. `cp china-ai/.env.example china-ai/.env`
2. Cree una clave en DeepSeek (platform.deepseek.com) y/o Qwen (bailian.console.alibabacloud.com).
3. Peguela en `.env`. Nunca se sube a git.

## Uso
```bash
python3 china-ai/cn_ai.py list
python3 china-ai/cn_ai.py ask "explica la fotosintesis"
python3 china-ai/cn_ai.py ask -p deepseek -r "resuelve este problema..."
python3 china-ai/cn_ai.py chat -p local
```

## Windows: guía paso a paso (instalar IA local + limpiar + desinstalar)
Abra **PowerShell como administrador** (clic derecho en Inicio → "Terminal (administrador)").

1. Permitir scripts solo en esta ventana: `Set-ExecutionPolicy -Scope Process Bypass -Force`
2. Instalar Ollama, descargar el modelo (qwen3:8b si hay 12 GB de RAM o más; si no, qwen3:4b), limpiar y recibir consejos de la IA: `.\china-ai\limpiar-pc.ps1`
3. Desinstalar programas innecesarios (usted marca cuáles; la IA solo aconseja): `.\china-ai\desinstalar-programas.ps1`

Notas: necesita `winget` (Windows 10/11 recientes). El modelo ocupa ~5 GB (8B) o ~2,5 GB (4B). Ningún script borra
documentos ni programas sin su confirmación. Las versiones legibles son los `.ps1` de esta carpeta.

### Atajo: todo en uno
Descargue la carpeta `china-ai/` y haga **doble clic en `EJECUTAR-TODO.bat`**: pide administrador, instala Ollama y el modelo, limpia, analiza con IA y le deja elegir qué desinstalar (siempre con su confirmación).
