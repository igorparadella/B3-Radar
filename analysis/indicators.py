
import pandas as pd
import numpy as np

from ta.momentum import RSIIndicator
from ta.trend import (
    SMAIndicator,
    EMAIndicator,
    MACD,
)
from ta.volatility import (
    BollingerBands,
    AverageTrueRange,
)


# ============================================================
# UTILIDADES
# ============================================================

def validar_dataframe(df):
    """
    Verifica se o DataFrame possui os dados necessários.
    """

    if df is None or df.empty:
        raise ValueError(
            "O DataFrame está vazio."
        )

    colunas_obrigatorias = [
        "Close",
        "High",
        "Low",
        "Volume",
    ]

    colunas_faltando = [
        coluna
        for coluna in colunas_obrigatorias
        if coluna not in df.columns
    ]

    if colunas_faltando:
        raise ValueError(
            "Colunas faltando: "
            + ", ".join(colunas_faltando)
        )


# ============================================================
# MÉDIAS MÓVEIS
# ============================================================

def calcular_medias_moveis(
    df,
    curta=20,
    media=50,
    longa=200,
):
    """
    Calcula médias móveis simples (SMA).
    """

    df = df.copy()

    df[f"SMA_{curta}"] = SMAIndicator(
        close=df["Close"],
        window=curta,
    ).sma_indicator()

    df[f"SMA_{media}"] = SMAIndicator(
        close=df["Close"],
        window=media,
    ).sma_indicator()

    df[f"SMA_{longa}"] = SMAIndicator(
        close=df["Close"],
        window=longa,
    ).sma_indicator()

    return df


# ============================================================
# RSI
# ============================================================

def calcular_rsi(df, periodo=14):
    """
    Calcula o RSI (Relative Strength Index).
    """

    df = df.copy()

    indicador = RSIIndicator(
        close=df["Close"],
        window=periodo,
    )

    df["RSI"] = indicador.rsi()

    return df


# ============================================================
# MACD
# ============================================================

def calcular_macd(df):
    """
    Calcula MACD, linha de sinal e diferença.
    """

    df = df.copy()

    indicador = MACD(
        close=df["Close"],
        window_slow=26,
        window_fast=12,
        window_sign=9,
    )

    df["MACD"] = indicador.macd()

    df["MACD_SIGNAL"] = (
        indicador.macd_signal()
    )

    df["MACD_DIFF"] = (
        indicador.macd_diff()
    )

    return df


# ============================================================
# BANDAS DE BOLLINGER
# ============================================================

def calcular_bollinger(df, periodo=20):
    """
    Calcula as Bandas de Bollinger.
    """

    df = df.copy()

    indicador = BollingerBands(
        close=df["Close"],
        window=periodo,
        window_dev=2,
    )

    df["BB_HIGH"] = (
        indicador.bollinger_hband()
    )

    df["BB_MIDDLE"] = (
        indicador.bollinger_mavg()
    )

    df["BB_LOW"] = (
        indicador.bollinger_lband()
    )

    df["BB_PERCENT"] = (
        indicador.bollinger_pband()
    )

    return df


# ============================================================
# ATR
# ============================================================

def calcular_atr(df, periodo=14):
    """
    Calcula o Average True Range.

    O ATR é utilizado como medida de volatilidade.
    """

    df = df.copy()

    indicador = AverageTrueRange(
        high=df["High"],
        low=df["Low"],
        close=df["Close"],
        window=periodo,
    )

    df["ATR"] = indicador.average_true_range()

    return df


# ============================================================
# RETORNOS
# ============================================================

def calcular_retornos(df):
    """
    Calcula retornos diários e acumulados.
    """

    df = df.copy()

    df["RETORNO_DIARIO"] = (
        df["Close"].pct_change()
    )

    df["RETORNO_20D"] = (
        df["Close"].pct_change(20)
    )

    df["RETORNO_60D"] = (
        df["Close"].pct_change(60)
    )

    df["RETORNO_252D"] = (
        df["Close"].pct_change(252)
    )

    return df


# ============================================================
# VOLATILIDADE
# ============================================================

def calcular_volatilidade(df, periodo=20):
    """
    Calcula a volatilidade anualizada baseada
    nos retornos diários.
    """

    df = df.copy()

    retorno = df["Close"].pct_change()

    df["VOLATILIDADE"] = (
        retorno
        .rolling(periodo)
        .std()
        * np.sqrt(252)
    )

    return df


# ============================================================
# VOLUME
# ============================================================

def calcular_volume(df, periodo=20):
    """
    Calcula volume médio e volume relativo.

    Volume relativo:
        volume atual / volume médio
    """

    df = df.copy()

    df["VOLUME_MEDIO"] = (
        df["Volume"]
        .rolling(periodo)
        .mean()
    )

    df["VOLUME_RELATIVO"] = (
        df["Volume"]
        / df["VOLUME_MEDIO"]
    )

    return df


# ============================================================
# DRAWDOWN
# ============================================================

def calcular_drawdown(df):
    """
    Calcula a distância do preço atual em relação
    ao maior preço histórico observado até aquele momento.
    """

    df = df.copy()

    maximo_acumulado = (
        df["Close"]
        .cummax()
    )

    df["DRAWDOWN"] = (
        df["Close"]
        / maximo_acumulado
        - 1
    )

    return df


# ============================================================
# TODOS OS INDICADORES
# ============================================================

def calcular_indicadores(df):
    """
    Executa todos os indicadores do sistema.
    """

    validar_dataframe(df)

    df = df.copy()

    df = calcular_medias_moveis(df)

    df = calcular_rsi(df)

    df = calcular_macd(df)

    df = calcular_bollinger(df)

    df = calcular_atr(df)

    df = calcular_retornos(df)

    df = calcular_volatilidade(df)

    df = calcular_volume(df)

    df = calcular_drawdown(df)

    return df


# ============================================================
# RESUMO DO ÚLTIMO DIA
# ============================================================

def gerar_resumo(df):
    """
    Pega somente o último registro dos indicadores
    e transforma em um dicionário simples.

    Esse será o formato que posteriormente enviaremos
    para o sistema de scoring e, depois, para a IA.
    """

    if df is None or df.empty:
        raise ValueError(
            "Não existem dados para gerar o resumo."
        )

    ultimo = df.iloc[-1]

    def numero(coluna, casas=2):
        """
        Retorna um número arredondado ou None.
        """

        valor = ultimo.get(coluna)

        if pd.isna(valor):
            return None

        return round(
            float(valor),
            casas,
        )

    resumo = {
        # ----------------------------------------------------
        # Preço
        # ----------------------------------------------------

        "preco": numero("Close"),

        # ----------------------------------------------------
        # Médias móveis
        # ----------------------------------------------------

        "sma_20": numero("SMA_20"),
        "sma_50": numero("SMA_50"),
        "sma_200": numero("SMA_200"),

        # ----------------------------------------------------
        # Momentum
        # ----------------------------------------------------

        "rsi": numero("RSI"),

        "macd": numero("MACD"),
        "macd_signal": numero("MACD_SIGNAL"),
        "macd_diff": numero("MACD_DIFF"),

        # ----------------------------------------------------
        # Bollinger
        # ----------------------------------------------------

        "bb_high": numero("BB_HIGH"),
        "bb_middle": numero("BB_MIDDLE"),
        "bb_low": numero("BB_LOW"),
        "bb_percent": numero("BB_PERCENT"),

        # ----------------------------------------------------
        # Volatilidade
        # ----------------------------------------------------

        "atr": numero("ATR"),
        "volatilidade": numero(
            "VOLATILIDADE",
            4,
        ),

        # ----------------------------------------------------
        # Retornos
        # ----------------------------------------------------

        "retorno_20d": numero(
            "RETORNO_20D",
            4,
        ),

        "retorno_60d": numero(
            "RETORNO_60D",
            4,
        ),

        "retorno_252d": numero(
            "RETORNO_252D",
            4,
        ),

        # ----------------------------------------------------
        # Volume
        # ----------------------------------------------------

        "volume": numero("Volume", 0),

        "volume_medio": numero(
            "VOLUME_MEDIO",
            0,
        ),

        "volume_relativo": numero(
            "VOLUME_RELATIVO",
            2,
        ),

        # ----------------------------------------------------
        # Drawdown
        # ----------------------------------------------------

        "drawdown": numero(
            "DRAWDOWN",
            4,
        ),
    }

    return resumo


# ============================================================
# TESTE
# ============================================================

if __name__ == "__main__":

    print(
        "Módulo de indicadores carregado com sucesso."
    )

    print()
    print(
        "Este arquivo será utilizado pelo pipeline"
    )

    print(
        "principal para analisar os dados históricos."
    )
