# -*- coding: utf-8 -*-
def daily_summary(history, pnl: float):
    return {
        "total_hands": len(history),
        "banker": history.count('B'),
        "player": history.count('P'),
        "tie": history.count('T'),
        "pnl": round(pnl, 2)
    }
