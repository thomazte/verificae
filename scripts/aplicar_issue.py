#!/usr/bin/env python3
"""Aplica ao dossiê uma issue aprovada (formulário .github/ISSUE_TEMPLATE/cartao.yml).

Lê o evento do GitHub (GITHUB_EVENT_PATH, ou --evento arquivo.json), valida tudo,
altera site/dossie.json, embute no index.html e atualiza a data do topo.
O conteúdo da issue é tratado só como DADO: nada é executado e links são conferidos.
Saída: escreve a mensagem em $RESULTADO (padrão resultado.md); código 0 = aplicado, 1 = recusado.
"""
import json, os, re, sys, unicodedata
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).parent))
import dossie

GRUPOS = {"Casos e investigações": "casos", "Falas e posições": "falas"}
STATUS = {
    "Investigado": "investigado",
    "Arquivado": "arquivado",
    "Reportagem, sem investigação confirmada": "reportagem",
    "Fala": "fala",
    "Posição pública": "posicao",
    "Decisão favorável a ele": "favoravel",
}
ACOES = {"Novo cartão": "novo", "Atualizar cartão existente": "atualizar", "Remover cartão": "remover"}

# Veículos e agências aceitos (domínio ou sufixo) e documentos oficiais.
DOMINIOS = [
    "g1.globo.com", "oglobo.globo.com", "folha.uol.com.br", "uol.com.br", "cnnbrasil.com.br",
    "poder360.com.br", "agenciabrasil.ebc.com.br", "metropoles.com", "conjur.com.br",
    "estadao.com.br", "lupa.news", "aosfatos.org",
    ".jus.br", ".gov.br", ".leg.br", ".mp.br",
]
LIMITES = {"titulo": 160, "resumo": 1800, "situacao": 800, "defesa": 800, "data": 80}
VAZIO = {"", "_No response_", "None"}

def parse_corpo(corpo):
    campos = {}
    for bloco in re.split(r"(?m)^### ", corpo):
        if "\n" not in bloco:
            continue
        titulo, _, valor = bloco.partition("\n")
        campos[titulo.strip()] = valor.strip()
    return campos

def limpa(v):
    v = (v or "").strip()
    return "" if v in VAZIO else re.sub(r"\s+", " ", v)

def slug(t):
    t = unicodedata.normalize("NFD", t).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-")[:40].strip("-")

def dominio_ok(url):
    p = urlparse(url)
    if p.scheme != "https" or not p.hostname:
        return False
    h = p.hostname.lower()
    for d in DOMINIOS:
        if d.startswith("."):          # sufixo oficial: .gov.br, .jus.br...
            if h.endswith(d):
                return True
        elif h == d or h.endswith("." + d):
            return True
    return False

def le_fontes(texto, erros):
    out = []
    for linha in [l.strip() for l in texto.splitlines() if l.strip() and l.strip() not in VAZIO]:
        if "|" not in linha:
            erros.append(f"Fonte sem o formato `Nome | https://link`: `{linha[:80]}`"); continue
        nome, url = [x.strip() for x in linha.split("|", 1)]
        if not nome or len(nome) > 80:
            erros.append(f"Nome de fonte vazio ou longo demais: `{linha[:80]}`"); continue
        if len(url) > 500 or not dominio_ok(url):
            erros.append(f"Link fora da lista de fontes aceitas (ou sem https): `{url[:100]}`"); continue
        out.append([nome, url])
    return out

def main():
    caminho = os.environ.get("GITHUB_EVENT_PATH")
    if "--evento" in sys.argv:
        caminho = sys.argv[sys.argv.index("--evento") + 1]
    evento = json.load(open(caminho, encoding="utf8"))
    numero = evento["issue"]["number"]
    campos = parse_corpo(evento["issue"].get("body") or "")
    get = lambda nome: limpa(campos.get(nome, ""))
    erros = []

    acao = ACOES.get(get("Ação"))
    if not acao:
        erros.append("Ação inválida.")
    for nome, v in [("Título", get("Título")), ("Resumo", get("Resumo")), ("Situação atual", get("Situação atual")),
                    ("O que diz a defesa", get("O que diz a defesa")), ("Data ou período", get("Data ou período"))]:
        if "<" in v or ">" in v:
            erros.append(f"O campo {nome} contém `<` ou `>`, que não são aceitos.")
    itens = dossie.carrega()
    por_id = {i["id"]: i for i in itens}

    novo = {
        "grupo": GRUPOS.get(get("Grupo")),
        "status": STATUS.get(get("Status")),
        "data": get("Data ou período"),
        "titulo": get("Título"),
        "resumo": get("Resumo"),
        "situacao": get("Situação atual"),
        "defesa": get("O que diz a defesa"),
    }
    for chave, lim in LIMITES.items():
        if len(novo[chave]) > lim:
            erros.append(f"O campo `{chave}` passa de {lim} caracteres.")
    fontes = le_fontes(campos.get("Fontes (uma por linha: Nome | https://link)", ""), erros)
    id_ = get("ID do cartão").lower()
    if id_ and not re.fullmatch(r"[a-z0-9-]{3,40}", id_):
        erros.append("ID inválido: use de 3 a 40 letras minúsculas, números e hífens.")

    resumo_msg = ""
    if not erros:
        if acao == "novo":
            falta = [k for k in ("grupo", "status", "data", "titulo", "resumo", "situacao", "defesa") if not novo[k]]
            if falta:
                erros.append("Faltam campos obrigatórios em cartão novo: " + ", ".join(falta) + ".")
            if not fontes:
                erros.append("Cartão novo precisa de pelo menos uma fonte.")
            id_ = id_ or slug(novo["titulo"])
            if not id_ or len(id_) < 3:
                erros.append("Não consegui criar um ID a partir do título; informe o ID.")
            elif id_ in por_id:
                erros.append(f"Já existe um cartão com o ID `{id_}`. Use a ação Atualizar.")
            if not erros:
                carta = dict(id=id_, **novo, fontes=fontes)
                pos = next((n for n, i in enumerate(itens) if i["grupo"] == carta["grupo"]), len(itens))
                itens.insert(pos, carta)
                resumo_msg = f"Cartão **{id_}** criado."
        elif acao == "atualizar":
            if id_ not in por_id:
                erros.append(f"Não existe cartão com o ID `{id_}`. IDs: " + ", ".join(sorted(por_id)) + ".")
            else:
                alvo = por_id[id_]
                mudou = []
                for k, v in novo.items():
                    if v:
                        if k == "data" or alvo.get(k) != v:
                            alvo[k] = v; mudou.append(k)
                novas = [f for f in fontes if f[1] not in {x[1] for x in alvo["fontes"]}]
                if novas:
                    alvo["fontes"] += novas; mudou.append(f"{len(novas)} fonte(s) nova(s)")
                if not mudou:
                    erros.append("Nada para atualizar: todos os campos vieram vazios ou iguais.")
                resumo_msg = f"Cartão **{id_}** atualizado: " + ", ".join(mudou) + "."
        elif acao == "remover":
            if id_ not in por_id:
                erros.append(f"Não existe cartão com o ID `{id_}`.")
            else:
                itens = [i for i in itens if i["id"] != id_]
                resumo_msg = f"Cartão **{id_}** removido."

    resultado = Path(os.environ.get("RESULTADO", "resultado.md"))
    if erros:
        resultado.write_text("Não apliquei esta issue. Corrija e ponha a etiqueta `aprovado` de novo:\n\n" +
                             "\n".join(f"- {e}" for e in erros) + "\n", encoding="utf8")
        print("RECUSADA"); return 1
    dossie.salva(itens)
    dossie.embute(itens)
    dossie.atualiza_data(datetime.now(ZoneInfo("America/Sao_Paulo")).strftime("%d/%m/%Y"))
    resultado.write_text(resumo_msg + "\n\nO site será publicado em 1 a 2 minutos. Issue fechada.\n", encoding="utf8")
    print("APLICADA:", resumo_msg); return 0

if __name__ == "__main__":
    sys.exit(main())
