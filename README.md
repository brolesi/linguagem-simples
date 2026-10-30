# Linguagem simples

Duas skills para agentes de IA (Claude Code, Claude.ai e outros que leem `SKILL.md`) que escrevem em português do Brasil:

- **`linguagem-simples`** escreve, reescreve e revisa textos para que qualquer pessoa entenda na primeira leitura. Segue os guias de linguagem simples e de redação oficial da Unicamp e termina com uma revisão para tirar os vícios de texto gerado por IA.
- **`sem-cara-de-ia`** revisa qualquer texto em pt-BR (post, artigo, e-mail, relatório) para tirar esses vícios, sem impor as regras de linguagem simples.

As duas usam um verificador em Python que aponta frase longa, sigla sem explicação, burocratês, termo pejorativo, expressões e estruturas típicas de IA, ritmo uniforme e caracteres invisíveis.

O repositório também guarda os quatro guias da Unicamp que serviram de base, em texto puro, na pasta [`fontes/`](fontes).

## Por que existe

Quem pede para uma IA "reescrever em linguagem simples" costuma receber um texto mais fácil de ler e, ao mesmo tempo, com cara de máquina: título em Title Case, emoji, lista com rótulo em negrito, "não se trata apenas de X, mas de Y", três adjetivos seguidos e uma frase motivacional no fim. Trocou-se o burocratês por outro vício.

Veja um caso. O original:

> Comunicamos aos senhores usuários que, em virtude da realização de manutenção preventiva nos equipamentos do sistema de abastecimento, haverá interrupção do fornecimento de água no período compreendido entre as 8h e as 17h do dia 12 de março.

O que um modelo costuma devolver:

> **Aviso Importante: Manutenção No Sistema De Abastecimento** 💧
>
> No dia 12 de março, realizaremos uma manutenção essencial no sistema, garantindo mais qualidade e segurança para você e sua família. Não se trata apenas de um reparo, mas de um investimento no seu bem-estar!

O que a skill entrega:

> **Falta de água na terça-feira, 12 de março**
>
> A água vai faltar das 8h às 17h por causa de uma manutenção nas bombas da Estação Centro. Depois das 17h, ela volta aos poucos. Em algumas casas pode levar até a noite.
>
> Encha uma vasilha para beber e cozinhar antes das 8h. Dúvidas: 0800 000 0000.

(Os detalhes como "Estação Centro" e o telefone precisam vir de quem pede. Quando não vêm, a skill escreve `[INFORMAR: telefone de atendimento]` em vez de inventar.)

Mais cinco casos estão em [`exemplos.md`](skills/linguagem-simples/references/exemplos.md).

## Instalação

### Claude Code, como plugin

```bash
claude plugin marketplace add brolesi/linguagem-simples
```

```bash
claude plugin install linguagem-simples@linguagem-simples
```

Ou, dentro de uma sessão do Claude Code, `/plugin marketplace add brolesi/linguagem-simples` e depois `/plugin install linguagem-simples@linguagem-simples`.

### Claude Code, copiando as pastas

Copie as duas pastas de `skills/` para `~/.claude/skills/` (vale para todos os projetos) ou para `.claude/skills/` dentro de um projeto. As duas precisam ficar lado a lado, porque `sem-cara-de-ia` usa o catálogo e o verificador que estão em `linguagem-simples`.

```bash
git clone https://github.com/brolesi/linguagem-simples.git
```

```bash
cp -r linguagem-simples/skills/linguagem-simples linguagem-simples/skills/sem-cara-de-ia ~/.claude/skills/
```

No Windows (PowerShell), o destino é `$env:USERPROFILE\.claude\skills\`.

### Claude.ai e app do Claude

Em **Configurações > Capacidades > Skills**, envie um `.zip` de cada pasta (`skills/linguagem-simples` e `skills/sem-cara-de-ia`). O verificador roda quando a execução de código está ativada. Sem ela, a skill faz a checagem lendo.

### Outros agentes

O formato `SKILL.md` com frontmatter YAML é lido por vários agentes. Em ferramentas que não carregam skills, cole o conteúdo de `skills/linguagem-simples/SKILL.md` como instrução de sistema e anexe os arquivos de `references/`.

## Como usar

As skills disparam sozinhas quando o pedido combina com a descrição. Alguns exemplos:

```text
Escreva um aviso para os moradores sobre a vacinação de cães e gatos no sábado, das 8h às 16h, na praça da matriz. Público: moradores do bairro, muitos idosos.
```

```text
Reescreva este ofício em linguagem simples, mantendo a formalidade: [texto]
```

```text
Revise este comunicado e me diga o que ainda está difícil de entender ou com cara de IA: [texto]
```

```text
Tira a cara de IA deste post do LinkedIn. Aqui vai um texto meu antigo para você pegar o meu jeito de escrever: [amostra]
```

### Modos

| Skill | Modos |
|---|---|
| `linguagem-simples` | **escrever** (do zero), **reescrever** (simplificar texto existente), **revisar** (diagnóstico com notas e trechos) |
| `sem-cara-de-ia` | **leve**, **padrão**, **forte** e **só diagnóstico** |

## Como a skill `linguagem-simples` trabalha

1. **Planeja.** Quem lê, o que já sabe, o que precisa saber, o que deve fazer depois. Separa a ideia principal da secundária e corta a terciária.
2. **Escreve** com as regras do guia: o mais importante primeiro, ordem direta, verbo em vez de substantivo, palavra comum, sigla explicada, mesmo termo do começo ao fim, linguagem inclusiva, lista só para itens de verdade.
3. **Tira a cara de IA** começando pela estrutura: a fórmula "não é X, é Y", parágrafos e frases do mesmo tamanho, trios automáticos, listas com rótulo em negrito, gerúndio de enfeite, moldura de abertura e fecho, frase de efeito no fim de cada parágrafo. Só depois olha o vocabulário.
4. **Verifica.** Roda o verificador, corrige o que se acumula, pergunta "o que ainda parece IA aqui?" e corrige de novo. Por fim, confere que nenhum fato, número ou prazo mudou.

### Quando as regras parecem brigar

Linguagem simples e texto humano puxam para o mesmo lado quase sempre. Em quatro pontos parecem se contradizer:

| Ponto | Linguagem simples pede | IA costuma fazer | A skill faz |
|---|---|---|---|
| Frases | Curtas | Todas do mesmo tamanho | Média curta, com variação real |
| Listas | Lista para separar itens | Lista para tudo, com rótulo em negrito e três itens | Lista só para itens paralelos, sem rótulo, quantos existirem |
| Títulos | Títulos para organizar | Pirâmide de títulos em Title Case | Título só em texto longo, que informa, com maiúscula só na primeira palavra |
| Tom | Amigável | Simpatia artificial e exclamação | Cordial e direto |

E uma diferença de gênero: em post e crônica, soar humano inclui opinião e primeira pessoa. Em documento oficial, a impessoalidade é obrigatória, e o que torna o texto humano é ser concreto e específico.

## O verificador

[`verificar.py`](skills/linguagem-simples/scripts/verificar.py) usa só a biblioteca padrão do Python 3.

```bash
python skills/linguagem-simples/scripts/verificar.py meu-texto.md
```

```bash
python skills/linguagem-simples/scripts/verificar.py --json meu-texto.md
```

Também lê da entrada padrão com `-` no lugar do arquivo.

O relatório mostra o tamanho médio das frases, a variação de tamanho das frases e dos parágrafos, os achados com linha, trecho e sugestão, e um veredito:

- **bom**: menos de 3 pontos por 100 palavras;
- **revisar**: de 3 a 8;
- **reescrever**: 8 ou mais.

Cada achado tem peso de 0 a 3. Peso 3 é para o que quase nunca aparece em texto humano ou não pode passar (termo discriminatório, caractere invisível). Expressões comuns, como "além disso" ou "através de", só entram quando se repetem.

| Categoria | O que procura |
|---|---|
| Expressão típica de IA | "é importante ressaltar", "no mundo atual", "faz toda a diferença", "em resumo", "papel crucial", restos de chatbot |
| Expressão repetida | Conectivos e palavras de inflação que aparecem duas vezes ou mais |
| Burocratês e chavão | As tabelas de verbosidade e chavões dos guias ("em epígrafe", "outrossim", "vimos por meio desta", "sem mais para o momento") |
| Termo pejorativo | A tabela de termos discriminatórios do guia, com a alternativa |
| Paralelismo negativo | "não é X, é Y", "não apenas… mas", "mais do que um X, é Y", "deixou de ser", "menos sobre… mais sobre" |
| Gerúndio de enfeite | ", garantindo", ", promovendo", ", contribuindo" depois de vírgula |
| Gerundismo | "estaremos enviando", "vou estar verificando" |
| Ordem indireta | Voz passiva com agente ("foi entregue pela diretora") |
| Substantivo no lugar de verbo | "realizar a inscrição", "efetuar o pagamento" |
| Frase longa | Acima de 20 palavras (aviso) e acima de 30 (alerta) |
| Ritmo e parágrafos uniformes | Variação de tamanho baixa demais, típica de texto gerado |
| Sigla sem explicação | Primeira ocorrência de sigla sem o nome completo ao lado |
| Tipografia | Title Case, lista com rótulo em negrito, excesso de negrito, travessão, emoji, exclamação, dois-pontos como muleta |
| Caracteres invisíveis | Espaço de largura zero, hífen invisível, marcas de direção, letras cirílicas e gregas no meio de palavras |

Para rodar os testes:

```bash
cd skills/linguagem-simples/scripts && python -m unittest test_verificar.py
```

## Estrutura do repositório

```
.
├── .claude-plugin/
│   ├── plugin.json              manifesto do plugin
│   └── marketplace.json         permite instalar com /plugin marketplace add
├── fontes/                      os quatro guias da Unicamp em texto puro
├── skills/
│   ├── linguagem-simples/
│   │   ├── SKILL.md
│   │   ├── references/
│   │   │   ├── regras-linguagem-simples.md   o guia consolidado
│   │   │   ├── padroes-ia.md                 catálogo de padrões de IA em pt-BR
│   │   │   ├── redacao-oficial.md            tratamento, datas, siglas, espécies de documento
│   │   │   └── exemplos.md                   seis casos antes e depois
│   │   └── scripts/
│   │       ├── verificar.py
│   │       └── test_verificar.py
│   └── sem-cara-de-ia/
│       └── SKILL.md
├── LICENSE
└── README.md
```

Se você só quer ler o guia, comece por [`regras-linguagem-simples.md`](skills/linguagem-simples/references/regras-linguagem-simples.md).

## Fontes

**Guias de linguagem simples e redação oficial** (Universidade Estadual de Campinas, Grupo de Trabalho da Portaria CGU nº 01/2023, 2024), em versão acessível do Laboratório de Acessibilidade da Unicamp (LABACES):

- *Guia de Linguagem Simples*
- *Guia de Atributos e Elementos da Redação Oficial*
- *Guia de Atos Administrativos Simplificado*
- *Manual de Padronização dos Atos Administrativos*

Esses guias, por sua vez, se apoiam no *Manual de Redação da Presidência da República* (2018), nas *Federal Plain Language Guidelines* (PLAIN, 2011), no *Guia de Linguagem Simples* do TJRS (2021), no programa de linguagem simples da Prefeitura de São Paulo e na Rede Linguagem Simples Brasil, entre outros.

**Projetos sobre texto gerado por IA em português**, cujos padrões foram reunidos e reescritos em [`padroes-ia.md`](skills/linguagem-simples/references/padroes-ia.md):

- [Zero-Lero](https://github.com/ViniciusStanula/Zero-Lero), de Vinicius Stanula
- [humanizer-pt-br](https://github.com/mackswendhell/humanizer-pt-br), de mackswendhell
- [desrobotizar](https://github.com/VitorDiToro/claude-plugins/blob/main/desrobotizar/skills/desrobotizar/SKILL.md), de Vitor Di Toro
- [humanizador](https://github.com/AndreAlmeidaDC/humanizador), de André Almeida
- [human-writer-pt](https://github.com/MrBridgeHQ/human-writer-pt), de Mr Bridge

## Limitações

- **O objetivo é clareza, não enganar detector.** Um texto que segue estas skills tende a não parecer IA porque fica específico e bem escrito. Nenhum verificador garante o resultado de ferramentas como GPTZero ou Copyleaks, e as skills não tentam otimizar para elas.
- **O verificador aponta, não decide.** Regex não entende contexto. Um "não é X, é Y" pode ser a melhor frase do texto. A palavra "jornada" é correta em "jornada de trabalho". Leia os achados com julgamento.
- **O padrão de formatação é o da Unicamp.** Margens, fontes e espécies de documento seguem o manual da universidade. Tratamento, datas e siglas seguem o *Manual de Redação da Presidência*, que vale para todo o serviço público federal. Para outra instituição, confira o manual dela.
- **Teste com gente.** A melhor validação de linguagem simples continua sendo pedir a alguém do público para ler e dizer o que entendeu.

## Contribuições

Abra uma issue ou um pull request com:

- um padrão de IA em pt-BR que não está no catálogo, com um exemplo real;
- um falso positivo do verificador, com o trecho;
- um exemplo antes e depois de outro tipo de documento.

## Licença

O código, as skills e os textos de referência deste repositório estão sob a [licença MIT](LICENSE).

Os arquivos da pasta [`fontes/`](fontes) são da Universidade Estadual de Campinas e estão aqui como material de referência, com crédito à instituição e ao grupo de trabalho que os elaborou. A licença MIT não se aplica a eles.
