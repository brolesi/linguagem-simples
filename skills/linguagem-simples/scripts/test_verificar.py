"""Testes do verificador. Rode com: python -m unittest test_verificar.py"""
import pathlib
import re
import subprocess
import sys
import unittest

from verificar import analisar, frases

AQUI = pathlib.Path(__file__).resolve().parent
EXEMPLOS = AQUI.parent / "references" / "exemplos.md"
FONTES = AQUI.parents[2] / "fontes"


def versoes(rotulo):
    """Extrai de exemplos.md os blocos citados que vêm depois de **rotulo**."""
    md = EXEMPLOS.read_text(encoding="utf-8")
    blocos = re.findall(r"\*\*" + re.escape(rotulo) + r"\*\*\n\n((?:>.*\n?)+)", md)
    return ["\n".join(l[1:].lstrip() for l in b.splitlines()) for b in blocos]

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

    def test_abreviatura_nao_quebra_frase(self):
        self.assertEqual(len(frases("O Sr. Silva chegou às 14h. A Dra. Souza saiu.")), 2)

    def test_caixa_alta_e_url_nao_sao_sigla(self):
        r = analisar("GUIA DE REDAÇÃO\n\nVeja em https://www.exemplo.gov.br/PDF/ABCD o texto.\n\nSILVA, João. Manual.")
        self.assertNotIn("sigla sem explicação", categorias(r))

    def test_sigla_explicada_passa(self):
        r = analisar("O Tribunal de Contas do Estado – TCESP pediu os dados. Depois, o TCESP respondeu.")
        self.assertNotIn("sigla sem explicação", categorias(r))

    def test_sequencia_de_aberturas_conta_uma_vez(self):
        r = analisar("Envie o RG. Envie o CPF. Envie a foto. Envie o comprovante. Envie a ficha.")
        self.assertEqual(sum(a["categoria"] == "aberturas repetidas" for a in r["achados"]), 1)

    def test_repeticao_tolerada_em_texto_longo(self):
        frase = "A equipe revisou o relatório na terça e mandou as correções para a chefia. "
        texto = frase * 120 + "Além disso, o prazo mudou. Além disso, a sala mudou."
        self.assertNotIn("expressão repetida", categorias(analisar(texto)))

    def test_texto_vazio(self):
        r = analisar("")
        self.assertEqual(r["palavras"], 0)
        self.assertEqual(r["achados"], [])


class TestRegressao(unittest.TestCase):
    """Os exemplos do guia funcionam como corpus de calibração."""

    def test_versoes_finais_passam(self):
        finais = versoes("Final")
        self.assertGreaterEqual(len(finais), 5)
        for t in finais:
            r = analisar(t)
            self.assertTrue(r["veredito"].startswith("bom"), (t[:60], r["achados"]))

    def test_versoes_com_cara_de_ia_sao_apontadas(self):
        ruins = versoes("Cara de IA")
        self.assertGreaterEqual(len(ruins), 5)
        for t in ruins:
            r = analisar(t)
            self.assertFalse(r["veredito"].startswith("bom"), (t[:60], r["pontos_por_100_palavras"]))

    def test_versoes_burocraticas_sao_apontadas(self):
        for t in versoes("Burocrático"):
            self.assertFalse(analisar(t)["veredito"].startswith("bom"), t[:60])

    def test_texto_humano_nao_pede_reescrita(self):
        # Os guias da Unicamp foram escritos por pessoas: podem ter achados, mas não o veredito máximo.
        for arq in sorted(FONTES.glob("*.txt")):
            r = analisar(arq.read_text(encoding="utf-8-sig"))
            self.assertFalse(r["veredito"].startswith("reescrever"), arq.name)


class TestRepositorio(unittest.TestCase):
    """Pega link quebrado, manifesto inválido e skill sem frontmatter antes de publicar."""
    RAIZ = AQUI.parents[2]

    def test_links_relativos_existem(self):
        for md in self.RAIZ.rglob("*.md"):
            if "nao-vai" in md.parts:
                continue
            for alvo in re.findall(r"\]\(([^)#\s]+)(?:#[^)]*)?\)", md.read_text(encoding="utf-8")):
                if not re.match(r"[a-z]+:", alvo):
                    self.assertTrue((md.parent / alvo).exists(), f"{md.relative_to(self.RAIZ)} → {alvo}")

    def test_manifestos_do_plugin(self):
        import json
        plugin = json.loads((self.RAIZ / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
        loja = json.loads((self.RAIZ / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8"))
        self.assertEqual(plugin["name"], loja["plugins"][0]["name"])
        self.assertRegex(plugin["version"], r"^\d+\.\d+\.\d+$")

    def test_frontmatter_das_skills(self):
        for skill in (self.RAIZ / "skills").glob("*/SKILL.md"):
            topo = re.match(r"---\n(.*?)\n---\n", skill.read_text(encoding="utf-8"), re.S)
            self.assertIsNotNone(topo, skill)
            self.assertIn(f"name: {skill.parent.name}\n", topo.group(1) + "\n")
            desc = re.search(r"^description: (.+)$", topo.group(1), re.M)
            self.assertTrue(desc and len(desc.group(1)) <= 1024, f"{skill}: description ausente ou longa demais")


class TestLinhaDeComando(unittest.TestCase):
    def rodar(self, *args, entrada=None):
        return subprocess.run([sys.executable, str(AQUI / "verificar.py"), *args], input=entrada,
                              capture_output=True, text=True, encoding="utf-8")

    def test_limite(self):
        ruim = "No mundo atual, vale ressaltar que isso faz toda a diferença."
        self.assertEqual(self.rodar("--limite", "3", "-", entrada=ruim).returncode, 1)
        self.assertEqual(self.rodar("--limite", "3", "-", entrada="A sala abre às 8h.").returncode, 0)

    def test_arquivo_inexistente(self):
        r = self.rodar("nao-existe.md")
        self.assertEqual(r.returncode, 2)
        self.assertIn("Não consegui abrir", r.stderr)

    def test_json(self):
        r = self.rodar("--json", "-", entrada="Estaremos enviando o boleto.")
        self.assertIn('"gerundismo"', r.stdout)


if __name__ == "__main__":
    unittest.main()
