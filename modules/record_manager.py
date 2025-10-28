# -*- coding: utf-8 -*-
def normalize_text(text: str):
    if not text: return None
    t = text.strip().upper()
    m = {"莊":"B","B":"B","閒":"P","閑":"P","P":"P","和":"T","T":"T"}
    return m.get(t)

def stats_from(history):
    return {
        "b": history.count("B"),
        "p": history.count("P"),
        "t": history.count("T"),
        "total": len(history)
    }

def route_labels(history):
    label = {"B":"莊","P":"閒","T":"和"}
    return [label[x] for x in history[-40:]]

def settle_profit(bet_on: str|None, actual: str, units: int, commission: dict):
    if bet_on is None:  # 沒下注
        return 0.0
    if actual == 'T':
        # 押和才算中
        return units * commission.get("tie", 8.0) if bet_on == 'T' else 0.0
    # 否則 B/P
    if bet_on == actual:
        mult = commission["banker"] if bet_on == 'B' else commission["player"]
        return units * mult
    else:
        return -1.0 * units
