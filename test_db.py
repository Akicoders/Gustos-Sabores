import pymysql

try:
    conn = pymysql.connect(
        host="gateway01.us-east-1.prod.aws.tidbcloud.com",
        port=4000,
        user="35KnDVzHdH1exok.root",
        password="0mIVPMrMMg6BO0La",
        database="gustos_db",
        ssl={"ssl_mode": "VERIFY_IDENTITY"}
    )
    print("Conexión exitosa a TiDB!")
    conn.close()
except Exception as e:
    print(f"Error conectando: {e}")
