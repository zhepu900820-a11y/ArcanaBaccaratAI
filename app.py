# -*- coding: utf-8 -*-
import json, datetime
from flask import Flask, request, jsonify, render_template, session, redirect, url_for

app = Flask(__name__)
app.secret_key = "change-me-in-production"

# === 讀取設定 ===
with open("config.json", "r", encoding="utf-8") as f:
    CFG = json.load(f)

# === 模組 ===
from modules.ai_manager import predict_choice
from modules.strategy_manager import next_stake_and_strategy, reset_strategy_state
from modules.record_manager import normalize_text, stats_from, route_labels, settle_profit
from modules.member_manager import USERS, get_user, require_login, login_user, logout_user
from modules.report_manager import daily_summary

# =============== 路由（頁面） ===============
@app.before_request
def guard():
    # 放行的路徑
    ALLOW = {"/login", "/static/", "/api/status", "/api/submit", "/api/clear"}
    if request.path == "/login" or request.path.startswith("/static"):
        return
    # 登入保護
    if request.path in {"/", "/home", "/admin", "/report"} and not get_user():
        return redirect(url_for("login"))

@app.get("/")
def root():
    return redirect(url_for("home"))

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        u = (request.form.get("username") or "").strip()
        p = (request.form.get("password") or "").strip()
        if u in USERS and USERS[u]["password"] == p:
            login_user(u)
            # 初始化 session 狀態
            session.setdefault("history", [])
            session.setdefault("bankroll", 0.0)
            session.setdefault("pnl", 0.0)
            session.setdefault("last_result", None)
            session.setdefault("strategy_state", {"name":"flat","step":1,"win_streak":0,"lose_streak":0})
            return redirect(url_for("home"))
        return render_template("login.html", app_title="登入", error="帳號或密碼錯誤")
    return render_template("login.html", app_title="登入")

@app.get("/logout")
def logout():
    logout_user()
    return redirect(url_for("login"))

@app.get("/home")
def home():
    return render_template("index.html", app_title="Arcana Baccarat AI", user=get_user())

@app.get("/admin")
def admin_page():
    return render_template("admin.html", app_title="後台管理", user=get_user(), users=USERS)

@app.get("/report")
def report_page():
    # 以 session 資料簡單做每日報表（MVP）
    hist = session.get("history", [])
    rep = daily_summary(hist, session.get("pnl", 0.0))
    return render_template("report.html", app_title="報表", user=get_user(), report=rep)

# =============== API ===============
@app.get("/api/status")
def api_status():
    h = session.get("history", [])
    s = stats_from(h)
    # AI 建議
    ai = predict_choice(h, CFG.get("ai", {}))
    # 當前配注（不結算，只提供建議用）
    stake_info = next_stake_and_strategy(session, confidence=ai["confidence"], last_result=session.get("last_result"))
    resp = {
        "ok": True,
        "user": get_user(),
        "stats": s,
        "route": route_labels(h),
        "suggestion": ai,
        "stake": stake_info,
        "pnl": round(session.get("pnl", 0.0), 2),
        "config": CFG
    }
    return jsonify(resp)

@app.post("/api/submit")
def api_submit():
    data = request.get_json(silent=True) or {}
    side = normalize_text(data.get("text",""))
    if not side:
        return jsonify(ok=False, msg="請輸入「莊/閒/和」或 B/P/T"), 400

    # 寫入路單
    h = session.get("history", [])
    h.append(side)
    session["history"] = h

    # AI 建議
    ai = predict_choice(h, CFG.get("ai", {}))

    # 依 AI 信心與策略狀態取得下注單位與策略
    stake_info = next_stake_and_strategy(session, confidence=ai["confidence"], last_result=session.get("last_result"))

    # 假設每手都「下在 AI 建議的方向」，並依實際結果結算盈虧
    # 若要改成「手動選擇下注方向」也很容易：前端送入 bet_on='B'/'P'/'T'
    bet_on = ai["choice"]
    profit = settle_profit(bet_on, side, stake_info["units"], CFG["commission"])
    session["pnl"] = round(session.get("pnl", 0.0) + profit, 2)

    # 更新策略的連贏/連輸狀態
    session["last_result"] = "win" if profit > 0 else ("tie" if profit == 0 else "lose")

    return jsonify(
        ok=True,
        stats=stats_from(h),
        route=route_labels(h),
        suggestion=ai,
        stake=stake_info,
        pnl=round(session["pnl"], 2),
        settled={"bet_on": bet_on, "actual": side, "profit": profit}
    )

@app.post("/api/clear")
def api_clear():
    session["history"] = []
    session["pnl"] = 0.0
    session["last_result"] = None
    reset_strategy_state(session)
    return jsonify(ok=True, stats=stats_from([]), route=[], suggestion=predict_choice([], CFG.get("ai", {})), pnl=0.0)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
