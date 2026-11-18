from functools import lru_cache

PITS_PER_SIDE = 6
STORE = (6, 13)
BOARD_SIZE = 14

def game_over(board):
    return sum(board[0:6]) == 0 or sum(board[7:13]) == 0

def sweep(board):
    b = list(board)
    b[6] += sum(b[0:6])
    b[13] += sum(b[7:13])
    for i in range(6):
        b[i] = 0
        b[i + 7] = 0
    return tuple(b)

def legal_moves(board, player):
    start = 0 if player == 0 else 7
    return [i for i in range(start, start + 6) if board[i] > 0]

def make_move(board, player, pit):
    start = 0 if player == 0 else 7
    if pit not in range(start, start + 6) or board[pit] <= 0:
        raise ValueError("That pit is not a legal move.")

    b = list(board)
    stones = b[pit]
    b[pit] = 0
    pos = pit

    while stones:
        pos = (pos + 1) % BOARD_SIZE
        if pos == STORE[1 - player]:
            continue
        b[pos] += 1
        stones -= 1

    # Capture only when the final stone lands in an empty pit on your side.
    own_start = 0 if player == 0 else 7
    if own_start <= pos < own_start + 6 and b[pos] == 1:
        opposite = 12 - pos
        if b[opposite] > 0:
            b[STORE[player]] += b[opposite] + 1
            b[opposite] = 0
            b[pos] = 0

    extra_turn = pos == STORE[player]
    result = tuple(b)
    if game_over(result):
        result = sweep(result)
    return result, (player if extra_turn else 1 - player), extra_turn

def evaluate(board, root):
    # Terminal score dominates every non-terminal heuristic.
    if game_over(board):
        b = sweep(board)
        return (b[STORE[root]] - b[STORE[1-root]]) * 10000

    store_diff = board[STORE[root]] - board[STORE[1-root]]
    own_start = 0 if root == 0 else 7
    opp_start = 7 if root == 0 else 0
    own_pits = sum(board[own_start:own_start+6])
    opp_pits = sum(board[opp_start:opp_start+6])

    # Stores are most important; remaining stones are a smaller positional signal.
    return store_diff * 12 + (own_pits - opp_pits) * 0.35

def search(board, player, root, depth, alpha, beta):
    if game_over(board):
        return evaluate(board, root)
    if depth <= 0:
        return evaluate(board, root)

    moves = legal_moves(board, player)
    if not moves:
        return evaluate(board, root)

    maximizing = player == root
    best = float("-inf") if maximizing else float("inf")

    # Search promising moves first to improve alpha-beta pruning.
    scored = []
    for pit in moves:
        nb, np, extra = make_move(board, player, pit)
        immediate = evaluate(nb, root)
        scored.append((immediate, pit, nb, np))
    scored.sort(key=lambda x: x[0], reverse=maximizing)

    for _, pit, nb, np in scored:
        value = search(nb, np, root, depth - 1, alpha, beta)
        if maximizing:
            best = max(best, value)
            alpha = max(alpha, best)
        else:
            best = min(best, value)
            beta = min(beta, best)
        if beta <= alpha:
            break
    return best

def explain_move(board, player, pit):
    nb, next_player, extra = make_move(board, player, pit)
    parts = []
    if extra:
        parts.append("Your last stone lands in your store, so you move again.")
    own_start = 0 if player == 0 else 7
    if nb[STORE[player]] > board[STORE[player]]:
        gained = nb[STORE[player]] - board[STORE[player]]
        parts.append(f"Adds {gained} stone(s) to your store.")
    if game_over(nb):
        parts.append("This move ends the game and sweeps remaining stones into the stores.")
    if not parts:
        parts.append("This move improves your projected store advantage after the opponent's best reply.")
    return " ".join(parts)

def top_moves(board, player, depth=10):
    if game_over(board):
        return []
    moves = legal_moves(board, player)
    results = []
    for pit in moves:
        nb, next_player, extra = make_move(board, player, pit)
        score = search(nb, next_player, player, depth - 1,
                       float("-inf"), float("inf"))
        results.append({
            "pit": pit + 1 if player == 0 else 13 - pit,
            "score": round(score, 2),
            "extra_turn": extra,
            "explanation": explain_move(board, player, pit)
        })
    results.sort(key=lambda item: item["score"], reverse=True)
    return results[:3]

def build_board(your_pits, opponent_pits, your_store, opponent_store, player):
    if len(your_pits) != 6 or len(opponent_pits) != 6:
        raise ValueError("Each side must have exactly six pits.")
    values = list(your_pits) + [your_store] + list(reversed(opponent_pits)) + [opponent_store]
    if any(not isinstance(x, int) or x < 0 for x in values):
        raise ValueError("Stone counts must be non-negative whole numbers.")
    if sum(values) == 0:
        raise ValueError("The board cannot be empty.")
    # Player 0 is the bottom/your side; player 1 is the top/opponent side.
    return tuple(values)
