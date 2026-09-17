# config.py

import os
from dotenv import load_dotenv


# ============================================================
# CARREGAMENTO DAS VARIÁVEIS DE AMBIENTE
# ============================================================

load_dotenv()


# ============================================================
# OPENAI
# ============================================================

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Deixamos o modelo configurável pelo .env.
# Assim podemos trocar o modelo sem alterar o código.
OPENAI_MODEL = os.getenv(
    "OPENAI_MODEL",
    "gpt-5.6-luna"
)


# ============================================================
# CONFIGURAÇÕES DO RADAR
# ============================================================

# Quantas ações serão enviadas para a IA.
#
# Quanto menor esse número, menor o consumo da API.
MAX_ACOES_IA = 5


# Score mínimo para uma ação ser considerada candidata.
#
# Ações abaixo desse valor ainda podem aparecer no ranking,
# mas não serão enviadas para a IA.
SCORE_MINIMO = 50


# ============================================================
# INDICADORES
# ============================================================

# Períodos das médias móveis
MEDIA_MOVEL_CURTA = 20
MEDIA_MOVEL_MEDIA = 50
MEDIA_MOVEL_LONGA = 200

# RSI
RSI_PERIODO = 14


# ============================================================
# DIRETÓRIOS
# ============================================================

DATA_DIR = "data"

RESULTADO_FILE = os.path.join(
    DATA_DIR,
    "resultado.json"
)

DADOS_ACOES_FILE = os.path.join(
    DATA_DIR,
    "stocks.json"
)


# ============================================================
# CONFIGURAÇÕES DE ANÁLISE
# ============================================================

# Valuation
PL_MAXIMO = 10

# Rentabilidade mínima
ROE_MINIMO = 15

# Dividend Yield mínimo
DIVIDEND_YIELD_MINIMO = 5

# Volume relativo mínimo
VOLUME_RELATIVO_MINIMO = 1.0


# ============================================================
# CONFIGURAÇÕES DO SISTEMA
# ============================================================

# Quantidade máxima de ações exibidas no terminal.
MAX_ACOES_EXIBIDAS = 20


# ============================================================
# VALIDAÇÃO
# ============================================================

def validar_configuracao():
    """
    Verifica se as configurações básicas estão corretas.
    """

    if not OPENAI_API_KEY:
        raise RuntimeError(
            "\n"
            "❌ OPENAI_API_KEY não encontrada.\n\n"
            "Crie um arquivo .env na raiz do projeto:\n\n"
            "OPENAI_API_KEY=sua_chave_aqui\n"
        )

    if MAX_ACOES_IA <= 0:
        raise ValueError(
            "MAX_ACOES_IA precisa ser maior que zero."
        )

    if SCORE_MINIMO < 0 or SCORE_MINIMO > 100:
        raise ValueError(
            "SCORE_MINIMO precisa estar entre 0 e 100."
        )

    if RSI_PERIODO <= 0:
        raise ValueError(
            "RSI_PERIODO precisa ser maior que zero."
        )


# ============================================================
# INFORMAÇÕES
# ============================================================

def mostrar_configuracao():

    print()
    print("=" * 60)
    print("⚙️ CONFIGURAÇÃO DO B3 INVESTMENT RADAR")
    print("=" * 60)

    print(
        f"🤖 Modelo OpenAI:      {OPENAI_MODEL}"
    )

    print(
        f"💰 Máx. ações na IA:   {MAX_ACOES_IA}"
    )

    print(
        f"📊 Score mínimo:       {SCORE_MINIMO}"
    )

    print(
        f"📈 Média curta:        {MEDIA_MOVEL_CURTA}"
    )

    print(
        f"📈 Média média:        {MEDIA_MOVEL_MEDIA}"
    )

    print(
        f"📈 Média longa:        {MEDIA_MOVEL_LONGA}"
    )

    print(
        f"📉 RSI período:        {RSI_PERIODO}"
    )

    print(
        f"📁 Dados:              {DADOS_ACOES_FILE}"
    )

    print(
        f"💾 Resultado:          {RESULTADO_FILE}"
    )

    print("=" * 60)
    print()