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
