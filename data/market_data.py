import os
import time
from datetime import datetime

import pandas as pd
import yfinance as yf


# ============================================================
# CONFIGURAÇÕES
# ============================================================

PERIODO_PADRAO = "2y"

INTERVALO_PADRAO = "1d"

# Pequena pausa entre requisições para evitar fazer muitas
# requisições seguidas.
ESPERA_ENTRE_REQUISICOES = 0.5


# ============================================================
# CONVERSÃO DE TICKER
# ============================================================

def ticker_b3_para_yahoo(ticker):
    """
    Converte um ticker da B3 para o formato utilizado
    pelo Yahoo Finance.

    Exemplo:

        PETR4 -> PETR4.SA
    """

    ticker = ticker.strip().upper()

    if not ticker:
        raise ValueError(
            "Ticker não pode estar vazio."
        )

    if not ticker.endswith(".SA"):
        ticker += ".SA"

    return ticker


# ============================================================
# DOWNLOAD DE UMA AÇÃO
# ============================================================

def baixar_historico(
    ticker,
    periodo=PERIODO_PADRAO,
    intervalo=INTERVALO_PADRAO,
):
    """
    Baixa o histórico de uma ação.

    Retorna um DataFrame com:

        Open
        High
        Low
        Close
        Volume
    """

    ticker_yahoo = ticker_b3_para_yahoo(
        ticker
    )

    print(
        f"📥 Baixando dados de {ticker.upper()}..."
    )

    try:

        dados = yf.download(
            ticker_yahoo,
            period=periodo,
            interval=intervalo,
            auto_adjust=True,
            progress=False,
            threads=False,
        )

    except Exception as erro:

        print(
            f"❌ Erro ao baixar {ticker}: {erro}"
        )

        return None

    if dados is None or dados.empty:

        print(
            f"⚠️ Nenhum dado encontrado para {ticker}."
        )

        return None

    # --------------------------------------------------------
    # O Yahoo pode retornar MultiIndex dependendo da versão
    # --------------------------------------------------------

    if isinstance(dados.columns, pd.MultiIndex):

        try:

            dados.columns = (
                dados.columns
                .get_level_values(0)
            )

        except Exception:

            dados.columns = [
                coluna[0]
                for coluna in dados.columns
            ]

    # --------------------------------------------------------
    # Mantemos apenas as colunas necessárias
    # --------------------------------------------------------

    colunas = [
        "Open",
        "High",
        "Low",
        "Close",
        "Volume",
    ]

    colunas_existentes = [
        coluna
        for coluna in colunas
        if coluna in dados.columns
    ]

    dados = dados[
        colunas_existentes
    ].copy()

    # --------------------------------------------------------
    # Garantir valores numéricos
    # --------------------------------------------------------

    for coluna in colunas_existentes:

        dados[coluna] = pd.to_numeric(
            dados[coluna],
            errors="coerce",
        )

    # --------------------------------------------------------
    # Remover linhas inválidas
    # --------------------------------------------------------

    dados = dados.dropna(
        subset=["Close"]
    )

    # Volume pode eventualmente estar ausente ou zerado.
    if "Volume" in dados.columns:

        dados["Volume"] = (
            dados["Volume"]
            .fillna(0)
        )

    # --------------------------------------------------------
    # Ordenar cronologicamente
    # --------------------------------------------------------

    dados = dados.sort_index()

    print(
        f"   ✓ {len(dados)} pregões encontrados."
    )

    return dados


# ============================================================
# BAIXAR VÁRIAS AÇÕES
# ============================================================

def baixar_acoes(
    tickers,
    periodo=PERIODO_PADRAO,
    intervalo=INTERVALO_PADRAO,
):
    """
    Baixa os dados de várias ações.

    Retorna:

        {
            "PETR4": DataFrame,
            "VALE3": DataFrame,
            ...
        }
    """

    resultados = {}

    for ticker in tickers:

        ticker = ticker.strip().upper()

        dados = baixar_historico(
            ticker,
            periodo=periodo,
            intervalo=intervalo,
        )

        if dados is not None and not dados.empty:

            resultados[ticker] = dados

        time.sleep(
            ESPERA_ENTRE_REQUISICOES
        )

    return resultados


# ============================================================
# ÚLTIMO PREÇO
# ============================================================

def obter_ultimo_preco(dados):
    """
    Retorna o último preço disponível.
    """

    if dados is None or dados.empty:
        return None

    if "Close" not in dados.columns:
        return None

    preco = dados["Close"].iloc[-1]

    if pd.isna(preco):
        return None

    return round(
        float(preco),
        2,
    )


# ============================================================
# ÚLTIMA DATA
# ============================================================

def obter_ultima_data(dados):
    """
    Retorna a data do último pregão disponível.
    """

    if dados is None or dados.empty:
        return None

    data = dados.index[-1]

    try:
        return data.strftime(
            "%Y-%m-%d"
        )

    except AttributeError:

        return str(data)


# ============================================================
# INFORMAÇÕES BÁSICAS
# ============================================================

def obter_informacoes_basicas(
    ticker,
    dados,
):
    """
    Gera informações básicas da ação.
    """

    return {
        "ticker": ticker,

        "preco": obter_ultimo_preco(
            dados
        ),

        "data": obter_ultima_data(
            dados
        ),

        "quantidade_registros": (
            len(dados)
            if dados is not None
            else 0
        ),
    }


# ============================================================
# SALVAR HISTÓRICO EM CSV
# ============================================================

def salvar_csv(
    ticker,
    dados,
    diretorio="data/historico",
):
    """
    Salva o histórico de uma ação em CSV.

    Exemplo:

        data/historico/PETR4.csv
    """

    if dados is None or dados.empty:
        return None

    os.makedirs(
        diretorio,
        exist_ok=True,
    )

    ticker = ticker.upper()

    caminho = os.path.join(
        diretorio,
        f"{ticker}.csv",
    )

    dados.to_csv(
        caminho,
        encoding="utf-8",
    )

    print(
        f"💾 Histórico salvo: {caminho}"
    )

    return caminho


# ============================================================
# CARREGAR HISTÓRICO LOCAL
# ============================================================

def carregar_csv(
    ticker,
    diretorio="data/historico",
):
    """
    Carrega um histórico salvo anteriormente.

    Isso permite trabalhar com dados locais sem precisar
    baixar novamente toda hora.
    """

    ticker = ticker.upper()

    caminho = os.path.join(
        diretorio,
        f"{ticker}.csv",
    )

    if not os.path.exists(caminho):

        return None

    try:

        dados = pd.read_csv(
            caminho,
            index_col=0,
            parse_dates=True,
        )

    except Exception as erro:

        print(
            f"❌ Erro ao carregar {caminho}: "
            f"{erro}"
        )

        return None

    return dados


# ============================================================
# ATUALIZAR DADOS
# ============================================================

def atualizar_acao(
    ticker,
    periodo=PERIODO_PADRAO,
):
    """
    Baixa os dados mais recentes e salva localmente.

    Retorna o DataFrame.
    """

    dados = baixar_historico(
        ticker,
        periodo=periodo,
    )

    if dados is None or dados.empty:

        return None

    salvar_csv(
        ticker,
        dados,
    )

    return dados


# ============================================================
# ATUALIZAR VÁRIAS AÇÕES
# ============================================================

def atualizar_acoes(
    tickers,
    periodo=PERIODO_PADRAO,
):
    """
    Atualiza várias ações.
    """

    resultados = {}

    print()
    print("=" * 60)
    print("📡 ATUALIZAÇÃO DOS DADOS")
    print("=" * 60)
    print()

    for ticker in tickers:

        dados = atualizar_acao(
            ticker,
            periodo=periodo,
        )

        if dados is not None:

            resultados[ticker.upper()] = (
                dados
            )

        time.sleep(
            ESPERA_ENTRE_REQUISICOES
        )

    print()
    print(
        f"✓ {len(resultados)} ações atualizadas."
    )
    print()

    return resultados


# ============================================================
# TESTE
# ============================================================

if __name__ == "__main__":

    print()
    print("=" * 60)
    print("📈 TESTE DO MARKET DATA")
    print("=" * 60)
    print()

    # Vamos testar somente uma ação primeiro.
    # Assim não fazemos várias requisições sem necessidade.

    ticker = "PETR4"

    dados = baixar_historico(
        ticker,
        periodo="6mo",
        intervalo="1d",
    )

    if dados is not None:

        print()
        print("📊 ÚLTIMOS REGISTROS:")
        print()

        print(
            dados.tail()
        )

        print()

        informacoes = (
            obter_informacoes_basicas(
                ticker,
                dados,
            )
        )

        print(
            "INFORMAÇÕES:"
        )

        for chave, valor in informacoes.items():

            print(
                f"  {chave}: {valor}"
            )

        print()

        salvar_csv(
            ticker,
            dados,
        )

    else:

        print(
            "❌ Não foi possível obter os dados."
        )
