# init_db.py —— 建立 SQLite 資料庫與表格
import sqlite3, os

BASE_DIR = os.path.dirname(__file__)
DB_PATH = os.path.join(BASE_DIR, "members.db")

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# 會員表
cur.execute("""
CREATE TABLE IF NOT EXISTS members(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE,
  password TEXT,
  level TEXT DEFAULT 'vip',
  daily_quota INTEGER DEFAULT 9999,
  used_today INTEGER DEFAULT 0,
  last_reset TEXT,
  expire_at TEXT
);
""")

# 紀錄表
cur.execute("""
CREATE TABLE IF NOT EXISTS records(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user TEXT,
  result TEXT,         -- 'B'/'P'/'T'
  created_at TEXT      -- ISO 時間字串
);
""")

conn.commit()
conn.close()
print(f"[db] ready: {DB_PATH}")
