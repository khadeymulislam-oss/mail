import json
import base64
import requests
import oracledb
import smtplib
import base64
from email.message import EmailMessage
import time


API_ENDPOINT = "http://192.168.199.121:5000/sendmail"
DB_USER = "IDEAPOPULAR"
DB_PASS = "XIPOPULAR#2126#"
DB_DSN = "192.168.199.121:1521/ORCLPDB"

conn = oracledb.connect(
    user=DB_USER,
    password=DB_PASS,
    dsn=DB_DSN
)

cursor = conn.cursor()

def read_clob(val):
    return val.read() if hasattr(val, "read") else (val or "")

def get_attachments_json(mail_id, cursor):
    sql = """
        SELECT FILENAME, MIME_TYPE, ATTACHMENT
        FROM apex_220200.WWV_FLOW_MAIL_ATTACHMENTS
        WHERE MAIL_ID = :id
    """
    cursor.execute(sql, {'id': mail_id})
    
    attachments = []
    for name, mime_type, blob_data in cursor:
        if blob_data:
            data = blob_data.read()
            base64_body = base64.b64encode(data).decode("utf-8")
        else:
            base64_body = ""
        attachments.append({
            "filename": name,
            "mime_type": mime_type,
            "content": base64_body
        })
    return attachments

def process_mail_queue():
    sql = """
    SELECT  ID, INCLUDES_HTML,MAIL_BCC, MAIL_BODY, MAIL_BODY_HTML, MAIL_CC, MAIL_FROM,  MAIL_SUBJ, MAIL_TO
    FROM apex_220200.WWV_FLOW_MAIL_QUEUE
    ORDER BY ID DESC
    """
    try:
        cursor.execute(sql)
        cols = [c[0] for c in cursor.description]
        
        for row in cursor:
            mail = dict(zip(cols, row))
            mail_id = mail["ID"]
            try:                
                payload = {
                    "from": read_clob(mail["MAIL_FROM"]),
                    "to": read_clob(mail["MAIL_TO"]),
                    "cc": read_clob(mail["MAIL_CC"]),
                    "bcc": read_clob(mail["MAIL_BCC"]),
                    "subject": read_clob(mail["MAIL_SUBJ"]),
                    "body": read_clob(mail["MAIL_BODY"]),
                    "html_body": read_clob(mail["MAIL_BODY_HTML"])
                }
                
                if mail["INCLUDES_HTML"] == 1:
                    payload["attachments"] = get_attachments_json(mail_id, cursor)  
                payload_json = json.dumps(payload)                  
                
                headers = {
                'Content-Type': 'application/json'
                }

                response = requests.request("POST", API_ENDPOINT, headers=headers, data=payload_json)
                # status = response.status_code
                # # print(response)
                # print(response.content)
                # success = json.loads(response.content.decode())["success"]
                # print(success)
                
                data = response.json()
                success = data.get("success")
                status = response.status_code

                print(success)
                if 200 <= status < 300:
                    cursor.execute(
                        "DELETE FROM apex_220200.WWV_FLOW_MAIL_ATTACHMENTS WHERE MAIL_ID = :id",
                        {"id": mail_id}
                    )
                    cursor.execute(
                        "DELETE FROM apex_220200.WWV_FLOW_MAIL_QUEUE WHERE ID = :id",
                        {"id": mail_id}
                    )
                    conn.commit()
                else:
                    print("API Error:", status, response.text)
                    conn.rollback()

            except Exception as e:
                print("Processing Error:", str(e))
                conn.rollback()

    except Exception as e:
        print("Query Error:", str(e))
        conn.rollback()

    # finally:
    #     cursor.close()
    #     conn.close()

if __name__ == "__main__":
    while True:
        print("Proceing...")
        process_mail_queue()
        print("Sleeping 2 minutes...")
        time.sleep(120)   # 120 seconds = 2 minutes

