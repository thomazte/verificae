#!/usr/bin/env python3
"""Lê os feeds RSS das agências de checagem e grava site/checagens.json.

Só guarda título, link, data, fonte e categorias de cada checagem. O veredito
vem do próprio título publicado pela agência; sem veredito claro, fica "checagem".
Itens antigos são mantidos (os feeds só trazem os últimos 10 a 20).
"""
import json, re, sys, urllib.request, xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

FEEDS = [
    ("Agência Lupa", "https://lupa.news/feed/"),
    ("Aos Fatos", "https://www.aosfatos.org/noticias/feed/"),
    ("G1 Fato ou Fake", "https://g1.globo.com/rss/g1/fato-ou-fake/"),
]
OUT = Path(__file__).resolve().parent.parent / "site" / "checagens.json"
MAX_ITEMS = 600

# Só entram itens que são checagens de fato (cada agência rotula de um jeito).
FALSO = re.compile(r"\b[ée] falso\b|\bfalsos?\b|\bfalsas?\b|\bnão é verdade\b|\bnão procede\b|\bnão (noticiou|disse|anunciou|extinguiu|aprovou)\b", re.I)
ENGANOSO = re.compile(r"enganos|engana\b|enganam|desinforma|descontextualiz|distorc|exagera", re.I)
VERDADE = re.compile(r"\b[ée] verdade\b|\b[ée] verdadeir", re.I)
CHECA_TITULO = re.compile(r"não (é|há|indica|houve|existe|foi)|sem (provas|evidência)|desmente|é falso", re.I)
def veredito(titulo):
    # G1 Fato ou Fake marca o veredito no título: "É #FAKE ..." / "É #FATO ..."
    if re.search(r"#FAKE\b", titulo, re.I): return "falso"
    if re.search(r"#FATO\b", titulo, re.I): return "verdadeiro"
    if FALSO.search(titulo): return "falso"
    if ENGANOSO.search(titulo): return "enganoso"
    if VERDADE.search(titulo): return "verdadeiro"
    return "checagem"

def baixa(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Accept-Encoding": "identity"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()

def le_feed(fonte, url):
    root = ET.fromstring(baixa(url))
    saida = []
    for it in root.findall(".//item"):
        titulo = (it.findtext("title") or "").strip()
        link = (it.findtext("link") or "").strip()
        cats = [c.text.strip() for c in it.findall("category") if c.text]
        if not titulo or not link:
            continue
        # Lupa mistura opinião e reportagem: exige a categoria de verificação.
        if fonte == "Agência Lupa" and "Verificação" not in cats:
            continue
        # Aos Fatos: a categoria nem sempre vem no feed; sem ela, vale o título.
        if fonte == "Aos Fatos" and "Checagem" not in cats and veredito(titulo) == "checagem" \
                and not CHECA_TITULO.search(titulo):
            continue
        try:
            data = parsedate_to_datetime(it.findtext("pubDate"))
            data = data.replace(tzinfo=timezone.utc) if data.tzinfo is None else data.astimezone(timezone.utc)
        except Exception:
            continue
        saida.append({
            "titulo": titulo, "link": link, "fonte": fonte,
            "data": data.strftime("%Y-%m-%d"),
            "veredito": veredito(titulo),
            "temas": [c for c in cats if c not in ("Checagem", "Verificação", "Jornalismo", "Uncategorized")][:4],
        })
    return saida

def main():
    antigos = {}
    if OUT.exists():
        for i in json.loads(OUT.read_text(encoding="utf8")).get("itens", []):
            antigos[i["link"]] = i
    semente = OUT.parent / "checagens_semente.json"
    if semente.exists():
        for i in json.loads(semente.read_text(encoding="utf8")):
            i["veredito"] = veredito(i["titulo"])
            antigos.setdefault(i["link"], i)
    for fonte, url in FEEDS:
        try:
            for i in le_feed(fonte, url):
                antigos[i["link"]] = i
        except Exception as e:  # um feed fora do ar não derruba os outros
            print(f"aviso: {fonte} falhou: {e}", file=sys.stderr)
    itens = sorted(antigos.values(), key=lambda i: i["data"], reverse=True)[:MAX_ITEMS]
    dados = json.dumps({"atualizado": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"), "itens": itens}, ensure_ascii=False, indent=1)
    OUT.write_text(dados, encoding="utf8")
    # Embute os dados no próprio index.html: um arquivo só, funciona de qualquer lugar.
    html = OUT.parent / "index.html"
    if html.exists():
        txt = html.read_text(encoding="utf8")
        txt = re.sub(r"/\*DADOS\*/.*?/\*FIM\*/", lambda m: "/*DADOS*/window.CHECAGENS_DATA = " + dados.replace("</", "<\\/") + ";/*FIM*/", txt, count=1, flags=re.S)
        html.write_text(txt, encoding="utf8")
    print(f"{len(itens)} checagens gravadas em {OUT}")

if __name__ == "__main__":
    main()
