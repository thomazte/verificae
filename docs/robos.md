# Robôs e publicação

Há dois workflows em `.github/workflows/`.

## `site.yml`: atualizar e publicar

- Roda duas vezes por dia (06h e 18h de Brasília), a cada alteração em `site/` ou `scripts/`, e pelo botão "Run workflow".
- Executa `scripts/fetch_checagens.py`, que lê os feeds da Agência Lupa, do Aos Fatos e do G1 Fato ou Fake e grava as checagens novas no `index.html` e em `site/checagens.json`.
- Guarda o acumulado no repositório (os feeds só trazem os últimos itens) e publica a pasta `site/` no GitHub Pages.

Importante: o robô **não verifica veracidade**. Ele repassa o veredito que a agência já publicou, com título e link originais.

### Ligar o GitHub Pages (uma vez)

Em Settings, Pages, escolha **Source: GitHub Actions**. Depois rode o workflow pela aba Actions.

## `vigia.yml`: avisar de notícia nova

- Roda três vezes por dia (08h, 14h e 20h de Brasília).
- Executa `scripts/vigia.py`, que procura notícias sobre Flávio no G1, na Folha, no Poder360 e no Metrópoles (feeds de política).
- Se há notícia nova com tema relevante (PF, STF, investigação, emendas etc.), abre uma **Issue** com a etiqueta `revisar`, listando os links e indicando qual cartão do dossiê pode precisar de revisão.
- **Não publica nem altera o site.** O dossiê só muda quando uma pessoa revisa e edita.
- Guarda o que já foi visto em `vigia/vistos.json`, para não repetir.

## Fontes aceitas

G1, Folha, CNN Brasil, Poder360, Agência Brasil e Metrópoles para notícias; Agência Lupa, Aos Fatos e G1 Fato ou Fake para checagens. A Agência Brasil pode tirar páginas do ar durante o período eleitoral; nesse caso, troque o link por equivalente de outro veículo.
