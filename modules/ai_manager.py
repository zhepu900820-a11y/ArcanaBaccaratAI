# -*- coding: utf-8 -*-
def _recent_stats(history, N):
    last = history[-N:]
    b = last.count('B'); p = last.count('P')
    total = max(b + p, 1)
    pb = b / total
    pp = p / total
    return pb, pp

def _streak_score(history):
    if len(history) < 3: return 0.0, 0.0
    s = 1
    for i in range(len(history)-2, -1, -1):
        if history[i] == history[i+1]:
            s += 1
        else:
            break
    last = history[-1]
    if last == 'B': return 0.7 + min(s,5)*0.06, 0.3
    if last == 'P': return 0.3, 0.7 + min(s,5)*0.06
    return 0.5, 0.5

def _zigzag_score(history):
    # 最近是否明顯對跳
    if len(history) < 6: return 0.5, 0.5
    seq = [x for x in history if x in ('B','P')]
    if len(seq) < 6: return 0.5, 0.5
    ok = all(seq[i] != seq[i-1] for i in range(-1, -6, -1))  # 最近5次都對跳
    if not ok: return 0.5, 0.5
    # 若最近對跳，下一手傾向反向（回歸）
    last = seq[-1]
    if last == 'B': return 0.45, 0.55
    else: return 0.55, 0.45

def predict_choice(history, ai_cfg):
    N = ai_cfg.get("recent_N", 20)
    w_base = ai_cfg.get("base_weight", 0.6)
    w_streak = ai_cfg.get("streak_weight", 0.2)
    w_zigzag = ai_cfg.get("zigzag_weight", 0.2)

    pb, pp = _recent_stats(history, N)
    sb, sp = _streak_score(history)
    zb, zp = _zigzag_score(history)

    wb = w_base*pb + w_streak*sb + w_zigzag*zb
    wp = w_base*pp + w_streak*sp + w_zigzag*zp

    # 小型貝葉斯平滑
    alpha = 1.5; beta = 1.5
    wb = (wb*10 + alpha) / (10 + alpha + beta)
    wp = (wp*10 + alpha) / (10 + alpha + beta)

    choice = 'B' if wb > wp else 'P'
    conf = abs(wb - wp) + 0.5 * max(wb, wp)  # 0~1 之間
    conf = max(0.0, min(conf, 1.0))

    label = {'B':'莊', 'P':'閒'}
    return {"choice": choice, "confidence": round(conf, 2), "reason": f"綜合近況/型態，傾向{label[choice]}"}
