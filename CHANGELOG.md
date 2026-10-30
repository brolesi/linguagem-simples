# Changelog

## 1.1.0 (2026-10-29)

**Verificador**

- Opção `--limite N` para uso em CI e pre-commit. Códigos de saída: 0, 1 (acima do limite) e 2 (erro de leitura).
- Mensagem clara para arquivo inexistente ou fora de UTF-8; BOM no início do arquivo é ignorado.
- Menos falsos positivos de sigla: palavras em caixa alta, sobrenomes em referência ABNT e trechos de URL deixaram de contar.
- Sequência de frases com a mesma abertura conta uma vez só.
- Expressões comuns toleram mais repetições em texto longo.
- Piso de 100 palavras (antes 150) para medir texto curto.
- Novos padrões: "temos o prazer de", "reflete nosso compromisso", "mundo atual" em qualquer posição, "em virtude da/do", "no período compreendido entre", "a partir da presente data", "sendo que", "deverá ser realizada", "a realização de", "Prezados senhores", "a todos os servidores", "mais do que X, Y representa…".
- Frases dentro de itens de lista e frases que terminam em negrito passaram a ser separadas corretamente.

**Testes e CI**

- 22 testes, incluindo calibração contra os exemplos do guia e contra os guias da Unicamp (texto humano), linha de comando e integridade do repositório.
- GitHub Actions em Linux e Windows, Python 3.9 e 3.13.

**Skills**

- Evals no formato do skill-creator: 8 casos para `linguagem-simples` e 4 para `sem-cara-de-ia`.

## 1.0.0 (2026-10-29)

- Primeira versão: skills `linguagem-simples` e `sem-cara-de-ia`, guia consolidado, catálogo de padrões de IA, referência de redação oficial, exemplos e verificador.
