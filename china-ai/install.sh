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

# Elige modelos segun RAM (GB) o 'PERFIL=potente|medio|ligero ./install.sh'
RAM=$( (awk '/MemTotal/{print int($2/1048576)}' /proc/meminfo 2>/dev/null) || (sysctl -n hw.memsize 2>/dev/null | awk '{print int($1/1073741824)}') || echo 8)
PERFIL=${PERFIL:-$([ "$RAM" -ge 48 ] && echo potente || ([ "$RAM" -ge 12 ] && echo medio || echo ligero))}
case "$PERFIL" in
  potente) MODELOS="qwen3:32b deepseek-r1:32b qwen2.5-coder:32b" ;;
  medio)   MODELOS="qwen3:8b deepseek-r1:8b qwen2.5-coder:7b" ;;
  *)       MODELOS="qwen3:4b deepseek-r1:1.5b qwen2.5-coder:3b" ;;
esac
echo ">> RAM=${RAM}GB perfil=$PERFIL modelos: $MODELOS"
for m in $MODELOS; do
  echo ">> ollama pull $m"; ollama pull "$m"
done

echo ">> listo. Pruebe:  python3 china-ai/cn_ai.py list"
