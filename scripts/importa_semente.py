#!/usr/bin/env python3
"""Importa checagens antigas a partir de uma lista de URLs (semente_urls.txt).

Para cada URL lê o título e a data de publicação nas meta tags da página e grava
em site/checagens_semente.json. O robô (fetch_checagens.py) junta isso ao que vem dos feeds.
"""
import json, re, sys, html, urllib.request
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from fetch_checagens import veredito, baixa

AQUI = Path(__file__).parent
FONTES = {"aosfatos.org": "Aos Fatos", "lupa.news": "Agência Lupa", "cnnbrasil.com.br": "CNN Brasil"}

def meta(pg, *props):
    for p in props:
        m = re.search(r'<meta[^>]+(?:property|name)=["\']%s["\'][^>]+content=["\']([^"\']+)["\']' % re.escape(p), pg) \
            or re.search(r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+(?:property|name)=["\']%s["\']' % re.escape(p), pg)
        if m: return html.unescape(m.group(1)).strip()
    return ""

def main():
    saida, falhas = [], []
    for url in [l.strip() for l in (AQUI / "semente_urls.txt").read_text().splitlines() if l.strip() and not l.startswith("#")]:
        try:
            pg = baixa(url).decode("utf8", "ignore")
        except Exception as e:
            falhas.append((url, str(e))); continue
        titulo = meta(pg, "og:title", "twitter:title") or ""
        titulo = re.sub(r"\s*[|\-–]\s*(Aos Fatos|CNN Brasil|Lupa).*$", "", titulo).strip()
        data = (meta(pg, "article:published_time", "datePublished") or "")[:10]
        if not re.match(r"\d{4}-\d{2}-\d{2}$", data):
            m = re.search(r'"datePublished"\s*:\s*"(\d{4}-\d{2}-\d{2})', pg)
            data = m.group(1) if m else ""
        fonte = next((v for k, v in FONTES.items() if k in url), "")
        if not titulo or not data:
            falhas.append((url, "sem título ou data")); continue
        saida.append({"titulo": titulo, "link": url, "fonte": fonte, "data": data, "veredito": veredito(titulo), "temas": []})
    (AQUI.parent / "site" / "checagens_semente.json").write_text(json.dumps(saida, ensure_ascii=False, indent=1), encoding="utf8")
    print(len(saida), "importadas;", len(falhas), "falhas")
    for u, e in falhas: print(" -", u, e)

if __name__ == "__main__":
    main()
