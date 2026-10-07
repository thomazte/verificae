#!/usr/bin/env python3
"""Vigia: procura notícias novas sobre Flávio Bolsonaro nos veículos aceitos e
monta vigia/relatorio.md para ser aberto como Issue no GitHub.

NÃO publica nada e NÃO altera o site. Serve para avisar uma pessoa de que algo novo
saiu e de quais cartões do dossiê talvez precisem de revisão.
"""
import json, re, sys
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
import xml.etree.ElementTree as ET
sys.path.insert(0, str(Path(__file__).parent))
from fetch_checagens import baixa

RAIZ = Path(__file__).resolve().parent.parent
ESTADO = RAIZ / "vigia" / "vistos.json"
RELATORIO = RAIZ / "vigia" / "relatorio.md"
JANELA_DIAS = 3

FEEDS = [
    ("G1", "https://g1.globo.com/rss/g1/politica/"),
    ("Folha", "https://feeds.folha.uol.com.br/poder/rss091.xml"),
    ("Poder360", "https://www.poder360.com.br/feed/"),
    ("Metrópoles", "https://www.metropoles.com/feed"),
]

# "Flávio" mas não o ministro Flávio Dino.
NOME = re.compile(r"Fl[áa]vio(?!\s+Dino)", re.I)
TEMA = re.compile(r"\b(PF|STF|TSE|PGR|MP|PL)\b|Mendon[çc]a|Moraes|Vorcaro|Master|Dark Horse|investig|inqu[ée]rito|den[úu]ncia|indici|opera[çc][ãa]o|arquiv|emenda|Coaf|Abin|rachadinha|fraude|multa|condena|pris[ãa]o|dela[çc][ãa]o|nota[s]? fiscal|patrim[ôo]nio|Constitui[çc][ãa]o|anistia|urna|Smartmatic", re.I)

# Palavras que indicam qual cartão do dossiê pode precisar de revisão.
CARTOES = [
    ("dark-horse", r"Dark Horse|Vorcaro|Master"),
    ("notas-fiscais", r"nota[s]? fiscal|Copenhagen|Cont[áa]bil Correa"),
    ("emenda-peixe", r"emenda|Peixe|Marielle|Br[aã]z[aã]o"),
    ("rachadinha", r"rachadinha|Queiroz|Kopenhagen"),
    ("abin", r"Abin|Ramagem"),
    ("urnas", r"urna|Smartmatic"),
    ("redemocratizar", r"Constitui[çc][ãa]o|redemocratiz"),
    ("anistia", r"anistia|8 de janeiro|8/1"),
    ("nobrega", r"N[óo]brega|mil[íi]cia"),
]

def cartoes_afetados(texto):
    return [c for c, rx in CARTOES if re.search(rx, texto, re.I)]

def le(fonte, url, desde):
    root = ET.fromstring(baixa(url))
    out = []
    for it in root.findall(".//item"):
        t = (it.findtext("title") or "").strip()
        l = (it.findtext("link") or "").strip()
        l = re.sub(r"^https://redir\.folha\.com\.br/redir/online/[^*]*\*", "", l)  # tira o redirecionador da Folha
        if not (t and l and NOME.search(t) and TEMA.search(t)):
            continue
        try:
            d = parsedate_to_datetime(it.findtext("pubDate"))
            d = d.replace(tzinfo=timezone.utc) if d.tzinfo is None else d.astimezone(timezone.utc)
        except Exception:
            continue
        if d >= desde:
            out.append({"fonte": fonte, "titulo": t, "link": l, "data": d.strftime("%d/%m/%Y %H:%M")})
    return out

def main():
    ESTADO.parent.mkdir(exist_ok=True)  # a pasta não existe num checkout novo
    vistos = set(json.loads(ESTADO.read_text(encoding="utf8"))) if ESTADO.exists() else set()
    desde = datetime.now(timezone.utc) - timedelta(days=JANELA_DIAS)
    novos = []
    for fonte, url in FEEDS:
        try:
            novos += [i for i in le(fonte, url, desde) if i["link"] not in vistos]
        except Exception as e:
            print(f"aviso: {fonte} falhou: {e}", file=sys.stderr)
    # tira duplicatas de link
    unicos = {i["link"]: i for i in novos}
    novos = sorted(unicos.values(), key=lambda i: i["data"][6:10] + i["data"][3:5] + i["data"][:2] + i["data"][11:], reverse=True)

    if RELATORIO.exists():
        RELATORIO.unlink()
    if novos:
        linhas = ["Notícias novas sobre Flávio Bolsonaro nos veículos aceitos. **Nada foi publicado.** "
                  "Leia, e se algum fato mudar (status de investigação, decisão, resposta da defesa), "
                  "atualize o cartão indicado em `site/index.html`.", ""]
        for i in novos:
            c = cartoes_afetados(i["titulo"])
            dica = f" (cartão: {', '.join(c)})" if c else ""
            linhas.append(f"- [ ] [{i['titulo']}]({i['link']}), {i['fonte']}, {i['data']}{dica}")
        linhas += ["", "Marque os itens já revisados e feche esta issue."]
        RELATORIO.write_text("\n".join(linhas) + "\n", encoding="utf8")
    vistos |= {i["link"] for i in novos}
    ESTADO.write_text(json.dumps(sorted(vistos)[-3000:], ensure_ascii=False, indent=0), encoding="utf8")
    print(f"{len(novos)} notícias novas")

if __name__ == "__main__":
    main()
