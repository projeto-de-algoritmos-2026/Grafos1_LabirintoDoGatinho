import heapq
import random
from collections import deque

from flask import Flask, jsonify, request, send_from_directory

app = Flask(__name__, static_folder="static")

# ─────────────────────────────────────────────
# Constantes do Labirinto
# ─────────────────────────────────────────────
GRID_SIZE = 10
START = (0, 0)
END = (9, 9)

# Tipos de célula
CELL_FREE = "free"
CELL_WALL = "wall"
CELL_BOMB = "bomb"
CELL_WATER = "water"

# Pesos para o Dijkstra
# Paredes e bombas têm peso "infinito" (intransitáveis)
WEIGHTS = {
    CELL_FREE: 1,
    CELL_WATER:  3,
    CELL_WALL: float("inf"),
    CELL_BOMB: float("inf"),
}

# Direções: cima, baixo, esquerda, direita
DIRECTIONS = [(-1, 0), (1, 0), (0, -1), (0, 1)]


# ─────────────────────────────────────────────
# Geração do Labirinto
# ─────────────────────────────────────────────

def gerar_labirinto() -> list[list[str]]:
    total = GRID_SIZE * GRID_SIZE

    # Tentamos até 100 vezes gerar um labirinto com caminho válido
    for _ in range(100):
        grid = [[CELL_FREE] * GRID_SIZE for _ in range(GRID_SIZE)]

        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                if (r, c) in (START, END):
                    continue
                roll = random.random()
                if roll < 0.25:
                    grid[r][c] = CELL_WALL
                elif roll < 0.35:
                    grid[r][c] = CELL_BOMB
                elif roll < 0.45:
                    grid[r][c] = CELL_WATER

        # Verifica conectividade com BFS
        if _bfs_conectividade(grid):
            return grid

    return _labirinto_garantido()


def _bfs_conectividade(grid: list[list[str]]) -> bool:
    visitado = [[False] * GRID_SIZE for _ in range(GRID_SIZE)]
    fila = deque([START])
    visitado[START[0]][START[1]] = True

    while fila:
        r, c = fila.popleft()
        if (r, c) == END:
            return True
        for dr, dc in DIRECTIONS:
            nr, nc = r + dr, c + dc
            if (
                0 <= nr < GRID_SIZE
                and 0 <= nc < GRID_SIZE
                and not visitado[nr][nc]
                and grid[nr][nc] not in (CELL_WALL, CELL_BOMB)
            ):
                visitado[nr][nc] = True
                fila.append((nr, nc))
    return False


def _labirinto_garantido() -> list[list[str]]:
    grid = [[CELL_WALL] * GRID_SIZE for _ in range(GRID_SIZE)]
    # Abre corredor horizontal + vertical para garantir conectividade
    for i in range(GRID_SIZE):
        grid[0][i] = CELL_FREE   # linha superior
        grid[i][9] = CELL_FREE   # coluna direita
    grid[0][0] = CELL_FREE
    grid[9][9] = CELL_FREE
    return grid


# ─────────────────────────────────────────────
# Construção do Grafo (Lista de Adjacência)
# ─────────────────────────────────────────────

def construir_grafo(grid: list[list[str]]) -> dict:
    grafo = {}

    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            tipo = grid[r][c]
            if tipo in (CELL_WALL, CELL_BOMB):
                continue  # Nó intransitável: sem arestas

            adjacentes = []
            for dr, dc in DIRECTIONS:
                nr, nc = r + dr, c + dc
                if 0 <= nr < GRID_SIZE and 0 <= nc < GRID_SIZE:
                    tipo_vizinho = grid[nr][nc]
                    if tipo_vizinho not in (CELL_WALL, CELL_BOMB):
                        peso = WEIGHTS[tipo_vizinho]
                        adjacentes.append(((nr, nc), peso))

            grafo[(r, c)] = adjacentes

    return grafo


# ─────────────────────────────────────────────
# Algoritmo 1: BFS — Busca em Largura
# ─────────────────────────────────────────────

def bfs(grafo: dict, origem: tuple, destino: tuple) -> list[tuple]:
    if origem not in grafo or destino not in grafo:
        return []

    visitado = {origem}

    # Fila armazena: (nó_atual, caminho_até_aqui)
    fila = deque([(origem, [origem])])

    while fila:
        no_atual, caminho = fila.popleft()

        if no_atual == destino:
            return caminho

        for (vizinho, _peso) in grafo.get(no_atual, []):
            if vizinho not in visitado:
                visitado.add(vizinho)
                fila.append((vizinho, caminho + [vizinho]))

    return []  # Sem caminho

# ─────────────────────────────────────────────
# Algoritmo 2: Dijkstra — Caminho de Menor Custo
# ─────────────────────────────────────────────

def dijkstra(grafo: dict, origem: tuple, destino: tuple) -> list[tuple]:
    if origem not in grafo or destino not in grafo:
        return []

    # dist[v] = menor custo conhecido até v
    dist = {no: float("inf") for no in grafo}
    dist[origem] = 0

    # Heap: (custo, nó, caminho)
    heap = [(0, origem, [origem])]

    # Conjunto de nós já finalizados (custo mínimo definitivo)
    finalizados = set()

    while heap:
        custo_atual, no_atual, caminho = heapq.heappop(heap)

        if no_atual in finalizados:
            continue  # Já processamos este nó com custo menor
        finalizados.add(no_atual)

        if no_atual == destino:
            return caminho

        for (vizinho, peso) in grafo.get(no_atual, []):
            if vizinho not in finalizados:
                novo_custo = custo_atual + peso
                if novo_custo < dist[vizinho]:
                    dist[vizinho] = novo_custo
                    heapq.heappush(heap, (novo_custo, vizinho, caminho + [vizinho]))

    return []  # Sem caminho

# ─────────────────────────────────────────────
# Estado Global
# ─────────────────────────────────────────────

estado = {
    "grid": None,
    "grafo": None,
}

# ─────────────────────────────────────────────
# Rotas da API Flask
# ─────────────────────────────────────────────

@app.route("/")
def index():
    return send_from_directory("static", "index.html")


@app.route("/api/mapa", methods=["GET"])
def api_mapa():
    grid = gerar_labirinto()
    grafo = construir_grafo(grid)

    # Persiste no estado global
    estado["grid"] = grid
    estado["grafo"] = grafo

    return jsonify({
        "grid": grid,
        "inicio": list(START),
        "fim": list(END),
        "tamanho": GRID_SIZE,
    })


@app.route("/api/caminhos", methods=["POST"])
def api_caminhos():
    dados = request.get_json()
    if not dados:
        return jsonify({"erro": "Corpo JSON inválido"}), 400

    x = dados.get("x", 0)
    y = dados.get("y", 0)
    origem = (x, y)

    grid = estado.get("grid")
    grafo = estado.get("grafo")

    if grid is None or grafo is None:
        return jsonify({"erro": "Labirinto não gerado. Chame /api/mapa primeiro."}), 400

    caminho_bfs = bfs(grafo, origem, END)
    caminho_dijkstra = dijkstra(grafo, origem, END)

    # Calcula custo real do Dijkstra (soma dos pesos)
    def calcular_custo(caminho):
        if len(caminho) < 2:
            return 0
        total = 0
        for i in range(1, len(caminho)):
            r, c = caminho[i]
            total += WEIGHTS.get(grid[r][c], 1)
        return total

    return jsonify({
        "path_bfs": [list(p) for p in caminho_bfs],
        "path_dijkstra": [list(p) for p in caminho_dijkstra],
        "custo_bfs": len(caminho_bfs) - 1 if caminho_bfs else -1,
        "custo_dijkstra": calcular_custo(caminho_dijkstra),
    })


# ─────────────────────────────────────────────
# Entry Point
# ─────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 50)
    print("  Labirinto do Gatinho — Servidor Flask iniciado")
    print("  Acesse: http://localhost:5000")
    print("=" * 50)
    app.run(debug=False, port=5000)
