# -*- coding: utf-8 -*-
def reset_strategy_state(session):
    session["strategy_state"] = {"name":"flat","step":1,"win_streak":0,"lose_streak":0}

def _cap_units(units, cfg):
    return int(max(1, min(units, cfg["risk"]["unit_max"])))

def next_stake_and_strategy(session, confidence: float, last_result: str|None):
    cfg = session.get("CFG_cache")
    # 將 config 快取在 session，或直接讀 app 層的 CFG 也行
    # 為了簡化，這裡直接從 /api/status 裡 app 層注入（此版本不另外快取）
    # 如果不存在，也給個最小 fallback：
    if not cfg:
        cfg = {
            "ai":{"confidence_threshold":0.6},
            "risk":{"max_lose_streak":3, "unit_max":5}
        }

    st = session.get("strategy_state", {"name":"flat","step":1,"win_streak":0,"lose_streak":0})
    name = st["name"]
    step = st["step"]
    win_s = st["win_streak"]
    lose_s = st["lose_streak"]

    # 更新連勝連敗
    if last_result == "win":
        win_s += 1; lose_s = 0
    elif last_result == "lose":
        lose_s += 1; win_s = 0

    # 風控：連輸過多 → 平注冷卻
    if lose_s >= cfg["risk"]["max_lose_streak"]:
        name, step = "flat", 1

    # 依信心調整策略（高信心走 1324，低信心走 flat）
    if confidence >= cfg["ai"]["confidence_threshold"] and lose_s == 0:
        if name == "flat":
            name, step = "1324", 1
    else:
        name, step = "flat", 1

    # 依策略決定單位
    units = 1
    if name == "flat":
        units = 1
    elif name == "1324":
        seq = [1,3,2,4]
        units = seq[(step-1) % 4]
        # 若上一手贏則 step+1；輸則回到1（此處只依照 last_result 調整視覺上的步階）
        if last_result == "win":
            step = step + 1 if step < 4 else 1
        elif last_result == "lose":
            step = 1

    units = _cap_units(units, cfg)

    st["name"] = name
    st["step"] = step
    st["win_streak"] = win_s
    st["lose_streak"] = lose_s
    session["strategy_state"] = st

    return {"name": name, "step": step, "units": units, "win_streak": win_s, "lose_streak": lose_s}
