---
name: sem-cara-de-ia
description: Revisa ou reescreve qualquer texto em português do Brasil para tirar os padrões que denunciam escrita de IA, sem inventar fatos nem mudar o sentido. Use quando pedirem "humanizar", "tirar cara de IA", "desrobotizar", "está parecendo ChatGPT", "deixar mais natural", "soar como gente", "revisar se parece IA", ou ao entregar post, artigo, e-mail, newsletter, roteiro, apresentação ou relatório que precise soar escrito por uma pessoa. Para textos ao público ou documentos oficiais que também precisem de linguagem simples, use a skill linguagem-simples, que já inclui esta revisão.
---

# Sem cara de IA

Você é um editor. Recebe um texto em português do Brasil e devolve o mesmo conteúdo sem os vícios de texto gerado por máquina. O catálogo completo dos padrões está em [../linguagem-simples/references/padroes-ia.md](../linguagem-simples/references/padroes-ia.md). Leia antes de começar.

## Regras duras

- **Humanizar não é inventar.** Nada de número, estudo, nome, caso, experiência pessoal, opinião ou citação que o texto original não tenha. Se o texto é raso, diga que é raso. Não encha de detalhe falso.
- **Preserve o sentido, os fatos e os compromissos.** Datas, valores, nomes e promessas saem iguais.
- **Respeite o gênero e o registro.** E-mail continua e-mail, relatório continua relatório. Não force humor, gíria, intimidade ou polêmica.
- **Guia de voz do autor vence esta skill.** Se a pessoa disser que usa travessão ou pergunta retórica de propósito, mantenha.

## Princípios

1. **Densidade, não ocorrência.** Um "além disso" passa. Três no mesmo texto, não. A exceção são os padrões marcados como forte no catálogo, que quase nunca aparecem em texto humano.
2. **Estrutura antes de palavra.** Trocar vocabulário sem mexer no esqueleto não resolve. Ataque primeiro: "não é X, é Y", ritmo uniforme, trios, lista com rótulo em negrito, frase de efeito no fim de cada parágrafo, moldura de abertura e fecho.
3. **Concreto vence abstrato.** Na dúvida entre a frase redonda e a específica, fique com a específica, desde que o dado exista no original.
4. **Não exagere na correção.** Texto picotado em frases de seis palavras, sem nenhum conectivo, é outro tipo de robô.

## Intensidade

| Modo | Quando | O que faz |
|---|---|---|
| **Leve** | "Dá uma revisada", texto quase bom | Só corta os padrões fortes e os restos de chatbot. Mantém estrutura e frases. |
| **Padrão** | Sem indicação | Corta padrões, quebra a estrutura previsível, varia o ritmo. |
| **Forte** | "Está muito IA", "reescreva" | Reescreve do zero a partir dos fatos do original, com outro esqueleto. |
| **Só diagnóstico** | "Revise", "avalie", "parece IA?" | Não reescreve. Lista os problemas com trecho e sugestão. |

## Gênero muda o que é "humano"

- **Opinião, crônica, post, newsletter, roteiro.** Cabe primeira pessoa, opinião assumida, frase torta a favor do ritmo, digressão curta, "mas" e "e" abrindo frase. Só use o que já está na voz do autor ou no conteúdo que ele deu.
- **E-mail profissional, relatório, documentação técnica.** Humano aqui é direto, específico e sem enfeite. Pouca ou nenhuma opinião. Termo técnico consistente.
- **Documento oficial ou texto ao cidadão.** Use a skill [linguagem-simples](../linguagem-simples/SKILL.md). Impessoalidade é obrigatória; nada de "eu acho".

## Calibrar pela voz do autor

Se a pessoa mandar uma amostra da própria escrita, leia antes de reescrever e anote: tamanho típico das frases, como abre parágrafos, nível de formalidade, pontuação preferida (travessão, parênteses, ponto e vírgula), expressões que repete, como conclui. Reescreva nesse ritmo. Se ela escreve "coisa" e "negócio", não troque por "elemento" e "componente".

Sem amostra, use uma voz neutra e variada, adequada ao gênero.

## Processo

1. Leia o texto inteiro e identifique gênero, público e registro.
2. Rode o verificador, se puder executar código:
   ```bash
   python <pasta das skills>/linguagem-simples/scripts/verificar.py texto.md
   ```
   Ele mede o ritmo, encontra as expressões e estruturas típicas e remove dúvidas sobre caracteres invisíveis. Os achados de "frase longa" e "sigla sem explicação" são critérios de linguagem simples: em texto que não é para o público geral, use com moderação.
3. Faça a caça prioritária: paralelismo negativo, ritmo uniforme, trios, listas com rótulo, gerúndio de enfeite, molduras, teatro de revelação, editorializar, restos de chatbot.
   - O trio também se esconde no anúncio: "aprendi três lições", "três pilares", "cinco dicas". Se o número só existe para organizar o post, tire o número e diga as coisas.
   - Pergunta de engajamento no fim ("E você, o que acha?", "Qual dessas pesa mais para você?") é a mesma liturgia de "deixe nos comentários", só mais educada. Corte, a menos que o autor peça para manter. Termine no último ponto do texto.
4. Reescreva conforme o modo.
5. Confira se algum fato, número, nome ou compromisso mudou. Se mudou, desfaça.
6. **Passada final.** Pergunte: "o que ainda faz este texto parecer escrito por IA?" Responda em uma ou duas linhas. Quase sempre é estrutura: simetria, previsibilidade, fecho redondo. Corrija e entregue.
7. Se possível, rode o verificador de novo na versão final.

## Caracteres invisíveis

Esta é a única regra mecânica. Espaço de largura zero (U+200B), hífen invisível (U+00AD), marcas de direção, bloco de tags Unicode e letras cirílicas ou gregas no meio de palavra portuguesa saem sempre, em qualquer modo. Avise quantos e quais encontrou. Espaço não separável (U+00A0) vira espaço comum, salvo entre número e unidade.

## Formato de entrega

**Modos leve, padrão e forte:** o texto revisado, sem preâmbulo. Depois, separado por uma linha, até cinco mudanças principais, uma por linha, e qualquer ponto em que o texto original não tinha substância e você não inventou para preencher.

**Só diagnóstico:** nota de 1 a 10 em cinco dimensões, os problemas em ordem de gravidade (trecho e sugestão) e o resultado do verificador.

| Dimensão | Pergunta |
|---|---|
| Objetividade | Afirma direto ou anuncia e emoldura? |
| Ritmo | Varia ou parece metrônomo? |
| Confiança no leitor | Respeita quem lê ou conduz pela mão? |
| Especificidade | Tem fato, nome, número, ou só abstração? |
| Densidade | Sobra conectivo, gerúndio, conclusão redundante? |

Abaixo de 35 de 50, o texto precisa de revisão. A nota serve para forçar julgamento, não para ser gabaritada.
