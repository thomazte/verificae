# Conteúdo e revisão

## Fluxo: da notícia ao site

1. O **vigia** abre uma issue `revisar` com notícias novas.
2. Você lê as matérias. Se algo mudou, abra uma issue pelo formulário **Cartão do dossiê** (Issues, New issue). A ação pode ficar em branco: com o ID de um cartão que já existe o robô atualiza, e sem ID cria um novo (para remover, escolha a ação explicitamente). Preencha os campos e as fontes (`Nome | https://link`, uma por linha).
3. Confira e ponha a etiqueta **`aprovado`**. Só o dono do repositório consegue disparar.
4. O robô valida, grava o cartão em `site/dossie.json`, atualiza a data do topo, comenta o resultado, fecha a issue e publica o site (1 a 2 minutos).

Se algo estiver errado (fonte fora da lista, campo faltando, ID inexistente), o robô não aplica nada, comenta o motivo e tira a etiqueta. Corrija e aprove de novo.

**Paywall:** notícias da Folha aparecem marcadas com 🔒 e servem só de alerta. Cite no cartão uma matéria que você consegue ler (G1, CNN, Metrópoles, Agência Brasil…); o link "procurar cobertura aberta" ajuda a achar a mesma notícia em outro veículo.

Em **atualização**, campos vazios mantêm o que já existe, e as fontes novas são **acrescentadas** às antigas. Para remover uma fonte antiga, edite `site/dossie.json` e rode `python3 scripts/dossie.py embutir`.

Fontes aceitas: G1, O Globo, Folha, UOL, CNN Brasil, Poder360, Agência Brasil, Metrópoles, Conjur, Estadão, Lupa, Aos Fatos e domínios oficiais (`.gov.br`, `.jus.br`, `.leg.br`, `.mp.br`). Links `http` sem `s` são recusados. Para incluir outro veículo, edite a lista `DOMINIOS` em `scripts/aplicar_issue.py`.

## Regras para os cartões

1. **Só entra o que tem fonte verificável**: veículo de grande circulação ou documento oficial. Alegação sem confirmação independente, fala de familiar e pedido de adversário político ficam de fora.
2. **Status real em cada cartão.** Investigação não é condenação. Escreva "investigado", "denunciado", "arquivado" ou "condenado" conforme o caso, e nunca "inocentado" para arquivamento sem julgamento de mérito.
3. **Resposta da defesa no mesmo cartão**, literal quando possível. Se não houver, diga isso.
4. **Decisão favorável ao citado aparece no mesmo cartão.** Se o cartão perde o sentido sem ela, retire o cartão inteiro, não só a parte favorável.
5. **Falas**: citação curta e literal, data e local, quem criticou e a explicação dele. Nada de falas de familiares atribuídas a ele, e nenhuma conclusão jurídica nossa ("inconstitucional") sem fonte jurídica.
6. **Revisão após cada Issue `revisar`.** Se um fato mudou, atualize `situacao`, `defesa` e a data de "atualizado em" no topo do `index.html`.

## O que já foi deixado de fora de propósito

- Ligação com o "Careca do INSS": existe só um pedido de investigação de um deputado adversário, sem investigação confirmada.
- Gastos pessoais pagos por terceiros e suposta intermediação junto a ministro do STF: sem comprovação independente.
- Acusação contra o vice: é sobre outra pessoa (e foi arquivada pelo ministro Gilmar Mendes em 06/10/2026, segundo o G1).
- Números de movimentação do Coaf: vêm de dados que o STF e o STJ anularam.
