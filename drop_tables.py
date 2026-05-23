import pymysql

conn = pymysql.connect(
    host="gateway01.us-east-1.prod.aws.tidbcloud.com",
    port=4000,
    user="35KnDVzHdH1exok.root",
    password="0mIVPMrMMg6BO0La",
    database="gustos_db",
    ssl={"ssl_mode": "VERIFY_IDENTITY"}
)
cursor = conn.cursor()
cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
cursor.execute("SHOW TABLES;")
tables = cursor.fetchall()
for table in tables:
    cursor.execute(f"DROP TABLE IF EXISTS {table[0]};")
cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
conn.commit()
print("All tables dropped.")
conn.close()
