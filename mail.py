from flask import Flask, request, jsonify
import smtplib
from email.message import EmailMessage

app = Flask(__name__)


GMAIL_USER = "hris@xyz.com"
GMAIL_APP_PASSWORD = "1582 ruls udqu rzig"  

def parse_recipients(value):  
    if not value:
        return []
    if isinstance(value, list):
        return value   
    return [email.strip() for email in value.split(",") if email.strip()]

@app.route("/sendmail", methods=["POST"])
def sendmail():
    try:
        data = request.get_json(force=True)
        from_addr  = data.get("from") or GMAIL_USER  
        to_list    = parse_recipients(data.get("to"))
        cc_list    = parse_recipients(data.get("cc"))
        bcc_list   = parse_recipients(data.get("bcc"))
        subject    = data.get("subject", "(no subject)")
        body_text  = data.get("body", "")
        body_html  = data.get("html_body")  
        if not to_list:
            return jsonify({"success": False, "error": "Missing 'to' field"}), 400       
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"]    = from_addr
        msg["To"]      = ", ".join(to_list)
        if cc_list:
            msg["Cc"]  = ", ".join(cc_list)
        if bcc_list:
            msg["Bcc"] = ", ".join(bcc_list)
        
        if body_html:           
            msg.set_content(body_text or "Your email client does not support HTML.")
            msg.add_alternative(body_html, subtype="html")
        else:
            msg.set_content(body_text or "")
        all_recipients = to_list + cc_list + bcc_list
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(GMAIL_USER, GMAIL_APP_PASSWORD)
            smtp.send_message(msg, from_addr=GMAIL_USER, to_addrs=all_recipients)
            
        return jsonify({"success": True, "message": "Email sent successfully"})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
