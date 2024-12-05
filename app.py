from flask import Flask, json, jsonify, request
from itertools import permutations
from flask_cors import CORS  # Importando o CORS

app = Flask(__name__)
CORS(app, supports_credentials=True)

# Funções auxiliares
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

def calcular_custo_por_no(grafo):
    custo_por_no = {}

    for origem, destinos in grafo.items():
        custo_total = 0
        
        for destino, peso in destinos:
            custo_total += peso
        
        custo_por_no[origem] = custo_total

    return custo_por_no

def vizinho_mais_proximo(grafo, inicio):
    visitados = {inicio}
    rota = [inicio]
    custo_total = 0

    atual = inicio
    while len(visitados) < len(grafo):
        vizinho_mais_proximo = None
        menor_peso = float('inf')
        for vizinho, peso in grafo[atual]:
            if vizinho not in visitados and peso < menor_peso:
                vizinho_mais_proximo = vizinho
                menor_peso = peso
        if vizinho_mais_proximo:
            rota.append(vizinho_mais_proximo)
            custo_total += menor_peso
            visitados.add(vizinho_mais_proximo)
            atual = vizinho_mais_proximo

    # Retorno ao ponto de partida
    for vizinho, peso in grafo[rota[-1]]:
        if vizinho == inicio:
            custo_total += peso
            break
    rota.append(inicio)
    return rota, custo_total

# Dados do problema
brinquedos = {
    'Insano': {'tempo_espera': 20, 'distancias': {'Kalafrio': 100, 'Vaikuntudo': 150, 'Maremoto': 200, 'Arrepius': 180, 'Ramubrinká': 170, 'Tobomusik': 90, 'Atlantis': 120, 'Aqua Show': 180, 'Moréia Negra': 150, 'Ilha do Tesouro': 100}},
    'Kalafrio': {'tempo_espera': 10, 'distancias': {'Insano': 100, 'Vaikuntudo': 120, 'Arrepius': 180, 'Ramubrinká': 170, 'Tobomusik': 110, 'Atlantis': 140, 'Aqua Show': 160, 'Moréia Negra': 180, 'Ilha do Tesouro': 130}},
    'Vaikuntudo': {'tempo_espera': 15, 'distancias': {'Insano': 150, 'Kalafrio': 120, 'Maremoto': 90, 'Arrepius': 200, 'Ramubrinká': 150, 'Tobomusik': 100, 'Atlantis': 130, 'Aqua Show': 160, 'Moréia Negra': 140, 'Ilha do Tesouro': 180}},
    'Maremoto': {'tempo_espera': 12, 'distancias': {'Insano': 200, 'Vaikuntudo': 90, 'Ramubrinká': 170, 'Ilha do Tesouro': 70, 'Arrepius': 120, 'Tobomusik': 130, 'Atlantis': 140, 'Aqua Show': 180, 'Moréia Negra': 160}},
    'Arrepius': {'tempo_espera': 18, 'distancias': {'Kalafrio': 180, 'Insano': 180, 'Vaikuntudo': 200, 'Maremoto': 120, 'Ramubrinká': 150, 'Tobomusik': 180, 'Atlantis': 160, 'Aqua Show': 140, 'Moréia Negra': 100, 'Ilha do Tesouro': 190}},
    'Ramubrinká': {'tempo_espera': 8, 'distancias': {'Maremoto': 170, 'Insano': 170, 'Vaikuntudo': 150, 'Arrepius': 150, 'Tobomusik': 100, 'Atlantis': 130, 'Aqua Show': 180, 'Moréia Negra': 110, 'Ilha do Tesouro': 160}},
    'Tobomusik': {'tempo_espera': 10, 'distancias': {'Atlantis': 120, 'Aqua Show': 100, 'Insano': 90, 'Kalafrio': 110, 'Vaikuntudo': 100, 'Maremoto': 130, 'Arrepius': 180, 'Ramubrinká': 100, 'Ilha do Tesouro': 150}},
    'Atlantis': {'tempo_espera': 7, 'distancias': {'Tobomusik': 120, 'Aqua Show': 150, 'Insano': 120, 'Kalafrio': 140, 'Vaikuntudo': 130, 'Maremoto': 140, 'Arrepius': 160, 'Ramubrinká': 130, 'Ilha do Tesouro': 110}},
    'Aqua Show': {'tempo_espera': 30, 'distancias': {'Tobomusik': 100, 'Ilha do Tesouro': 200, 'Insano': 180, 'Kalafrio': 160, 'Vaikuntudo': 160, 'Maremoto': 180, 'Arrepius': 140, 'Ramubrinká': 180, 'Atlantis': 150}},
    'Moréia Negra': {'tempo_espera': 14, 'distancias': {'Ilha do Tesouro': 160, 'Arrepius': 120, 'Insano': 150, 'Kalafrio': 180, 'Vaikuntudo': 140, 'Maremoto': 160, 'Tobomusik': 180, 'Ramubrinká': 110, 'Atlantis': 130}},
    'Ilha do Tesouro': {'tempo_espera': 12, 'distancias': {'Maremoto': 70, 'Aqua Show': 200, 'Moréia Negra': 160, 'Insano': 100, 'Kalafrio': 130, 'Vaikuntudo': 180, 'Arrepius': 190, 'Ramubrinká': 160, 'Tobomusik': 150, 'Atlantis': 110}}
}

# Criando o grafo inicial
def criar_grafo_completo(brinquedos):
    novo_grafo = {}
    for brinquedo, dados in brinquedos.items():
        novo_grafo[brinquedo] = []
        for destino, distancia in dados['distancias'].items():
            tempo_espera = brinquedos[destino]['tempo_espera']
            peso = calcular_peso(distancia, tempo_espera)
            novo_grafo[brinquedo].append((destino, peso))
    return novo_grafo

# Inicializando o grafo
grafo = criar_grafo_completo(brinquedos)

# Dados das coordenadas
coordenadas = {
    "Insano": {"x": 1, "y": 5},
    "Kalafrio": {"x": 2, "y": 3},
    "Vaikuntudo": {"x": 4, "y": 8},
    "Maremoto": {"x": 7, "y": 1},
    "Arrepius": {"x": 3, "y": 7},
    "Ramubrinká": {"x": 7, "y": 4},
    "Tobomusik": {"x": 8, "y": 2},
    "Atlantis": {"x": 9, "y": 6},
    "Aqua Show": {"x": 12, "y": 7},
    "Ilha do Tesouro": {"x": 11, "y": 2},
    "Moréia Negra": {"x": 14, "y": 8}
}

# Inicializando o ponto de partida e rota
inicio = 'Insano'
rota, custo = vizinho_mais_proximo(grafo, inicio)

# Rotas da API
@app.route('/rota', methods=['GET'])
def rota_api():
    custo_por_no = calcular_custo_por_no(grafo)
    return jsonify({
        "rota": rota,
        "custo": custo,
        "grafo": coordenadas,
        "inicio": inicio,
        "custo_por_no": custo_por_no
    })

@app.route('/atualizar', methods=['POST'])
def atualizar_api():
    global brinquedos, grafo, coordenadas
    dados = request.json
    brinquedos = dados.get('brinquedos', brinquedos)
    grafo = criar_grafo_completo(brinquedos)
    coordenadas = dados.get('coordenadas', coordenadas)
    return jsonify({"message": "Dados atualizados com sucesso"})

if __name__ == '__main__':
    app.run(debug=True, port= 8080)
