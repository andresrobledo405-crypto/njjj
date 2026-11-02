#!/usr/bin/env python3
"""Cliente unificado para IA china (DeepSeek, Kimi, Qwen, GLM, MiniMax, local Ollama).

Solo libreria estandar. Lee claves de china-ai/.env o del entorno.

  python3 china-ai/cn_ai.py list
  python3 china-ai/cn_ai.py ask "hola"                      # elige el primer proveedor disponible
  python3 china-ai/cn_ai.py ask -p deepseek -r "problema"   # modo razonamiento
  python3 china-ai/cn_ai.py ask -p qwen -m codigo "escribe un quicksort"
  python3 china-ai/cn_ai.py chat -p kimi                    # conversacion interactiva
"""
import argparse, json, os, sys, urllib.request, urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))


def load_env():
    for path in (os.path.join(HERE, ".env"), os.path.join(HERE, "..", "video", ".env")):
        if os.path.exists(path):
            for line in open(path, encoding="utf-8"):
                line = line.split("#", 1)[0].strip()
                if "=" in line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip().strip('"\''))


def registry():
    return json.load(open(os.path.join(HERE, "models.json"), encoding="utf-8"))


def local_up(base):
    try:
        urllib.request.urlopen(base.replace("/v1", "/api/tags"), timeout=2)
        return True
    except Exception:
        return False


def available(name, p):
    if name == "local":
        return local_up(p["base_url"])
    return bool(os.environ.get(p["key_env"] or ""))


def pick_model(p, mode, explicit):
    if explicit:
        return p.get(explicit, explicit)  # alias (codigo/vision/razonamiento) o nombre literal
    return p.get(mode, p["default"]) if mode else p["default"]


def chat(provider, p, model, messages, stream=True):
    headers = {"Content-Type": "application/json"}
    if p["key_env"]:
        headers["Authorization"] = "Bearer " + os.environ[p["key_env"]]
    body = json.dumps({"model": model, "messages": messages, "stream": stream}).encode()
    req = urllib.request.Request(p["base_url"] + "/chat/completions", body, headers)
    out = []
    try:
        with urllib.request.urlopen(req, timeout=600) as r:
            if not stream:
                text = json.load(r)["choices"][0]["message"]["content"]
                print(text)
                return text
            for raw in r:
                raw = raw.decode().strip()
                if not raw.startswith("data:") or raw.endswith("[DONE]"):
                    continue
                delta = json.loads(raw[5:])["choices"][0].get("delta", {})
                piece = delta.get("content") or ""
                if piece:
                    out.append(piece)
                    sys.stdout.write(piece)
                    sys.stdout.flush()
        print()
        return "".join(out)
    except urllib.error.HTTPError as e:
        sys.exit(f"[{provider}] HTTP {e.code}: {e.read().decode(errors='replace')[:300]}")
    except urllib.error.URLError as e:
        sys.exit(f"[{provider}] sin conexion: {e.reason}")


def resolve(args, reg):
    names = [args.provider] if args.provider else reg["orden_auto"]
    for n in names:
        p = reg["providers"].get(n)
        if p and available(n, p):
            mode = "razonamiento" if getattr(args, "reason", False) else None
            return n, p, pick_model(p, mode, args.model)
    sys.exit("Ningun proveedor disponible. Copie china-ai/.env.example a china-ai/.env "
             "y ponga una clave, o ejecute china-ai/install.sh para el modelo local.")


def main():
    load_env()
    reg = registry()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list")
    for c in ("ask", "chat"):
        s = sub.add_parser(c)
        s.add_argument("-p", "--provider", choices=list(reg["providers"]))
        s.add_argument("-m", "--model", help="nombre exacto o alias: codigo, vision, razonamiento")
        s.add_argument("-r", "--reason", action="store_true", help="usar modelo de razonamiento")
        s.add_argument("-s", "--system", default="Eres un asistente util. Responde en español salvo que se pida otro idioma.")
        if c == "ask":
            s.add_argument("prompt", nargs="+")
    a = ap.parse_args()

    if a.cmd == "list":
        for n, p in reg["providers"].items():
            ok = "LISTO " if available(n, p) else "falta "
            print(f"{ok} {n:9} {p['default']:24} {p['fuerte_en']}")
        return

    name, p, model = resolve(a, reg)
    print(f"[{name} · {model}]", file=sys.stderr)
    msgs = [{"role": "system", "content": a.system}]
    if a.cmd == "ask":
        msgs.append({"role": "user", "content": " ".join(a.prompt)})
        chat(name, p, model, msgs)
        return
    print("Escriba 'salir' para terminar.", file=sys.stderr)
    while True:
        try:
            q = input("tú> ").strip()
        except EOFError:
            break
        if q.lower() in ("salir", "exit", "quit"):
            break
        if q:
            msgs.append({"role": "user", "content": q})
            msgs.append({"role": "assistant", "content": chat(name, p, model, msgs)})


if __name__ == "__main__":
    main()
