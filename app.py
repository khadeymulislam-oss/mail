from flask import Flask, request, jsonify
from flask_cors import CORS
import smtplib
import base64
from email.message import EmailMessage

app = Flask(__name__)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
GMAIL_USER = "xyz@gmail.com"
GMAIL_APP_PASSWORD = "app_pasword"

def parse_recipients(value):
    if not value:
        return []
    if isinstance(value, list):
        return value
    return [email.strip() for email in value.split(",") if email.strip()]


@app.route("/")
def index():    
    return jsonify({
            "from": "sum@xyz.com",
            "to": "nanny@zyt.com",
            "cc":"",
            "bcc":"",
            "subject": "Person wants to meet with you!",
            "body": " wants to meet with  persons.",
            "html_body":"<h1>wants to meet with  persons</h1>"
            })
    
@app.route("/sendmail", methods=["POST"])
def sendmail():
    try:
        data = request.get_json(force=True)

        from_addr = data.get("from") or GMAIL_USER
        to_list   = parse_recipients(data.get("to"))
        cc_list   = parse_recipients(data.get("cc"))
        bcc_list  = parse_recipients(data.get("bcc"))
        subject   = data.get("subject", "(no subject)")
        body_text = data.get("body", "")
        body_html = data.get("html_body")
        attachments = data.get("attachments", [])

        if not to_list:
            return jsonify({"success": False, "error": "Missing 'to' field"}), 400

        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = from_addr
        msg["To"] = ", ".join(to_list)

        if cc_list:
            msg["Cc"] = ", ".join(cc_list)
        if bcc_list:
            msg["Bcc"] = ", ".join(bcc_list)

      
        if body_html:
            msg.set_content(body_text or "Your email client does not support HTML.")
            msg.add_alternative(body_html, subtype="html")
        else:
            msg.set_content(body_text)

        
        for file in attachments:
            filename = file.get("filename")
            content = file.get("content")
            mime_type = file.get("mime_type", "application/octet-stream")

            if filename and content:
                maintype, subtype = mime_type.split("/", 1)

                decoded_file = base64.b64decode(content)

                msg.add_attachment(
                    decoded_file,
                    maintype=maintype,
                    subtype=subtype,
                    filename=filename
                )
        

        all_recipients = to_list + cc_list + bcc_list

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(GMAIL_USER, GMAIL_APP_PASSWORD)
            smtp.send_message(msg, from_addr=GMAIL_USER, to_addrs=all_recipients)

        return jsonify({"success": True, "message": "Email sent successfully"})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
