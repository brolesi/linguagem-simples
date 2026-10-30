#!/usr/bin/env python3
"""Verificador de linguagem simples e de padrões de texto gerado por IA (pt-BR).

Uso:
    python verificar.py texto.md
    python verificar.py --json texto.md
    python verificar.py --limite 8 texto.md   (código 1 se passar do limite)
    cat texto.md | python verificar.py -

Códigos de saída: 0 ok, 1 acima do --limite, 2 erro ao ler o arquivo.

Só usa a biblioteca padrão. Os achados são alertas para julgamento humano:
o que conta é a densidade, não cada ocorrência isolada.
"""
import argparse
import json
import re
import statistics
import sys
import unicodedata

# ---------------------------------------------------------------------------
# Listas de expressões. Formato: expressão -> sugestão ("" = corte ou reescreva).
# ---------------------------------------------------------------------------

# Quase nunca aparecem em texto humano. Uma ocorrência já merece olhar.
IA_FORTE = {
    "não é à toa que": "corte e deixe a evidência falar",
    "faz toda a diferença": "diga qual diferença",
    "um verdadeiro": "corte o reforço",
    "uma verdadeira": "corte o reforço",
    "em resumo": "termine no último ponto que importa",
    "em suma": "termine no último ponto que importa",
    "resumindo:": "termine no último ponto que importa",
    "em conclusão": "termine no último ponto que importa",
    "em última análise": "corte",
    "mundo atual": "diga qual mudança concreta, ou corte",
    "nos dias de hoje": "comece pelo assunto",
    "nos dias atuais": "comece pelo assunto",
    "mundo cada vez mais": "comece pelo assunto",
    "no cenário atual": "diga qual cenário, ou corte",
    "no contexto atual": "diga qual contexto, ou corte",
    "em constante evolução": "corte",
    "é importante ressaltar": "afirme direto",
    "é importante destacar": "afirme direto",
    "é importante lembrar": "afirme direto",
    "é importante salientar": "afirme direto",
    "é importante notar": "afirme direto",
    "vale ressaltar": "afirme direto",
    "vale destacar": "afirme direto",
    "vale lembrar": "afirme direto",
    "vale mencionar": "afirme direto",
    "cabe ressaltar": "afirme direto",
    "cabe destacar": "afirme direto",
    "convém destacar": "afirme direto",
    "convém ressaltar": "afirme direto",
    "espero ter ajudado": "corte (resto de conversa com chatbot)",
    "espero que isso ajude": "corte (resto de conversa com chatbot)",
    "ótima pergunta": "corte (resto de conversa com chatbot)",
    "excelente pergunta": "corte (resto de conversa com chatbot)",
    "se quiser, posso": "corte (resto de conversa com chatbot)",
    "fique à vontade para": "corte ou diga o que a pessoa deve fazer",
    "é aqui que entra": "entregue a informação direto",
    "e é aqui que": "entregue a informação direto",
    "é aí que entra": "entregue a informação direto",
    "o que ninguém te conta": "corte o teatro de revelação",
    "o que poucos sabem": "corte o teatro de revelação",
    "a boa notícia?": "entregue a informação direto",
    "o pulo do gato": "entregue a informação direto",
    "por que isso importa": "mostre a importância com um fato",
    "isso muda tudo": "diga o que muda",
    "mergulhar fundo": "corte",
    "vamos mergulhar": "corte",
    "mergulhe": "corte",
    "tapeçaria": "corte a metáfora",
    "divisor de águas": "diga o que mudou",
    "no final do dia": "no fim, afinal (ou corte)",
    "na mesma página": "de acordo, alinhados",
    "mover o ponteiro": "dizer o efeito concreto",
    "papel crucial": "diga o que a coisa faz",
    "papel fundamental": "diga o que a coisa faz",
    "desempenha um papel": "diga o que a coisa faz",
    "lança as bases": "diga o que foi feito",
    "pedra angular": "base (ou corte)",
    "imagine um mundo": "comece pelo fato",
    "você já parou para pensar": "afirme",
    "pense nisso": "corte",
    "sem sombra de dúvida": "corte",
    "temos o prazer de": "dê a notícia direto",
    "temos a satisfação de": "dê a notícia direto",
    "reflete nosso compromisso": "diga o que foi feito",
    "reforça nosso compromisso": "diga o que foi feito",
    "reforça o compromisso": "diga o que foi feito",
    "reforça seu compromisso": "diga o que foi feito",
    "compromisso contínuo": "diga o que foi feito",
    "importância crucial": "diga por que importa, com um fato",
}

# Normais em texto humano; viram sinal quando se acumulam (2+ no texto).
IA_DENSIDADE = {
    "além disso": "", "dessa forma": "", "desta forma": "", "nesse sentido": "",
    "nesse contexto": "", "neste contexto": "", "diante disso": "",
    "diante desse cenário": "", "por fim": "", "ademais": "também",
    "cada vez mais": "quantifique ou corte", "através de": "por, com, pelo",
    "de forma eficiente": "", "de forma eficaz": "", "de forma clara": "",
    "de maneira eficiente": "", "de maneira eficaz": "",
    "conta com": "tem", "contam com": "têm",
    "crucial": "", "essencial": "", "jornada": "processo, etapa (se não for jornada de trabalho)",
    "desvendar": "explicar, mostrar", "primordial": "",
    "potencializar": "aumentar, melhorar", "alavancar": "aumentar, usar",
    "otimizar": "melhorar, acelerar", "aprimorar": "melhorar",
    "robusto": "", "robusta": "", "sinergia": "", "inovador": "", "inovadora": "",
    "estratégico": "", "estratégica": "", "impulsionar": "aumentar",
    "no que tange": "sobre", "no que diz respeito a": "sobre",
    "à luz de": "segundo, com base em", "sob essa ótica": "",
    "inúmeros": "muitos (ou o número)", "inúmeras": "muitas (ou o número)",
    "uma série de": "", "uma gama de": "", "um leque de": "",
    "especialistas apontam": "nomeie a fonte ou corte",
    "estudos mostram": "nomeie a fonte ou corte",
    "estudos indicam": "nomeie a fonte ou corte",
    "pesquisas mostram": "nomeie a fonte ou corte",
    "de suma importância": "importante",
    "excelência": "", "transformação": "", "impactando": "afetando (ou o efeito concreto)",
}

# Burocratês e chavões dos guias de redação oficial e de linguagem simples.
BUROCRATES = {
    "concomitantemente": "ao mesmo tempo",
    "subsidiariamente": "de forma secundária",
    "peticionar": "entrar com uma ação",
    "expertise": "especialista, experiência",
    "outrossim": "também",
    "destarte": "assim, desta forma",
    "supracitado": "citado", "supracitada": "citada",
    "supramencionado": "citado", "supramencionada": "citada",
    "acima citado": "citado", "acima citada": "citada",
    "em epígrafe": "citado",
    "precípuo": "principal", "precípua": "principal",
    "aprazada": "no prazo",
    "desiderato": "objetivo",
    "via de regra": "geralmente",
    "devido ao fato de": "porque, por causa de",
    "tendo em vista que": "como, porque",
    "em virtude de": "por, por causa de",
    "em virtude da": "pela, por causa da",
    "em virtude do": "pelo, por causa do",
    "no período compreendido entre": "entre, de … a …",
    "a partir da presente data": "a partir de [data]",
    "sendo que": "e, mas (ou divida a frase)",
    "no sentido de": "para",
    "com o objetivo de": "para",
    "com a finalidade de": "para",
    "a fim de": "para",
    "por conseguinte": "por isso",
    "no tocante a": "sobre", "no tocante ao": "sobre o", "no tocante à": "sobre a",
    "mister se faz": "é preciso",
    "faz-se necessário": "é preciso",
    "faz-se mister": "é preciso",
    "cumpre salientar": "(corte e afirme)",
    "cumpre esclarecer": "(corte e afirme)",
    "impende destacar": "(corte e afirme)",
    "alhures": "em outro lugar",
    "temos a informar": "informamos",
    "levamos ao seu conhecimento": "informamos",
    "levamos a seu conhecimento": "informamos",
    "somos de opinião": "consideramos, acreditamos",
    "encarecemos": "solicitamos",
    "temos em nosso poder": "recebemos",
    "para dirimir dúvidas": "para esclarecer dúvidas",
    "dirimir": "esclarecer, resolver",
    "vimos, através desta": "comece pelo verbo (solicitamos, informamos)",
    "vimos através desta": "comece pelo verbo (solicitamos, informamos)",
    "vimos por meio desta": "comece pelo verbo (solicitamos, informamos)",
    "venho, por meio desta": "comece pelo verbo (solicito, informo)",
    "venho por meio desta": "comece pelo verbo (solicito, informo)",
    "venho, pelo presente": "comece pelo verbo (solicito, informo)",
    "pelo presente": "corte",
    "por intermédio da presente": "corte",
    "esta tem por finalidade": "comece pelo verbo",
    "acusamos o recebimento": "confirmamos o recebimento",
    "sem mais para o momento": "Atenciosamente,",
    "reiteramos os protestos": "Agradecemos a atenção / Atenciosamente,",
    "elevada estima e consideração": "Atenciosamente,",
    "elevada estima e apreço": "Atenciosamente,",
    "antecipadamente somos gratos": "agradecemos",
    "aproveitando o ensejo": "corte",
    "causou-nos espécie": "causou-nos estranheza",
    "ilustríssimo": "abolido; use Senhor/Senhora",
    "ilustríssima": "abolido; use Senhor/Senhora",
    "ilmo.": "abolido; use Senhor/Senhora",
    "ilma.": "abolido; use Senhor/Senhora",
    "digníssimo": "abolido; use Senhor/Senhora",
    "digníssima": "abolido; use Senhor/Senhora",
    "a próprio punho": "à mão",
    "residência domiciliar": "residência",
    "data venia": "com todo o respeito (ou corte)",
}

# Termos pejorativos ou excludentes (Guia de Linguagem Simples, Tabela 4).
DISCRIMINATORIOS = {
    "denegrir": "difamar", "denegriu": "difamou", "denegrindo": "difamando",
    "judiar": "maltratar", "judiou": "maltratou", "judiação": "maus-tratos",
    "mulata": "parda", "mulato": "pardo", "mulatas": "pardas", "mulatos": "pardos",
    "humor negro": "humor ácido",
    "lista negra": "lista restrita, lista proibida",
    "mercado negro": "mercado clandestino",
    "cor de pele": "bege, rosa-claro",
    "aleijado": "pessoa com deficiência", "aleijada": "pessoa com deficiência",
    "deficiente mental": "pessoa com deficiência intelectual",
    "portador de deficiência": "pessoa com deficiência",
    "portadora de deficiência": "pessoa com deficiência",
    "portadores de deficiência": "pessoas com deficiência",
    "os deficientes": "as pessoas com deficiência",
    "prezados senhores": "Prezadas Senhoras e Prezados Senhores",
    "prezados colaboradores": "Prezadas e prezados, ou o nome da equipe",
    "a todos os servidores": "às servidoras e aos servidores, ou 'você'",
    "todo cidadão": "toda cidadã e todo cidadão",
}

# Siglas tão comuns que não exigem nome por extenso.
SIGLAS_COMUNS = {
    "CPF", "RG", "CEP", "CNPJ", "PDF", "URL", "OK", "PIX", "SUS", "INSS", "IBGE",
    "ONU", "TV", "DVD", "CD", "USB", "HTML", "CSS", "API", "IA", "AI", "EUA",
    "BR", "SP", "RJ", "MG", "RS", "PR", "SC", "BA", "PE", "CE", "DF", "GO", "PA",
    "AM", "ES", "MT", "MS", "PB", "RN", "AL", "SE", "PI", "MA", "TO", "RO", "AC",
    "AP", "RR", "UTC", "GMT", "LTDA", "SA", "ME", "MEI", "FAQ", "PS", "XML", "JSON",
    "CLT", "FGTS", "IPTU", "IPVA", "CNH", "OAB", "CRM", "SMS", "PS",
}

GERUNDIO_ENFEITE = (
    "garantindo|proporcionando|promovendo|permitindo|possibilitando|contribuindo|"
    "demonstrando|evidenciando|refletindo|destacando|reforçando|fortalecendo|ampliando|"
    "otimizando|facilitando|assegurando|gerando|trazendo|oferecendo|consolidando|"
    "impulsionando|potencializando|tornando|buscando|visando|simbolizando|marcando|"
    "abrindo|elevando|transformando|criando|agregando|valorizando|resultando|impactando"
)

INVISIVEIS = {
    "​": "zero width space", "‌": "zero width non-joiner",
    "‍": "zero width joiner", "⁠": "word joiner", "﻿": "BOM no meio do texto",
    "­": "hífen invisível (soft hyphen)", "᠎": "separador mongol",
    "‎": "marca LTR", "‏": "marca RTL",
}
HOMOGLIFOS = "аеорсухοАЕОРСХ"  # cirílico e grego que imitam letras latinas

PADROES = [
    # (categoria, regex, peso, mensagem)
    ("paralelismo negativo",
     r"\bnão (?:é|são|foi|era|se trata|se resume|basta)(?: apenas| só| somente| simplesmente| mais)?\b"
     r"[^.!?\n]{0,90}?(?:[,;.—–]|\s-)\s*(?:é|são|mas|e sim|trata-se|se trata|era)\b",
     3, "fórmula 'não é X, é Y': afirme Y direto"),
    ("paralelismo negativo", r"\bnão (?:apenas|só|somente)\b[^.!?\n]{1,80}?\bmas(?: também)?\b",
     2, "'não apenas X, mas Y': diga as duas coisas sem a rampa"),
    ("paralelismo negativo", r"\bmais do que (?:um|uma|apenas|só)\b[^.!?\n]{1,60}?[,.]\s*(?:[^.!?\n]{0,40}?\b)?(?:é|são|representa|significa|torna-se)\b",
     3, "'mais do que X, é Y': afirme Y direto"),
    ("paralelismo negativo", r"\bdeixou de ser\b[^.!?\n]{1,60}?\b(?:se tornou|passou a ser|para (?:se tornar|ser))\b",
     2, "'deixou de ser X e virou Y': diga o que é hoje, com dado"),
    ("paralelismo negativo", r"\bmenos sobre\b[^.!?\n]{1,60}?\bmais sobre\b",
     3, "'menos sobre X, mais sobre Y': afirme Y"),
    ("gerúndio de enfeite", r",\s+(?:" + GERUNDIO_ENFEITE + r")\b",
     2, "cláusula com gerúndio depois da vírgula: corte ou troque pela consequência concreta"),
    ("gerundismo", r"\b(?:estarei|estaremos|estará|estarão|(?:vou|vamos|vai|vão|pode|posso|podemos|podem|deve|devemos|devem|irei|iremos|irá|irão) estar)\s+\w+(?:ando|endo|indo)\b",
     3, "gerundismo: use 'enviaremos' ou 'vamos enviar'"),
    ("voz passiva com agente",
     r"\b(?:foi|foram|será|serão|é|são|era|eram|seja|sejam|tem sido|têm sido)\s+\w+(?:ado|ada|ados|adas|ido|ida|idos|idas)\s+pel[oa]s?\b",
     1, "passiva com agente: ponha quem faz no começo (ordem direta)"),
    ("substantivo no lugar do verbo",
     r"\b(?:ser|sendo|foi|foram|será|serão|deverá ser|deverão ser|deve ser|devem ser)\s+(?:realizad|efetuad)\w*\b|\brealização d[eaoe]s?\b",
     1, "troque 'deverá ser realizada' ou 'a realização de' pelo verbo da ação: 'peça', 'faça', 'inscreva-se'"),
    ("substantivo no lugar do verbo",
     r"\b(?:realiz|efetu|proced|promov)\w*\s+(?:a|à|o|ao|as|os|uma|um)\s+\w+(?:ção|ções|mento|mentos|agem)\b",
     1, "troque 'realizar a inscrição' por 'inscrever-se', 'efetuar o pagamento' por 'pagar'"),
    ("pergunta retórica autorrespondida", r"(?:^|[.!]\s+)[A-ZÁÉÍÓÚ][^.!?\n]{0,40}\?\s+[A-ZÁÉÍÓÚ][^.!?\n]{0,60}[.!]",
     1, "pergunta seguida da resposta: afirme direto (ignore se for FAQ)"),
]

ABREVIATURAS = r"(?:Sr|Sra|Srs|Sras|Dr|Dra|Drs|Dras|Prof|Profa|Exa|Exma|Exmo|Sa|av|Av|art|Art|n|nº|p|pág|tel|etc|ex|cód|end|min|máx|obs|Obs|V|S|fl|fls|inc|Ltda|Cia|aprox|séc|vol|ed|jan|fev|mar|abr|jun|jul|ago|set|out|nov|dez)\."


def normalizar(texto):
    """Remove blocos de código e devolve só a prosa."""
    texto = re.sub(r"```.*?```", " ", texto, flags=re.S)
    texto = re.sub(r"`[^`]*`", " ", texto)
    texto = re.sub(r"https?://\S+|www\.\S+|\S+@\S+\.\w+", " ", texto)
    return texto


def palavras(s):
    return re.findall(r"[\wÀ-ÿ]+(?:[-'][\wÀ-ÿ]+)*", s)


def blocos(texto):
    """Separa em parágrafos de prosa, itens de lista e títulos, com número da linha."""
    prosa, itens, titulos = [], [], []
    atual, inicio = [], 0
    for n, linha in enumerate(texto.splitlines(), 1):
        l = linha.strip()
        if not l or l.startswith(("|", ">")):
            if atual:
                prosa.append((inicio, " ".join(atual)))
                atual = []
            continue
        if re.match(r"#{1,6}\s", l):
            if atual:
                prosa.append((inicio, " ".join(atual)))
                atual = []
            titulos.append((n, l.lstrip("#").strip()))
        elif re.match(r"([-*•]|\d+[.)]|[a-z]\))\s", l):
            if atual:
                prosa.append((inicio, " ".join(atual)))
                atual = []
            itens.append((n, re.sub(r"^([-*•]|\d+[.)]|[a-z]\))\s+", "", l)))
        else:
            if not atual:
                inicio = n
            atual.append(l)
    if atual:
        prosa.append((inicio, " ".join(atual)))
    return prosa, itens, titulos


def frases(paragrafo):
    protegido = re.sub(ABREVIATURAS, lambda m: m.group(0).replace(".", "§"), paragrafo)
    partes = re.split(r"(?<=[.!?…])(?:\*\*)?\s+(?=[\"“(*]*[A-ZÁÉÍÓÚÂÊÔÃÕÇ0-9])", protegido)
    return [p.replace("§", ".").strip() for p in partes if palavras(p)]


def trecho(s, ini, fim, folga=30):
    a, b = max(0, ini - folga), min(len(s), fim + folga)
    return ("…" if a else "") + s[a:b].replace("\n", " ") + ("…" if b < len(s) else "")


def linha_de(texto, pos):
    return texto.count("\n", 0, pos) + 1


def buscar_lista(texto, baixo, lista, categoria, peso, achados, minimo=1):
    for expr, sugestao in lista.items():
        pat = r"(?<![\wÀ-ÿ])" + re.escape(expr) + r"(?![\wÀ-ÿ])"
        ocorr = list(re.finditer(pat, baixo))
        if len(ocorr) < minimo:
            continue
        for m in ocorr:
            achados.append({
                "categoria": categoria, "peso": peso, "linha": linha_de(texto, m.start()),
                "trecho": trecho(texto, m.start(), m.end()),
                "sugestao": f"'{expr}' ({len(ocorr)}x)" + (f" → {sugestao}" if sugestao else " → corte ou reescreva"),
            })


def cv(valores):
    """Coeficiente de variação: desvio-padrão / média."""
    if len(valores) < 2 or statistics.mean(valores) == 0:
        return None
    return statistics.pstdev(valores) / statistics.mean(valores)


def analisar(bruto):
    achados = []

    # Caracteres invisíveis e homóglifos: checagem determinística.
    for ch, nome in INVISIVEIS.items():
        qtd = bruto[1:].count(ch) if ch == "﻿" else bruto.count(ch)
        if qtd:
            achados.append({"categoria": "caractere invisível", "peso": 3, "linha": None,
                            "trecho": nome, "sugestao": f"{qtd}x: remova"})
    for m in re.finditer(r"[a-zA-ZÀ-ÿ]*[" + HOMOGLIFOS + r"][a-zA-ZÀ-ÿ" + HOMOGLIFOS + r"]*", bruto):
        if re.search(r"[a-zA-ZÀ-ÿ]", m.group(0)):
            achados.append({"categoria": "homóglifo", "peso": 3, "linha": linha_de(bruto, m.start()),
                            "trecho": m.group(0), "sugestao": "letra cirílica/grega no meio de palavra: troque pela latina"})

    texto = normalizar(bruto)
    baixo = texto.lower()
    prosa, itens, titulos = blocos(texto)
    todas_frases = [(n, f) for n, p in prosa + itens for f in frases(p)]
    total_palavras = len(palavras(texto))

    # Listas de expressões.
    buscar_lista(texto, baixo, IA_FORTE, "expressão típica de IA", 3, achados)
    # Texto longo tolera mais repetições: 2 até 1.000 palavras, depois 1 a mais a cada 500.
    buscar_lista(texto, baixo, IA_DENSIDADE, "expressão repetida", 1, achados,
                 minimo=max(2, -(-total_palavras // 500)))
    buscar_lista(texto, baixo, BUROCRATES, "burocratês/chavão", 2, achados)
    buscar_lista(texto, baixo, DISCRIMINATORIOS, "termo pejorativo ou excludente", 3, achados)

    # Padrões de frase.
    for categoria, regex, peso, msg in PADROES:
        flags = re.I | re.M if categoria != "pergunta retórica autorrespondida" else re.M
        for m in re.finditer(regex, texto, flags):
            achados.append({"categoria": categoria, "peso": peso, "linha": linha_de(texto, m.start()),
                            "trecho": trecho(texto, m.start(), m.end(), 10), "sugestao": msg})

    # Frases longas (o guia recomenda evitar mais de 20 palavras).
    for n, f in todas_frases:
        qtd = len(palavras(f))
        if qtd > 30:
            achados.append({"categoria": "frase longa", "peso": 2, "linha": n,
                            "trecho": f[:120] + ("…" if len(f) > 120 else ""),
                            "sugestao": f"{qtd} palavras: divida em duas ou mais"})
        elif qtd > 20:
            achados.append({"categoria": "frase longa", "peso": 1, "linha": n,
                            "trecho": f[:120] + ("…" if len(f) > 120 else ""),
                            "sugestao": f"{qtd} palavras: veja se dá para dividir"})

    # Ritmo: frases todas do mesmo tamanho denunciam texto de máquina.
    tam_frases = [len(palavras(f)) for _, f in todas_frases]
    cv_frases = cv(tam_frases)
    if len(tam_frases) >= 8 and cv_frases is not None and cv_frases < 0.35:
        achados.append({"categoria": "ritmo uniforme", "peso": 3, "linha": None,
                        "trecho": f"variação do tamanho das frases = {cv_frases:.2f}",
                        "sugestao": "misture frases curtas (5-8 palavras) com médias (15-22)"})

    tam_par = [len(palavras(p)) for _, p in prosa]
    cv_par = cv(tam_par)
    if len(tam_par) >= 4 and cv_par is not None and cv_par < 0.30:
        achados.append({"categoria": "parágrafos uniformes", "peso": 3, "linha": None,
                        "trecho": f"{len(tam_par)} parágrafos, média {statistics.mean(tam_par):.0f} palavras, variação {cv_par:.2f}",
                        "sugestao": "junte dois parágrafos, deixe outro com uma frase só"})

    # Aberturas repetidas.
    inicios = [palavras(f)[0].lower() for _, f in todas_frases if palavras(f)]
    i = 0
    while i < len(inicios):
        j = i
        while j + 1 < len(inicios) and inicios[j + 1] == inicios[i]:
            j += 1
        if j - i >= 2 and len(inicios[i]) > 2:  # uma sequência conta uma vez só
            achados.append({"categoria": "aberturas repetidas", "peso": 1, "linha": todas_frases[i][0],
                            "trecho": f"{j - i + 1} frases seguidas começam com '{inicios[i]}'",
                            "sugestao": "varie a abertura ou junte as frases (ignore se for tabela ou formulário)"})
        i = j + 1

    # Tipografia de IA.
    for n, t in titulos:
        ps = [p for p in palavras(t) if len(p) > 3]
        if len(ps) >= 3 and sum(p[0].isupper() for p in ps[1:]) >= max(2, 0.6 * (len(ps) - 1)) and not t.isupper():
            achados.append({"categoria": "título em Title Case", "peso": 2, "linha": n, "trecho": t,
                            "sugestao": "em português, maiúscula só na primeira palavra e em nomes próprios"})
    # Vale para item de lista e para linha solta ("**Quando:** sábado"), que é o mesmo vício.
    rotulos = [n for n, l in enumerate(texto.splitlines(), 1)
               if re.match(r"\s*(?:(?:[-*•]|\d+[.)])\s+)?(?:\*\*[^*]{1,40}\*\*\s*:|\*\*[^*]{1,40}:\*\*)", l)]
    if len(rotulos) >= 2:
        achados.append({"categoria": "lista com rótulo em negrito", "peso": 2, "linha": rotulos[0],
                        "trecho": f"{len(rotulos)} linhas no formato '**Rótulo:** frase'",
                        "sugestao": "tire o rótulo ou transforme em frase corrida"})
    negritos = len(re.findall(r"\*\*[^*]+\*\*", texto))
    if total_palavras and negritos / total_palavras * 100 > 2:
        achados.append({"categoria": "negrito demais", "peso": 1, "linha": None,
                        "trecho": f"{negritos} trechos em negrito", "sugestao": "deixe negrito só para o que a pessoa não pode perder (prazo, valor)"})
    travessoes = len(re.findall(r"\s[—–]\s(?![A-Z]{2,}\b)", texto))
    if travessoes >= 3 and travessoes / total_palavras * 1000 > 4:
        achados.append({"categoria": "travessão demais", "peso": 2, "linha": None,
                        "trecho": f"{travessoes} travessões em {total_palavras} palavras",
                        "sugestao": "troque a maioria por vírgula, ponto ou parênteses"})
    emojis = re.findall(r"[\U0001F300-\U0001FAFF☀-➿]", texto)
    if emojis:
        achados.append({"categoria": "emoji", "peso": 1, "linha": None, "trecho": "".join(emojis[:10]),
                        "sugestao": "tire emojis de títulos e listas"})
    aspas = len(re.findall(r"[“”‘’]", texto))
    if aspas:
        achados.append({"categoria": "aspas curvas", "peso": 0, "linha": None, "trecho": f"{aspas} aspas curvas",
                        "sugestao": "em texto digital, prefira aspas retas (só informativo)"})
    exclam = texto.count("!")
    if total_palavras and exclam / total_palavras * 100 > 1:
        achados.append({"categoria": "exclamações", "peso": 1, "linha": None, "trecho": f"{exclam} pontos de exclamação",
                        "sugestao": "corte quase todos"})
    muleta = re.findall(r"(?m)(?:^|[.!?]\s+)[A-ZÁÉÍÓÚ][^:.!?\n]{3,40}:\s+[a-záéíóúâêôãõç]", texto)
    if len(muleta) >= 3:
        achados.append({"categoria": "dois-pontos como muleta", "peso": 1, "linha": None,
                        "trecho": f"{len(muleta)} frases no formato 'O problema é simples: …'",
                        "sugestao": "use 'porque', 'que', 'quando' ou reescreva"})

    # Siglas sem nome por extenso na primeira vez.
    vistas = set()
    for m in re.finditer(r"(?<![\wÀ-ÿ])[A-Z][A-Za-z]?[A-Z]{1,5}s?(?![\wÀ-ÿ])", texto):
        sigla = m.group(0).rstrip("s") if m.group(0).endswith("s") and m.group(0)[:-1].isupper() else m.group(0)
        if sigla in vistas or sigla in SIGLAS_COMUNS or not sum(c.isupper() for c in sigla) >= 2:
            continue
        vistas.add(sigla)
        antes, depois = texto[max(0, m.start() - 3):m.start()], texto[m.end():m.end() + 2]
        if re.search(r"[(–—-]\s?$", antes) or depois.startswith(" (") or depois.startswith("("):
            continue
        if texto[max(0, m.start() - 2):m.start()].endswith("# ") or m.group(0).isupper() and len(m.group(0)) > 5:
            continue
        # Palavra em caixa alta (título, nome em referência ABNT) não é sigla.
        ini_linha = texto.rfind("\n", 0, m.start()) + 1
        fim_linha = texto.find("\n", m.end())
        linha = texto[ini_linha:fim_linha if fim_linha != -1 else len(texto)]
        letras = [c for c in linha if c.isalpha()]
        vizinhas = re.findall(r"[\wÀ-ÿ]+", texto[max(0, m.start() - 25):m.start()])[-1:] + \
            re.findall(r"[\wÀ-ÿ]+", texto[m.end():m.end() + 25])[:1]
        if (sum(c.isupper() for c in letras) >= 0.6 * len(letras)
                or any(len(v) >= 2 and v.isupper() for v in vizinhas)
                or re.match(r",\s+[A-ZÁÉÍÓÚ][a-zà-ÿ]", texto[m.end():m.end() + 4])):
            continue
        achados.append({"categoria": "sigla sem explicação", "peso": 1, "linha": linha_de(texto, m.start()),
                        "trecho": trecho(texto, m.start(), m.end(), 20),
                        "sugestao": f"na primeira vez, escreva o nome completo: 'Nome por extenso – {sigla}'"})

    pontos = sum(a["peso"] for a in achados)
    # shortcut: piso de 100 palavras para texto curto não ser punido por 1 ou 2 achados leves.
    densidade = pontos / max(total_palavras, 100) * 100
    if densidade < 3:
        veredito = "bom: revise só os achados de peso 3"
    elif densidade < 8:
        veredito = "revisar: há padrões acumulados"
    else:
        veredito = "reescrever: o texto está carregado de padrões"
    return {
        "palavras": total_palavras,
        "frases": len(tam_frases),
        "media_palavras_por_frase": round(statistics.mean(tam_frases), 1) if tam_frases else 0,
        "variacao_frases": round(cv_frases, 2) if cv_frases is not None else None,
        "paragrafos": len(tam_par),
        "variacao_paragrafos": round(cv_par, 2) if cv_par is not None else None,
        "pontos": pontos,
        "pontos_por_100_palavras": round(densidade, 1),
        "veredito": veredito,
        "achados": sorted(achados, key=lambda a: (-a["peso"], a["categoria"], a["linha"] or 0)),
    }


def imprimir(r):
    print(f"Palavras: {r['palavras']} | Frases: {r['frases']} | Média por frase: {r['media_palavras_por_frase']}"
          f" | Variação das frases: {r['variacao_frases']} | Parágrafos: {r['paragrafos']}"
          f" | Variação dos parágrafos: {r['variacao_paragrafos']}")
    print(f"Pontos: {r['pontos']} ({r['pontos_por_100_palavras']} por 100 palavras) → {r['veredito']}\n")
    if not r["achados"]:
        print("Nenhum padrão encontrado. Ainda assim, leia em voz alta.")
        return
    categoria = None
    for a in r["achados"]:
        if a["categoria"] != categoria:
            categoria = a["categoria"]
            print(f"## {categoria}")
        onde = f"linha {a['linha']}: " if a["linha"] else ""
        print(f"  [{a['peso']}] {onde}{a['trecho']}\n      {a['sugestao']}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("arquivo", help="arquivo de texto ou markdown; '-' lê da entrada padrão")
    ap.add_argument("--json", action="store_true", help="saída em JSON")
    ap.add_argument("--limite", type=float, metavar="N",
                    help="sai com código 1 se os pontos por 100 palavras forem N ou mais (para CI e pre-commit)")
    args = ap.parse_args()
    for fluxo in (sys.stdout, sys.stderr):
        if hasattr(fluxo, "reconfigure"):
            fluxo.reconfigure(encoding="utf-8")
    try:
        if args.arquivo == "-":
            sys.stdin.reconfigure(encoding="utf-8")
            texto = sys.stdin.read()
        else:
            with open(args.arquivo, encoding="utf-8-sig") as f:
                texto = f.read()
    except OSError as e:
        print(f"Não consegui abrir '{args.arquivo}': {e.strerror}", file=sys.stderr)
        sys.exit(2)
    except UnicodeDecodeError:
        print(f"'{args.arquivo}' não está em UTF-8. Salve o arquivo como UTF-8 e tente de novo.", file=sys.stderr)
        sys.exit(2)
    texto = unicodedata.normalize("NFC", texto)
    r = analisar(texto)
    if args.json:
        print(json.dumps(r, ensure_ascii=False, indent=2))
    else:
        imprimir(r)
    if args.limite is not None and r["pontos_por_100_palavras"] >= args.limite:
        sys.exit(1)


if __name__ == "__main__":
    main()
