# ============================================================
# UTILIDADES
# ============================================================

def numero(dados, chave, padrao=None):
    """
    Obtém um número do dicionário com segurança.
    """

    valor = dados.get(chave, padrao)

    if valor is None:
        return padrao

    try:
        valor = float(valor)
    except (TypeError, ValueError):
        return padrao

    return valor


def limitar(valor, minimo=0, maximo=100):
    """
    Mantém um valor dentro de um intervalo.
    """

    return max(
        minimo,
        min(maximo, valor)
    )


# ============================================================
# TENDÊNCIA
# ============================================================

def score_tendencia(dados):
    """
    Avalia a posição do preço em relação às médias móveis.

    Máximo: 30 pontos.
    """

    preco = numero(dados, "preco")
    sma_20 = numero(dados, "sma_20")
    sma_50 = numero(dados, "sma_50")
    sma_200 = numero(dados, "sma_200")

    score = 0

    if preco is None:
        return 0

    # Preço acima da média de 20 dias
    if sma_20 is not None and preco > sma_20:
        score += 7

    # Preço acima da média de 50 dias
    if sma_50 is not None and preco > sma_50:
        score += 8

    # Preço acima da média de 200 dias
    if sma_200 is not None and preco > sma_200:
        score += 10

    # Estrutura das médias
    if (
        sma_20 is not None
        and sma_50 is not None
        and sma_20 > sma_50
    ):
        score += 5

    return limitar(score, 0, 30)


# ============================================================
# MOMENTUM
# ============================================================

def score_momentum(dados):
    """
    Avalia momentum usando RSI e MACD.

    Máximo: 20 pontos.
    """

    rsi = numero(dados, "rsi")
    macd = numero(dados, "macd")
    macd_signal = numero(
        dados,
        "macd_signal"
    )

    score = 0

    # --------------------------------------------------------
    # RSI
    # --------------------------------------------------------

    if rsi is not None:

        # Região intermediária
        if 40 <= rsi <= 60:
            score += 8

        # Momentum moderado
        elif 30 <= rsi < 40:
            score += 5

        elif 60 < rsi <= 70:
            score += 5

        # Evitamos premiar extremos
        elif 20 <= rsi < 30:
            score += 2

        elif 70 < rsi <= 80:
            score += 2

    # --------------------------------------------------------
    # MACD
    # --------------------------------------------------------

    if (
        macd is not None
        and macd_signal is not None
    ):

        if macd > macd_signal:
            score += 7

        else:
            score += 2

    return limitar(score, 0, 20)


# ============================================================
# VOLUME
# ============================================================

def score_volume(dados):
    """
    Avalia o volume relativo.

    Máximo: 10 pontos.
    """

    volume_relativo = numero(
        dados,
        "volume_relativo"
    )

    if volume_relativo is None:
        return 5

    if volume_relativo >= 2:
        return 10

    if volume_relativo >= 1.5:
        return 8

    if volume_relativo >= 1:
        return 6

    if volume_relativo >= 0.7:
        return 3

    return 0


# ============================================================
# VALUATION
# ============================================================

def score_valuation(dados):
    """
    Avalia P/L.

    Máximo: 15 pontos.

    Atenção:
    P/L baixo não significa automaticamente que uma empresa
    esteja barata. O indicador deve ser analisado junto com
    crescimento, setor, dívida e outros fundamentos.
    """

    pl = numero(
        dados,
        "pl"
    )

    if pl is None:
        return 7

    if pl <= 0:
        return 0

    if pl <= 5:
        return 15

    if pl <= 8:
        return 13

    if pl <= 12:
        return 10

    if pl <= 18:
        return 6

    if pl <= 25:
        return 3

    return 0


# ============================================================
# RENTABILIDADE
# ============================================================

def score_roe(dados):
    """
    Avalia ROE.

    Máximo: 15 pontos.
    """

    roe = numero(
        dados,
        "roe"
    )

    if roe is None:
        return 7

    if roe >= 30:
        return 15

    if roe >= 25:
        return 13

    if roe >= 20:
        return 11

    if roe >= 15:
        return 8

    if roe >= 10:
        return 4

    return 0


# ============================================================
# DIVIDENDOS
# ============================================================

def score_dividendos(dados):
    """
    Avalia Dividend Yield.

    Máximo: 10 pontos.

    O objetivo aqui é apenas considerar o indicador.
    Dividend Yield elevado isoladamente não significa
    que o investimento seja melhor.
    """

    dividend_yield = numero(
        dados,
        "dividend_yield"
    )

    if dividend_yield is None:
        return 5

    if dividend_yield >= 10:
        return 10

    if dividend_yield >= 7:
        return 9

    if dividend_yield >= 5:
        return 7

    if dividend_yield >= 3:
        return 5

    if dividend_yield >= 1:
        return 3

    return 0


# ============================================================
# RETORNO
# ============================================================

def score_retorno(dados):
    """
    Avalia retornos recentes.

    Máximo: 10 pontos.

    Usamos isso como contexto de momentum, não como previsão.
    """

    retorno_20 = numero(
        dados,
        "retorno_20d"
    )

    retorno_60 = numero(
        dados,
        "retorno_60d"
    )

    score = 0

    if retorno_20 is not None:

        if retorno_20 > 0.10:
            score += 5

        elif retorno_20 > 0.03:
            score += 4

        elif retorno_20 > 0:
            score += 2

    if retorno_60 is not None:

        if retorno_60 > 0.15:
            score += 5

        elif retorno_60 > 0.05:
            score += 4

        elif retorno_60 > 0:
            score += 2

    return limitar(score, 0, 10)


# ============================================================
# PENALIDADE DE VOLATILIDADE
# ============================================================

def penalidade_volatilidade(dados):
    """
    Aplica uma pequena penalidade para volatilidade muito alta.

    Máximo: -10 pontos.
    """

    volatilidade = numero(
        dados,
        "volatilidade"
    )

    if volatilidade is None:
        return 0

    # Volatilidade anualizada.
    if volatilidade > 0.80:
        return -10

    if volatilidade > 0.60:
        return -7

    if volatilidade > 0.45:
        return -4

    if volatilidade > 0.30:
        return -2

    return 0


# ============================================================
# SCORE COMPLETO
# ============================================================

def calcular_score(dados):
    """
    Calcula o score quantitativo final.

    Componentes:

        Tendência       30
        Momentum        20
        Volume          10
        Valuation       15
        ROE             15
        Dividendos      10
        Retorno         10

    Total bruto possível: 110.

    Depois normalizamos para 0-100.

    A volatilidade pode gerar uma penalidade adicional.
    """

    tendencia = score_tendencia(dados)

    momentum = score_momentum(dados)

    volume = score_volume(dados)

    valuation = score_valuation(dados)

    roe = score_roe(dados)

    dividendos = score_dividendos(dados)

    retorno = score_retorno(dados)

    penalidade = penalidade_volatilidade(
        dados
    )

    # Soma dos componentes
    bruto = (
        tendencia
        + momentum
        + volume
        + valuation
        + roe
        + dividendos
        + retorno
        + penalidade
    )

    # O máximo positivo dos componentes é 110.
    score = (bruto / 110) * 100

    return round(
        limitar(score),
        2
    )


# ============================================================
# DETALHAMENTO DO SCORE
# ============================================================

def detalhar_score(dados):
    """
    Retorna todos os componentes do score.

    Isso será utilizado posteriormente no dashboard.
    """

    tendencia = score_tendencia(dados)
    momentum = score_momentum(dados)
    volume = score_volume(dados)
    valuation = score_valuation(dados)
    roe = score_roe(dados)
    dividendos = score_dividendos(dados)
    retorno = score_retorno(dados)
    penalidade = penalidade_volatilidade(
        dados
    )

    bruto = (
        tendencia
        + momentum
        + volume
        + valuation
        + roe
        + dividendos
        + retorno
        + penalidade
    )

    score = round(
        limitar((bruto / 110) * 100),
        2
    )

    return {
        "score": score,

        "componentes": {
            "tendencia": tendencia,
            "momentum": momentum,
            "volume": volume,
            "valuation": valuation,
            "roe": roe,
            "dividendos": dividendos,
            "retorno": retorno,
            "penalidade_volatilidade": penalidade,
        },

        "score_bruto": round(
            bruto,
            2
        ),
    }


# ============================================================
# CLASSIFICAÇÃO
# ============================================================

def classificar_score(score):
    """
    Classifica apenas para organização visual.

    Não representa recomendação de investimento.
    """

    if score >= 75:
        return "ALTA PRIORIDADE DE ESTUDO"

    if score >= 60:
        return "PRIORIDADE DE ESTUDO"

    if score >= 45:
        return "ACOMPANHAR"

    return "BAIXA PRIORIDADE"


# ============================================================
# RANKING
# ============================================================

def criar_ranking(dados_acoes):
    """
    Recebe:

        {
            "PETR4": {...},
            "VALE3": {...},
            ...
        }

    Retorna uma lista ordenada pelo score.
    """

    ranking = []

    for ticker, dados in dados_acoes.items():

        detalhes = detalhar_score(
            dados
        )

        ranking.append({
            "ticker": ticker,
            "score": detalhes["score"],
            "classificacao": classificar_score(
                detalhes["score"]
            ),
            "componentes": detalhes[
                "componentes"
            ],
            "indicadores": dados,
        })

    # Maior score primeiro
    ranking.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    return ranking


# ============================================================
# TOP CANDIDATAS
# ============================================================

def selecionar_candidatas(
    dados_acoes,
    quantidade=10,
):
    """
    Retorna somente as principais candidatas.

    IMPORTANTE:
    Isso não significa que sejam os "melhores investimentos".
    Significa apenas que receberam maior score dentro
    dos critérios quantitativos definidos.
    """

    ranking = criar_ranking(
        dados_acoes
    )

    return ranking[:quantidade]


# ============================================================
# TESTE
# ============================================================

if __name__ == "__main__":

    dados_teste = {

        "PETR4": {
            "preco": 38.52,
            "sma_20": 39.10,
            "sma_50": 37.90,
            "sma_200": 35.20,
            "rsi": 42.1,
            "macd": 0.8,
            "macd_signal": 0.5,
            "volume_relativo": 1.34,
            "pl": 6.8,
            "roe": 24.3,
            "dividend_yield": 8.2,
            "retorno_20d": 0.04,
            "retorno_60d": 0.08,
            "volatilidade": 0.32,
        },

        "VALE3": {
            "preco": 64.30,
            "sma_20": 63.80,
            "sma_50": 65.20,
            "sma_200": 61.40,
            "rsi": 51.7,
            "macd": 0.4,
            "macd_signal": 0.6,
            "volume_relativo": 1.08,
            "pl": 5.9,
            "roe": 18.7,
            "dividend_yield": 6.4,
            "retorno_20d": 0.02,
            "retorno_60d": 0.06,
            "volatilidade": 0.28,
        },

        "ITUB4": {
            "preco": 39.20,
            "sma_20": 38.60,
            "sma_50": 37.90,
            "sma_200": 35.80,
            "rsi": 57.4,
            "macd": 1.2,
            "macd_signal": 0.8,
            "volume_relativo": 1.12,
            "pl": 8.1,
            "roe": 21.5,
            "dividend_yield": 5.7,
            "retorno_20d": 0.06,
            "retorno_60d": 0.12,
            "volatilidade": 0.22,
        },
    }

    print()
    print("=" * 70)
    print("📊 TESTE DO SISTEMA DE SCORING")
    print("=" * 70)
    print()

    ranking = criar_ranking(
        dados_teste
    )

    for posicao, acao in enumerate(
        ranking,
        start=1
    ):

        print(
            f"{posicao:>2}. "
            f"{acao['ticker']:<7} "
            f"Score: {acao['score']:>5.1f} "
            f"| {acao['classificacao']}"
        )

        print(
            f"    Tendência:   "
            f"{acao['componentes']['tendencia']:>2}"
        )

        print(
            f"    Momentum:    "
            f"{acao['componentes']['momentum']:>2}"
        )

        print(
            f"    Volume:      "
            f"{acao['componentes']['volume']:>2}"
        )

        print(
            f"    Valuation:   "
            f"{acao['componentes']['valuation']:>2}"
        )

        print(
            f"    ROE:         "
            f"{acao['componentes']['roe']:>2}"
        )

        print(
            f"    Dividendos:  "
            f"{acao['componentes']['dividendos']:>2}"
        )

        print(
            f"    Retorno:     "
            f"{acao['componentes']['retorno']:>2}"
        )

        print(
            f"    Volatilidade:"
            f" {acao['componentes']['penalidade_volatilidade']:>3}"
        )

        print()
