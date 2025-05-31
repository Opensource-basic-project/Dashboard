import sqlite3

conn = sqlite3.connect("legislation.db")
cur = conn.cursor()

# 진행중 입법예고 확인
print("\n--- 진행중: link_url 비어있는 항목 ---")
cur.execute("SELECT bill_id, bill_name FROM legislation_notices WHERE link_url IS NULL OR link_url = ''")
for row in cur.fetchall():
    print(row)

# 종료된 입법예고 확인
print("\n--- 종료된: link_url 비어있는 항목 ---")
cur.execute("SELECT bill_id, bill_name FROM ended_legislation_notices WHERE link_url IS NULL OR link_url = ''")
for row in cur.fetchall():
    print(row)

# proposal_text도 확인
print("\n--- 진행중: proposal_text 비어있는 항목 ---")
cur.execute("SELECT bill_id, bill_name FROM legislation_notices WHERE proposal_text IS NULL OR proposal_text = ''")
for row in cur.fetchall():
    print(row)

print("\n--- 종료된: proposal_text 비어있는 항목 ---")
cur.execute("SELECT bill_id, bill_name FROM ended_legislation_notices WHERE proposal_text IS NULL OR proposal_text = ''")
for row in cur.fetchall():
    print(row)

conn.close()
