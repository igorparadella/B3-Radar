from flask import Flask, render_template, jsonify
import os
import json

from database.database import (
inicializar_banco,
obter_ultimas_analises
)

app = Flask(**name**)

# Garante que o banco exista ao iniciar o servidor

inicializar_banco()

def carregar_resultado():
    """
    Carrega o resultado mais recente gerado pelo radar.
    """


    arquivo = "data/resultado.json"

    if not os.path.exists(arquivo):
        return {
            "acoes": [],
            "mensagem": "Nenhum resultado disponível ainda."
        }

    try:
        with open(
            arquivo,
            "r",
            encoding="utf-8"
        ) as f:
            return json.load(f)

    except json.JSONDecodeError:
        return {
            "acoes": [],
            "mensagem": "O arquivo de resultado está inválido."
        }


    @app.route("/")

def index():
"""
Página principal do dashboard.
"""


resultado = carregar_resultado()

return render_template(
    "index.html",
    resultado=resultado
)


@app.route("/api/resultado")
def api_resultado():
    """
    Retorna o resultado do radar em JSON.
    """


    return jsonify(carregar_resultado())


    @app.route("/api/analises")
    def api_analises():
    """
    Retorna as análises armazenadas no banco.
    """


    analises = obter_ultimas_analises(20)

    return jsonify(analises)


    @app.route("/api/status")

def api_status():
    """
    Endpoint simples para verificar se o servidor está funcionando.
    """


    return jsonify({
        "status": "online",
        "servico": "B3 Radar"
    })


    if **name** == "**main**":


    print("=" * 50)
    print("B3 RADAR")
    print("=" * 50)
    print()
    print("Dashboard iniciado.")
    print("Acesse no navegador:")
    print("http://127.0.0.1:5000")
    print()

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )

