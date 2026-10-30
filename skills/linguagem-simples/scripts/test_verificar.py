"""Testes do verificador. Rode com: python -m unittest test_verificar.py"""
import unittest

from verificar import analisar

TEXTO_IA = """# Guia Completo Para Melhorar Sua Comunicação

No mundo atual, a comunicação clara é fundamental. Não se trata apenas de escrever bem, é sobre conectar pessoas.

Além disso, é importante ressaltar que o processo foi realizado pela equipe, garantindo resultados expressivos. Além disso, estaremos enviando o material.

- **Clareza:** A clareza melhora a leitura.
- **Objetividade:** A objetividade economiza tempo.

Em resumo, a comunicação faz toda a diferença.
"""

TEXTO_LIMPO = """A inscrição para o curso de Linguagem Simples vai até 15 de março.

Para se inscrever, entre no site da Escola de Educação Corporativa – Educorp e preencha o formulário. Leva uns cinco minutos. Se o site não abrir, mande um e-mail para a secretaria e diga seu nome completo, sua matrícula e o setor onde você trabalha.

As vagas são limitadas a 40 pessoas.
"""


def categorias(r):
    return {a["categoria"] for a in r["achados"]}


class TestVerificar(unittest.TestCase):
    def test_texto_com_cara_de_ia(self):
        r = analisar(TEXTO_IA)
        c = categorias(r)
        for esperado in ("expressão típica de IA", "paralelismo negativo", "gerúndio de enfeite",
                         "gerundismo", "voz passiva com agente", "expressão repetida",
                         "lista com rótulo em negrito", "título em Title Case"):
            self.assertIn(esperado, c)
        self.assertTrue(r["veredito"].startswith("reescrever"))

    def test_texto_limpo(self):
        r = analisar(TEXTO_LIMPO)
        self.assertTrue(r["veredito"].startswith("bom"), r)
        self.assertNotIn("sigla sem explicação", categorias(r))

    def test_burocrates_e_discriminatorio(self):
        r = analisar("Vimos por meio desta informar que o assunto em epígrafe está na lista negra.")
        c = categorias(r)
        self.assertIn("burocratês/chavão", c)
        self.assertIn("termo pejorativo ou excludente", c)

    def test_sigla_sem_explicacao(self):
        r = analisar("O TCESP pediu as informações à DGA.")
        self.assertIn("sigla sem explicação", categorias(r))

    def test_invisiveis(self):
        r = analisar("Texto​ com marca­ escondida.")
        self.assertIn("caractere invisível", categorias(r))

    def test_frase_longa(self):
        longa = " ".join(["palavra"] * 35) + "."
        self.assertIn("frase longa", categorias(analisar(longa)))


if __name__ == "__main__":
    unittest.main()
