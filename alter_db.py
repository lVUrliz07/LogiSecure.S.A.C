import sqlite3

db_path = "c:/Users/skyis/Downloads/logisecure/logisecure.db"
conn = sqlite3.connect(db_path)
c = conn.cursor()
try:
    c.execute("ALTER TABLE usuarios ADD COLUMN totp_secret VARCHAR(32);")
    print("Added totp_secret")
except Exception as e:
    print("Error totp_secret:", e)

try:
    c.execute("ALTER TABLE usuarios ADD COLUMN is_totp_enabled BOOLEAN DEFAULT 0;")
    print("Added is_totp_enabled")
except Exception as e:
    print("Error is_totp_enabled:", e)

conn.commit()
conn.close()
