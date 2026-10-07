# Como o site funciona

Tudo está em `site/index.html`, sem build e sem dependências.

## Dossiê

Os cartões ficam na lista `ITEMS` dentro do `<script>`. Cada item tem:

- `id`, `grupo` (`casos` ou `falas`), `status`, `data`, `titulo`, `resumo`;
- `situacao` (estágio real do caso) e `defesa` (resposta de quem é citado);
- `fontes`: lista de `[nome, link]`.

Os selos de `status` são definidos em `BADGES`: `investigado`, `arquivado`, `reportagem`, `fala`, `posicao`, `favoravel`.

## Busca "Recebeu algo no zap?"

As checagens ficam embutidas no próprio `index.html`, entre os marcadores `/*DADOS*/` e `/*FIM*/`. Não apague esses marcadores: é entre eles que o robô grava os dados. A busca ignora acentos e mostra até 10 resultados por relevância.

O veredito (falso, enganoso, verdadeiro) vem do título publicado pela agência. Sem veredito claro, o selo diz só "Checagem".

## Tema

O site abre sempre no tema claro (azul-marinho). O botão de sol e lua, no canto superior direito, liga o tema escuro, e o navegador lembra a escolha.

## Rodapé

O campo "Quem mantém este site" identifica o responsável e o contato para correções. A legislação eleitoral exige identificação de quem publica, então mantenha-o sempre preenchido.
