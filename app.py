from flask import Flask, jsonify
from itertools import permutations

from flask_cors import CORS  # Importe o CORS

app = Flask(__name__)

# Permite CORS para todas as rotas
CORS(app)


# Funções do TSP
def calcular_peso(distancia, tempo_espera):
    return distancia + (tempo_espera * 3)

def calcular_custo(rota, grafo):
    custo_total = 0
    for i in range(len(rota) - 1):
        origem = rota[i]
        destino = rota[i + 1]

        for vizinho, peso in grafo[origem]:
            if vizinho == destino:
                custo_total += peso
                break

    for vizinho, peso in grafo[rota[-1]]:
        if vizinho == rota[0]:
            custo_total += peso
            break
    return custo_total

def tsp(grafo, inicio):
    nodos = list(grafo.keys())
    nodos.remove(inicio)

    menor_custo = float('inf')
    melhor_rota = None

    for permutacao in permutations(nodos):
        rota = [inicio] + list(permutacao)
        custo = calcular_custo(rota, grafo)
        if custo < menor_custo:
            menor_custo = custo
            melhor_rota = rota

    return melhor_rota, menor_custo

# Dados do problema
brinquedos = {
    'A': {'tempo_espera': 10, 'distancias': {'B': 100, 'C': 150}},
    'B': {'tempo_espera': 5, 'distancias': {'A': 100, 'C': 120, 'D': 200}},
    'C': {'tempo_espera': 8, 'distancias': {'A': 150, 'B': 120, 'D': 90}},
    'D': {'tempo_espera': 12, 'distancias': {'B': 200, 'C': 90}}
}

grafo = {}
for brinquedo, dados in brinquedos.items():
    grafo[brinquedo] = []
    for destino, distancia in dados['distancias'].items():
        tempo_espera = brinquedos[destino]['tempo_espera']
        peso = calcular_peso(distancia, tempo_espera)
        grafo[brinquedo].append((destino, peso))

# Coordenadas fictícias dos brinquedos para o gráfico
coordenadas = {
    "A": {"x": 1, "y": 5},
    "B": {"x": 2, "y": 3},
    "C": {"x": 4, "y": 8},
    "D": {"x": 7, "y": 1}
}

inicio = 'A'
rota, custo = tsp(grafo, inicio)

# Rota API
@app.route('/rota')
def rota_api():
    return jsonify({
        "rota": rota,
        "custo": custo,
        "grafo": coordenadas
    })

if __name__ == '__main__':
    app.run(debug=True)
