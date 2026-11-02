#!/usr/bin/env bash
# Instala el modelo local (Ollama + Qwen/DeepSeek pequenos) y prepara .env.
# Ejecutelo usted: descarga e instala el binario oficial de Ollama (https://ollama.com/install.sh).
set -euo pipefail
cd "$(dirname "$0")"

[ -f .env ] || { cp .env.example .env; echo ">> creado china-ai/.env (ponga sus claves)"; }

command -v zstd >/dev/null || { echo ">> instalando zstd"; (sudo apt-get install -y zstd || apt-get install -y zstd); }

if ! command -v ollama >/dev/null; then
  echo ">> instalando Ollama (script oficial)"
  curl -fsSL https://ollama.com/install.sh | sh
fi

if ! curl -fs -m 2 http://localhost:11434/api/tags >/dev/null; then
  echo ">> iniciando ollama serve"
  nohup ollama serve >/tmp/ollama.log 2>&1 &
  for _ in $(seq 20); do curl -fs -m 1 http://localhost:11434/api/tags >/dev/null && break; sleep 1; done
fi

for m in $(python3 -c "import json;print(' '.join(json.load(open('models.json'))['local_pull']))"); do
  echo ">> ollama pull $m"; ollama pull "$m"
done

echo ">> listo. Pruebe:  python3 china-ai/cn_ai.py list"
