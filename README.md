# Labirinto do Gatinho

Número da Lista: 09<br>
Conteúdo da Disciplina: Grafos 1<br>

## Alunos
|Matrícula | Aluno |
| -- | -- |
| 23/1027023  |  Amanda Cruz Lima |
| 22/1031158  |  Felipe de Oliveira Motta |

## Sobre

Projeto desenvolvido como um minijogo de fuga de labirinto. O usuário controla um gatinho 🐱 que deve sair da posição (0,0) e chegar ao peixinho 🐟 em (9,9) em uma grade 10×10 gerada aleatoriamente.

O objetivo central é permitir a visualização e comparação em tempo real de dois algoritmos clássicos de caminho mínimo sobre a mesma estrutura de labirinto:

- **BFS (Busca em Largura):** explora o grafo camada por camada usando uma fila (`deque`). Garante o caminho com o **menor número de passos**, ignorando os pesos das células. Complexidade: O(V + E).

O labirinto é gerado no backend como um grafo representado por **lista de adjacência**. Paredes e bombas não possuem entradas no grafo (intransitáveis). A cada movimento do jogador, o algoritmo é executado novamente e os caminhos são desenhados sobre o mapa em tempo real.

---

## Screenshots


## Instalação

Linguagem: Python 3.10+

**Pré-requisitos:**
- Python 3.10 ou superior instalado

**Comandos:**

```bash
# 1. Entre na pasta do projeto
cd G9_Grafos_PA-26.1

# 2. Crie e ative um ambiente virtual (recomendado)
python -m venv venv

# Linux/macOS:
source venv/bin/activate

# Windows:
venv\Scripts\activate

# 3. Instale a dependência
pip install -r requirements.txt

# 4. Inicie o servidor
python app.py
```

---

## Uso

Após executar `python app.py`, acesse **http://localhost:5000** no navegador.

| Ação | Controle |
|---|---|
| Mover o gatinho | Setas ⬆️⬇️⬅️➡️ ou W / A / S / D |
| Gerar novo labirinto | Botão "Novo Labirinto" |
| Alternar visualização dos caminhos | Botões "Apenas BFS", "Apenas Dijkstra", "Ambos" ou "Ocultar" |

**Objetivo:** levar o gatinho da posição (0,0) até a saída 🐟 em (9,9).

**Tipos de célula:**
- **Chão livre** — transitável
- **Água** 🌊 — transitável
- **Parede** 🧱 — bloqueia o movimento
- **Bomba** 💣 — pisar encerra o jogo imediatamente

O caminho BFS é recalculado a cada passo e atualizados instantaneamente na tela.

---

## Outros

**Estrutura do projeto:**
```
labirinto-rpg/
├── app.py           ← Backend Flask: geração do labirinto, BFS e API REST
├── requirements.txt ← Dependências (apenas Flask)
└── static/
    └── index.html   ← Frontend completo: HTML, CSS e JavaScript em um único arquivo
```
