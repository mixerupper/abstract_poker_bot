# KQ = "KQ"; KJ = "KJ"; QK = "QK"; QJ = "QJ"; JK = "JK"; JQ = "JQ"
# CARDS_DEALINGS = [KQ, KJ, QK, QJ, JK, JQ]

CHANCE = "CHANCE"

CHECK = "CHECK"
CALL = "CALL"
FOLD = "FOLD"
BET = "BET"


# RESULTS_MAP = {}
# RESULTS_MAP[QK] = -1
# RESULTS_MAP[JK] = -1
# RESULTS_MAP[JQ] = -1
# RESULTS_MAP[KQ] = 1
# RESULTS_MAP[KJ] = 1
# RESULTS_MAP[QJ] = 1

A = 1
B = -A

MAX_HAND_VALUE = 3

def card_dealing(max_hand_value: int = MAX_HAND_VALUE):
    dealings = []
    for i in range(1, max_hand_value+1):
        for j in range(1, max_hand_value+1):
            if j==i:
                continue
            else:
                dealings.append(cards(i, j))
    return dealings

def cards(a: int, b: int):
    return f"{a}.{b}"

def results_map(cards: str):
    a, b = cards.split('.')
    a, b = int(a), int(b)
    if a > b:
        return 1
    if a < b:
        return -1
    else:
        raise(Exception("tied result"))
        return 0

