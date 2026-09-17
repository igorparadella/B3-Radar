import json
from openai import OpenAI

from config import OPENAI_API_KEY, OPENAI_MODEL

def criar_cliente():
"""
Cria o cliente da OpenAI.
"""

```
if not OPENAI_API_KEY:
    raise RuntimeError(
        "OPENAI_API_KEY não foi configurada no arquivo .env"
    )

return OpenAI(api_key=OPENAI_API_KEY)
```

def preparar_dados(acoes):
"""
Prepara os dados das ações para serem enviados à IA.

```
Remove informações desnecessárias para reduzir
o tamanho da requisição.
"""

dados = []

for acao in acoes:

    item = {
        "ticker": acao.get("ticker"),

        "score": acao.get("score"),

        "classificacao": acao.get("classificacao"),

        "preco": acao.get("preco"),

        "rsi": acao.get("rsi"),

        "sma_20": acao.get("sma_20"),
        "sma_50": acao.get("sma_50"),
        "sma_200": acao.get("sma_200"),

        "macd": acao.get("macd"),
        "macd_signal": acao.get("macd_signal"),

        "volume_relativo": acao.get(
            "volume_relativo"
        ),

        "retorno_20d": acao.get(
            "retorno_20d"
        ),

        "retorno_60d": acao.get(
            "retorno_60d"
        ),

        "retorno_252d": acao.get(
            "retorno_252d"
        ),

        "volatilidade": acao.get(
            "volatilidade"
        ),

        "drawdown": acao.get(
            "drawdown"
        ),

        "pl": acao.get("pl"),
        "roe": acao.get("roe"),
        "dividend_yield": acao.get(
            "dividend_yield"
        )
    }

    dados.append(item)

return dados
```

def criar_prompt(acoes):
"""
Cria o prompt enviado para a IA.
"""

```
dados = preparar_dados(acoes)

dados_json = json.dumps(
    dados,
    ensure_ascii=False,
    indent=2,
    default=str
)

prompt = f"""
```

Você é um analista auxiliar de pesquisa de investimentos.

Seu trabalho é analisar os dados quantitativos fornecidos
pelo meu sistema de monitoramento de ações da B3.

IMPORTANTE:

* Não dê ordens diretas de compra ou venda.
* Não prometa rentabilidade.
* Não trate o score como probabilidade de retorno.
* Não invente dados que não foram fornecidos.
* Diferencie claramente fatos, sinais técnicos e incertezas.
* A análise deve servir para decidir quais empresas merecem
  uma investigação mais aprofundada.
* Considere riscos e pontos negativos, não apenas pontos positivos.
* Se os dados forem insuficientes, diga explicitamente.

Para cada ação, informe:

1. Resumo do cenário
2. Principais sinais positivos
3. Principais riscos
4. Indicadores que merecem investigação
5. O que seria necessário verificar antes de qualquer decisão
6. Uma classificação textual:

   * ESTUDAR
   * ACOMPANHAR
   * POUCO PRIORITÁRIO

Depois faça uma conclusão geral comparando os ativos
SEM criar um ranking de "melhor investimento".

Dados fornecidos pelo sistema:

{dados_json}
"""

```
return prompt
```

def analisar_acoes(acoes):
"""
Envia as ações selecionadas para a OpenAI.

```
Retorna o texto produzido pela IA.
"""

if not acoes:
    return "Nenhuma ação foi selecionada para análise."

cliente = criar_cliente()

prompt = criar_prompt(acoes)

resposta = cliente.responses.create(
    model=OPENAI_MODEL,
    input=prompt,
    max_output_tokens=1500
)

return resposta.output_text
```

def analisar_uma_acao(acao):
"""
Analisa somente uma ação.

```
Útil para consultas individuais no dashboard.
"""

return analisar_acoes([acao])
```

def salvar_analise_texto(
ticker,
texto,
arquivo="data/analise_ia.json"
):
"""
Salva análises da IA em um arquivo JSON.
"""

```
try:
    with open(
        arquivo,
        "r",
        encoding="utf-8"
    ) as arquivo_json:

        dados = json.load(arquivo_json)

except (
    FileNotFoundError,
    json.JSONDecodeError
):
    dados = {}

dados[ticker] = {
    "analise": texto
}

with open(
    arquivo,
    "w",
    encoding="utf-8"
) as arquivo_json:

    json.dump(
        dados,
        arquivo_json,
        ensure_ascii=False,
        indent=2
    )
```

if **name** == "**main**":

```
print("Módulo de análise com IA carregado.")

if not OPENAI_API_KEY:
    print(
        "AVISO: OPENAI_API_KEY não encontrada."
    )
else:
    print(
        f"Modelo configurado: {OPENAI_MODEL}"
    )
```
