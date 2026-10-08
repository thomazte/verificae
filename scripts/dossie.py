#!/usr/bin/env python3
"""Dossiê: os cartões ficam em site/dossie.json e são embutidos no index.html.

Uso:
  python3 scripts/dossie.py embutir     # copia site/dossie.json para dentro do index.html

Edite site/dossie.json (fonte da verdade) e rode "embutir"; ou use o fluxo de issues
(.github/workflows/aprovar.yml), que faz isso sozinho.
"""
import json, re, sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
JSON = RAIZ / "site" / "dossie.json"
HTML = RAIZ / "site" / "index.html"
MARCA = re.compile(r"/\*DOSSIE\*/.*?/\*FIMDOSSIE\*/", re.S)

def carrega():
    return json.loads(JSON.read_text(encoding="utf8"))

def salva(itens):
    JSON.write_text(json.dumps(itens, ensure_ascii=False, indent=1) + "\n", encoding="utf8")

def embute(itens):
    txt = HTML.read_text(encoding="utf8")
    dados = json.dumps(itens, ensure_ascii=False, indent=1).replace("</", "<\\/")
    novo, n = MARCA.subn(lambda m: "/*DOSSIE*/" + dados + "/*FIMDOSSIE*/", txt, count=1)
    if n != 1:
        raise SystemExit("marcadores /*DOSSIE*/ ... /*FIMDOSSIE*/ não encontrados no index.html")
    HTML.write_text(novo, encoding="utf8")

def atualiza_data(dd_mm_aaaa):
    txt = HTML.read_text(encoding="utf8")
    novo = re.sub(r"(atualizado em )\d{2}/\d{2}/\d{4}", lambda m: m.group(1) + dd_mm_aaaa, txt, count=1)
    HTML.write_text(novo, encoding="utf8")

if __name__ == "__main__":
    if sys.argv[1:] == ["embutir"]:
        embute(carrega()); print("dossiê embutido no index.html")
    else:
        print(__doc__)
