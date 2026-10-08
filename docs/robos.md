# Robôs e publicação

Há dois workflows em `.github/workflows/`.

## `site.yml`: atualizar e publicar

- Roda duas vezes por dia (06h e 18h de Brasília), a cada alteração em `site/` ou `scripts/`, e pelo botão "Run workflow".
- Executa `scripts/fetch_checagens.py`, que lê os feeds da Agência Lupa, do Aos Fatos e do G1 Fato ou Fake e grava as checagens novas no `index.html` e em `site/checagens.json`.
- Guarda o acumulado no repositório (os feeds só trazem os últimos itens). Esse commit é o que dispara a publicação no Netlify.

Importante: o robô **não verifica veracidade**. Ele repassa o veredito que a agência já publicou, com título e link originais.

### Publicar no Netlify (recomendado se você já usa)

1. No Netlify: Add new site, Import from Git, escolha este repositório.
2. Build command: vazio. Publish directory: `site` (o `netlify.toml` já diz isso).
3. A cada commit em `site/` (inclusive os do robô) o Netlify publica sozinho. Commits que não mexem em `site/` são ignorados.

Atenção ao limite do plano gratuito: confira no Netlify quantos deploys por mês ele permite, porque o robô gera até 2 por dia.

### Publicar no GitHub Pages (alternativa, sem limite)

1. Em Settings, Pages, escolha **Source: GitHub Actions**.
2. Em Settings, Secrets and variables, Actions, Variables, crie `USAR_PAGES` com o valor `true`.
3. Rode o workflow pela aba Actions.

## `vigia.yml`: avisar de notícia nova

- Roda três vezes por dia (08h, 14h e 20h de Brasília).
- Executa `scripts/vigia.py`, que procura notícias sobre Flávio no G1, na Folha, no Poder360 e no Metrópoles (feeds de política).
- Se há notícia nova com tema relevante (PF, STF, investigação, emendas etc.), abre uma **Issue** com a etiqueta `revisar`, listando os links e indicando qual cartão do dossiê pode precisar de revisão.
- **Não publica nem altera o site.** O dossiê só muda quando uma pessoa revisa e edita.
- Guarda o que já foi visto em `vigia/vistos.json`, para não repetir.
- Cada notícia da issue traz links **"atualizar `<cartão>`"** e **"novo cartão"**, que abrem o formulário já preenchido com a ação, o ID do cartão e a fonte (`Veículo | link`). Falta só escrever o resumo, a situação e a defesa e aprovar.
- Para testar com notícias já vistas: Actions, "Vigia de notícias", Run workflow, marcando **reprocessar**.
- Cria as etiquetas `cartao`, `aprovado` e `revisar` se ainda não existirem.

## `aprovar.yml`: aplicar uma issue aprovada

- Dispara quando a etiqueta `aprovado` é colocada numa issue do formulário **Cartão do dossiê**, e só se quem colocou for o dono do repositório.
- Executa `scripts/aplicar_issue.py`, que valida os campos (status e grupo de listas fechadas, links `https` de veículos aceitos, tamanhos, sem `<` ou `>`), altera `site/dossie.json` e o `index.html`, comenta o resultado e fecha a issue.
- Depois chama o `site.yml` para publicar (um push com o token do workflow não dispara outro workflow sozinho).
- O conteúdo da issue é tratado só como dado: nada vira comando.

## Fontes aceitas

G1, Folha, CNN Brasil, Poder360, Agência Brasil e Metrópoles para notícias; Agência Lupa, Aos Fatos e G1 Fato ou Fake para checagens. A Agência Brasil pode tirar páginas do ar durante o período eleitoral; nesse caso, troque o link por equivalente de outro veículo.
