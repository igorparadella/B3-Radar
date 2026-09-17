import os
import json
from datetime import datetime

from config import (
MAX_ACOES_IA,
SCORE_MINIMO,
DATA_DIR,
RESULTADO_FILE,
DADOS_ACOES_FILE,
validar_configuracao
)

from data.market_data import (
baixar_acoes,
salvar_csv
)

from analysis.indicators import (
calcular_indicadores,
gerar_resumo
)

from analysis.filters import (
filtrar_acoes
)

from analysis.scoring import (
calcular_score,
classificar_score,
detalhar_score,
criar_ranking,
selecionar_candidatas
)

from database.database import (
inicializar_banco,
salvar_precos,
salvar_analise
)

from ai.analyst import (
analisar_acoes
)

def carregar_tickers():
"""
Carrega os tickers do arquivo stocks.json.
"""

```
if not os.path.exists(DADOS_ACOES_FILE):
    raise FileNotFoundError(
        f"Arquivo não encontrado: {DADOS_ACOES_FILE}"
    )

with open(
    DADOS_ACOES_FILE,
    "r",
    encoding="utf-8"
) as arquivo:

    dados = json.load(arquivo)

tickers = dados.get("acoes", [])

if not tickers:
    raise ValueError(
        "Nenhuma ação foi encontrada em stocks.json."
    )

return tickers
```

def preparar_acao(ticker, df):
"""
Calcula todos os indicadores de uma ação
e transforma o resultado em um dicionário.
"""

```
if df is None or df.empty:
    return None

try:
    df = calcular_indicadores(df)

    resumo = gerar_resumo(df)

    if not resumo:
        return None

    resumo["ticker"] = ticker

    # Score quantitativo
    score = calcular_score(resumo)

    resumo["score"] = score
    resumo["classificacao"] = classificar_score(score)

    # Detalhamento do score
    detalhes = detalhar_score(resumo)

    if isinstance(detalhes, dict):
        resumo["detalhes_score"] = detalhes

    return resumo

except Exception as erro:

    print(
        f"[ERRO] Não foi possível analisar "
        f"{ticker}: {erro}"
    )

    return None
```

def baixar_dados(tickers):
"""
Baixa os dados históricos das ações.
"""

```
print()
print("Baixando dados de mercado...")
print("-" * 50)

dados = baixar_acoes(
    tickers,
    periodo="2y",
    intervalo="1d"
)

if not dados:
    raise RuntimeError(
        "Nenhum dado de mercado foi obtido."
    )

return dados
```

def processar_acoes(dados):
"""
Calcula indicadores e scores de todas as ações.
"""

```
resultados = []

print()
print("Calculando indicadores...")
print("-" * 50)

for ticker, df in dados.items():

    print(f"Analisando {ticker}...")

    resultado = preparar_acao(
        ticker,
        df
    )

    if resultado is None:
        print(
            f"  -> Sem dados suficientes."
        )
        continue

    resultados.append(resultado)

return resultados
```

def aplicar_filtros_resultados(resultados):
"""
Aplica os filtros fundamentais/técnicos
disponíveis ao resultado das ações.
"""

```
print()
print("Aplicando filtros...")
print("-" * 50)

aprovadas = []

for acao in resultados:

    passou, motivos = filtrar_acoes(
        acao
    )

    acao["filtros_aprovados"] = passou
    acao["motivos_filtro"] = motivos

    if passou:

        aprovadas.append(acao)

        print(
            f"  ✓ {acao['ticker']}"
        )

    else:

        print(
            f"  ✗ {acao['ticker']}"
        )

return aprovadas
```

def gerar_ranking_final(resultados):
"""
Cria o ranking quantitativo das ações.
"""

```
ranking = criar_ranking(
    resultados
)

# Garante que somente ações acima
# do score mínimo sejam candidatas.
candidatas = [
    acao
    for acao in ranking
    if float(
        acao.get("score", 0)
    ) >= SCORE_MINIMO
]

return candidatas
```

def selecionar_para_ia(ranking):
"""
Seleciona somente as principais candidatas
para enviar à IA.

```
Isso reduz bastante o consumo da API.
"""

candidatas = selecionar_candidatas(
    ranking,
    limite=MAX_ACOES_IA
)

return candidatas
```

def salvar_dados_locais(dados):
"""
Salva os históricos em CSV e SQLite.
"""

```
print()
print("Salvando dados locais...")
print("-" * 50)

for ticker, df in dados.items():

    try:

        salvar_csv(
            ticker,
            df
        )

        salvar_precos(
            ticker,
            df
        )

    except Exception as erro:

        print(
            f"[AVISO] Erro ao salvar "
            f"{ticker}: {erro}"
        )
```

def executar_analise_ia(candidatas):
"""
Envia somente as candidatas selecionadas
para a análise da OpenAI.
"""

```
if not candidatas:
    print()
    print(
        "Nenhuma ação atingiu o score mínimo."
    )

    return ""

print()
print("Enviando candidatas para a IA...")
print("-" * 50)

print(
    "Ações enviadas:",
    ", ".join(
        acao["ticker"]
        for acao in candidatas
    )
)

try:

    analise = analisar_acoes(
        candidatas
    )

    return analise

except Exception as erro:

    print(
        f"[ERRO] Falha na análise da IA: {erro}"
    )

    return ""
```

def salvar_resultado(
resultados,
ranking,
candidatas,
analise_ia
):
"""
Salva o resultado completo da execução.
"""

```
os.makedirs(
    DATA_DIR,
    exist_ok=True
)

resultado = {
    "data": datetime.now().isoformat(
        timespec="seconds"
    ),

    "total_acoes": len(
        resultados
    ),

    "total_aprovadas": len(
        ranking
    ),

    "total_candidatas_ia": len(
        candidatas
    ),

    "acoes": ranking,

    "candidatas_ia": candidatas,

    "analise_ia": analise_ia
}

with open(
    RESULTADO_FILE,
    "w",
    encoding="utf-8"
) as arquivo:

    json.dump(
        resultado,
        arquivo,
        ensure_ascii=False,
        indent=2,
        default=str
    )

return resultado
```

def salvar_analises_banco(
candidatas,
analise_ia
):
"""
Salva o resultado da análise da IA
no banco SQLite.

```
A análise completa é associada a cada
candidata enviada para a IA.
"""

if not candidatas:
    return

for acao in candidatas:

    try:

        salvar_analise(
            ticker=acao["ticker"],
            score=acao.get(
                "score",
                0
            ),
            classificacao=acao.get(
                "classificacao",
                ""
            ),
            dados=acao,
            analise_ia=analise_ia
        )

    except Exception as erro:

        print(
            f"[AVISO] Não foi possível "
            f"salvar análise de "
            f"{acao['ticker']}: {erro}"
        )
```

def mostrar_resultado(
ranking,
candidatas,
analise_ia
):
"""
Mostra um resumo da execução no terminal.
"""

```
print()
print("=" * 60)
print("RESULTADO DO B3 RADAR")
print("=" * 60)

if not ranking:

    print()
    print(
        "Nenhuma ação passou pelos filtros."
    )

else:

    print()

    for posicao, acao in enumerate(
        ranking,
        start=1
    ):

        ticker = acao.get(
            "ticker",
            "N/A"
        )

        score = float(
            acao.get(
                "score",
                0
            )
        )

        classificacao = acao.get(
            "classificacao",
            ""
        )

        preco = acao.get(
            "preco"
        )

        print(
            f"{posicao:02d}. "
            f"{ticker:<8} "
            f"Score: {score:>6.2f} "
            f"Preço: {preco} "
            f"| {classificacao}"
        )

print()
print("-" * 60)

print(
    f"Candidatas enviadas à IA: "
    f"{len(candidatas)}"
)

if analise_ia:

    print()
    print("ANÁLISE DA IA")
    print("-" * 60)
    print(analise_ia)

print()
print("=" * 60)
```

def main():

```
print("=" * 60)
print("B3 RADAR")
print("Sistema de monitoramento quantitativo")
print("=" * 60)

try:

    # 1. Configuração
    validar_configuracao()

    # 2. Banco
    inicializar_banco()

    # 3. Tickers
    tickers = carregar_tickers()

    print()
    print(
        f"Ações configuradas: {len(tickers)}"
    )

    # 4. Mercado
    dados = baixar_dados(
        tickers
    )

    # 5. Salvar histórico
    salvar_dados_locais(
        dados
    )

    # 6. Indicadores
    resultados = processar_acoes(
        dados
    )

    # 7. Filtros
    resultados_filtrados = (
        aplicar_filtros_resultados(
            resultados
        )
    )

    # 8. Ranking
    ranking = gerar_ranking_final(
        resultados_filtrados
    )

    # 9. Seleção para IA
    candidatas = selecionar_para_ia(
        ranking
    )

    # 10. IA
    analise_ia = executar_analise_ia(
        candidatas
    )

    # 11. Salvar resultado
    salvar_resultado(
        resultados=resultados,
        ranking=ranking,
        candidatas=candidatas,
        analise_ia=analise_ia
    )

    # 12. Banco
    salvar_analises_banco(
        candidatas,
        analise_ia
    )

    # 13. Terminal
    mostrar_resultado(
        ranking,
        candidatas,
        analise_ia
    )

    print()
    print(
        f"Resultado salvo em: "
        f"{RESULTADO_FILE}"
    )

except KeyboardInterrupt:

    print()
    print(
        "Execução interrompida pelo usuário."
    )

except Exception as erro:

    print()
    print("=" * 60)
    print("ERRO DURANTE A EXECUÇÃO")
    print("=" * 60)
    print(erro)
```

if **name** == "**main**":
main()
