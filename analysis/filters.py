import pandas as pd

from config import (
    SCORE_MINIMO,
    PL_MAXIMO,
    ROE_MINIMO,
    DIVIDEND_YIELD_MINIMO,
    VOLUME_RELATIVO_MINIMO,
)


# ============================================================
# UTILIDADES
# ============================================================

def valor_valido(valor):
    """
    Verifica se um valor existe e não é NaN.
    """

    if valor is None:
        return False

    try:
        return not pd.isna(valor)
    except (TypeError, ValueError):
        return False


def obter_valor(dados, chave, padrao=None):
    """
    Obtém um valor do dicionário com segurança.
    """

    valor = dados.get(chave, padrao)

    if not valor_valido(valor):
        return padrao

    return valor


# ============================================================
# FILTRO DE DADOS
# ============================================================

def possui_dados_minimos(dados):
    """
    Verifica se a ação possui os principais indicadores
    necessários para análise.

    Não exigimos absolutamente todos os indicadores porque
    alguns podem não estar disponíveis dependendo da fonte.
    """

    campos_obrigatorios = [
        "preco",
        "rsi",
        "sma_20",
        "sma_50",
    ]

    for campo in campos_obrigatorios:

        if not valor_valido(
            dados.get(campo)
        ):
            return False

    return True


# ============================================================
# FILTRO DE LIQUIDEZ
# ============================================================

def verificar_liquidez(dados):
    """
    Verifica se existe atividade suficiente de negociação.

    O volume relativo não deve ser utilizado sozinho como
    medida absoluta de liquidez. Aqui ele funciona apenas
    como um filtro inicial.
    """

    volume_relativo = obter_valor(
        dados,
        "volume_relativo",
    )

    if volume_relativo is None:
        return True

    return volume_relativo > 0


# ============================================================
# FILTRO DE RSI
# ============================================================

def verificar_rsi(dados):
    """
    Remove situações extremas de RSI.

    Não significa que RSI extremo seja necessariamente ruim.
    O objetivo é evitar que o radar trate situações extremas
    como candidatas normais.
    """

    rsi = obter_valor(
        dados,
        "rsi",
    )

    if rsi is None:
        return False

    return 20 <= rsi <= 80


# ============================================================
# FILTRO DE TENDÊNCIA
# ============================================================

def verificar_tendencia(dados):
    """
    Verifica a posição do preço em relação às médias móveis.

    Aqui não exigimos que todos os sinais sejam positivos.
    O objetivo é identificar a estrutura da tendência.
    """

    preco = obter_valor(
        dados,
        "preco",
    )

    sma_20 = obter_valor(
        dados,
        "sma_20",
    )

    sma_50 = obter_valor(
        dados,
        "sma_50",
    )

    if (
        preco is None
        or sma_20 is None
        or sma_50 is None
    ):
        return False

    # Aceitamos tanto tendência positiva quanto negativa
    # nesta etapa. O scoring será responsável por diferenciar.
    return preco > 0 and sma_20 > 0 and sma_50 > 0


# ============================================================
# FILTRO DE VALUATION
# ============================================================

def verificar_valuation(dados):
    """
    Faz um filtro simples de P/L.

    Atenção:
    P/L baixo não significa automaticamente que uma empresa
    está barata. Pode existir um motivo fundamental para isso.
    """

    pl = obter_valor(
        dados,
        "pl",
    )

    if pl is None:
        return True

    # P/L negativo normalmente significa prejuízo.
    if pl <= 0:
        return False

    return pl <= PL_MAXIMO


# ============================================================
# FILTRO DE RENTABILIDADE
# ============================================================

def verificar_roe(dados):
    """
    Verifica o ROE quando disponível.

    Empresas com ROE maior podem apresentar maior eficiência
    na utilização do patrimônio, mas ROE isoladamente não
    determina a qualidade de uma empresa.
    """

    roe = obter_valor(
        dados,
        "roe",
    )

    if roe is None:
        return True

    return roe >= ROE_MINIMO


# ============================================================
# FILTRO DE DIVIDENDOS
# ============================================================

def verificar_dividend_yield(dados):
    """
    Verifica Dividend Yield quando disponível.

    Este filtro é opcional e não elimina empresas que não
    possuem Dividend Yield disponível.
    """

    dividend_yield = obter_valor(
        dados,
        "dividend_yield",
    )

    if dividend_yield is None:
        return True

    # Apenas impede valores negativos.
    return dividend_yield >= 0


# ============================================================
# FILTRO PRINCIPAL
# ============================================================

def aplicar_filtros(dados):
    """
    Aplica todos os filtros básicos a uma ação.

    Retorna:
        True  -> passou
        False -> não passou
    """

    if not possui_dados_minimos(dados):
        return False

    if not verificar_liquidez(dados):
        return False

    if not verificar_rsi(dados):
        return False

    if not verificar_tendencia(dados):
        return False

    if not verificar_valuation(dados):
        return False

    if not verificar_roe(dados):
        return False

    if not verificar_dividend_yield(dados):
        return False

    return True


# ============================================================
# FILTRAR TODAS AS AÇÕES
# ============================================================

def filtrar_acoes(dados_acoes):
    """
    Recebe um dicionário contendo várias ações e retorna
    somente aquelas que passaram pelos filtros.

    Exemplo:

        {
            "PETR4": {...},
            "VALE3": {...},
            "ITUB4": {...}
        }

    Retorna:

        {
            "PETR4": {...},
            "ITUB4": {...}
        }
    """

    aprovadas = {}

    for ticker, dados in dados_acoes.items():

        try:

            passou = aplicar_filtros(
                dados
            )

            if passou:
                aprovadas[ticker] = dados

        except Exception as erro:

            print(
                f"⚠️ Erro ao analisar {ticker}: "
                f"{erro}"
            )

    return aprovadas


# ============================================================
# RELATÓRIO DOS FILTROS
# ============================================================

def explicar_filtros(dados):
    """
    Retorna uma explicação mostrando quais filtros
    foram aprovados ou reprovados.

    Isso será útil posteriormente no dashboard.
    """

    resultado = {
        "dados_minimos": possui_dados_minimos(
            dados
        ),

        "liquidez": verificar_liquidez(
