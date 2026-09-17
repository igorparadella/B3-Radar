import sqlite3
import os
import json
from datetime import datetime

DB_DIR = "data"
DB_FILE = os.path.join(DB_DIR, "radar.db")

def conectar():
"""
Cria uma conexão com o banco SQLite.
"""
os.makedirs(DB_DIR, exist_ok=True)

```
conexao = sqlite3.connect(DB_FILE)
conexao.row_factory = sqlite3.Row

return conexao
```

def inicializar_banco():
"""
Cria as tabelas necessárias caso ainda não existam.
"""

```
conexao = conectar()
cursor = conexao.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS precos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ticker TEXT NOT NULL,
        data TEXT NOT NULL,
        preco REAL,
        volume REAL,
        UNIQUE(ticker, data)
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS analises (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ticker TEXT NOT NULL,
        data TEXT NOT NULL,
        score REAL,
        classificacao TEXT,
        dados TEXT,
        analise_ia TEXT
    )
""")

cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_precos_ticker
    ON precos(ticker)
""")

cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_analises_ticker
    ON analises(ticker)
""")

conexao.commit()
conexao.close()
```

def salvar_preco(ticker, data, preco, volume=0):
"""
Salva o preço de uma ação.

```
Se já existir um registro para o mesmo ticker e data,
ele é atualizado.
"""

conexao = conectar()
cursor = conexao.cursor()

cursor.execute("""
    INSERT INTO precos (
        ticker,
        data,
        preco,
        volume
    )
    VALUES (?, ?, ?, ?)

    ON CONFLICT(ticker, data)
    DO UPDATE SET
        preco = excluded.preco,
        volume = excluded.volume
""", (
    ticker,
    data,
    preco,
    volume
))

conexao.commit()
conexao.close()
```

def salvar_precos(ticker, df):
"""
Salva todo o histórico de preços de um DataFrame.
"""

```
if df is None or df.empty:
    return

conexao = conectar()
cursor = conexao.cursor()

registros = []

for data, linha in df.iterrows():

    preco = linha.get("Close", 0)
    volume = linha.get("Volume", 0)

    try:
        preco = float(preco)
    except (TypeError, ValueError):
        preco = 0

    try:
        volume = float(volume)
    except (TypeError, ValueError):
        volume = 0

    if hasattr(data, "strftime"):
        data_formatada = data.strftime("%Y-%m-%d")
    else:
        data_formatada = str(data)

    registros.append((
        ticker,
        data_formatada,
        preco,
        volume
    ))

cursor.executemany("""
    INSERT INTO precos (
        ticker,
        data,
        preco,
        volume
    )
    VALUES (?, ?, ?, ?)

    ON CONFLICT(ticker, data)
    DO UPDATE SET
        preco = excluded.preco,
        volume = excluded.volume
""", registros)

conexao.commit()
conexao.close()
```

def obter_historico(ticker, limite=None):
"""
Retorna o histórico de preços de uma ação.
"""

```
conexao = conectar()
cursor = conexao.cursor()

if limite:
    cursor.execute("""
        SELECT ticker, data, preco, volume
        FROM precos
        WHERE ticker = ?
        ORDER BY data DESC
        LIMIT ?
    """, (ticker, limite))
else:
    cursor.execute("""
        SELECT ticker, data, preco, volume
        FROM precos
        WHERE ticker = ?
        ORDER BY data ASC
    """, (ticker,))

resultados = cursor.fetchall()

conexao.close()

return [dict(linha) for linha in resultados]
```

def salvar_analise(
ticker,
score,
classificacao,
dados,
analise_ia=""
):
"""
Salva o resultado de uma análise.

```
'dados' pode ser um dicionário contendo
indicadores técnicos e fundamentalistas.
"""

conexao = conectar()
cursor = conexao.cursor()

data = datetime.now().isoformat(timespec="seconds")

if isinstance(dados, dict):
    dados = json.dumps(
        dados,
        ensure_ascii=False,
        default=str
    )

cursor.execute("""
    INSERT INTO analises (
        ticker,
        data,
        score,
        classificacao,
        dados,
        analise_ia
    )
    VALUES (?, ?, ?, ?, ?, ?)
""", (
    ticker,
    data,
    score,
    classificacao,
    dados,
    analise_ia
))

conexao.commit()
conexao.close()
```

def obter_ultima_analise(ticker):
"""
Retorna a análise mais recente de uma ação.
"""

```
conexao = conectar()
cursor = conexao.cursor()

cursor.execute("""
    SELECT *
    FROM analises
    WHERE ticker = ?
    ORDER BY data DESC
    LIMIT 1
""", (ticker,))

resultado = cursor.fetchone()

conexao.close()

if resultado is None:
    return None

resultado = dict(resultado)

if resultado.get("dados"):
    try:
        resultado["dados"] = json.loads(resultado["dados"])
    except (json.JSONDecodeError, TypeError):
        pass

return resultado
```

def obter_ultimas_analises(limite=20):
"""
Retorna as análises mais recentes.
"""

```
conexao = conectar()
cursor = conexao.cursor()

cursor.execute("""
    SELECT *
    FROM analises
    ORDER BY data DESC
    LIMIT ?
""", (limite,))

resultados = cursor.fetchall()

conexao.close()

return [dict(linha) for linha in resultados]
```

def limpar_dados():
"""
Apaga todos os dados armazenados no banco.

```
Cuidado: essa função remove o histórico.
"""

conexao = conectar()
cursor = conexao.cursor()

cursor.execute("DELETE FROM precos")
cursor.execute("DELETE FROM analises")

conexao.commit()
conexao.close()
```

if **name** == "**main**":

```
print("Inicializando banco de dados...")

inicializar_banco()

print(f"Banco criado em: {DB_FILE}")
print("Banco de dados pronto.")
```
