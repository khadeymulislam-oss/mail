from flask import Flask, request, jsonify
from flask_cors import CORS
import smtplib
import base64
import oracledb
from email.message import EmailMessage
from datetime import datetime

app = Flask(__name__)
# cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
cors = CORS(app, resources={r"/styleinfo": {"origins": "*"}, r"/api/*": {"origins": "*"}})

SMTP_USERNAME = ''
SMTP_PASSWORD = ''

DB_USER = ""
DB_PASS = ""
DB_DSN = "10.251.182.183:1521/ORCLPDB"



def check_username_password(username, password):
    conn = oracledb.connect(
        user=DB_USER,
        password=DB_PASS,
        dsn=DB_DSN
    )

    try:
        cursor = conn.cursor()

        sql = """
            SELECT count(*)
            FROM user_tbl
            WHERE user_name = :P_USER_NAME
              AND pass_word = HASHMD5(:P_PASSWORD)
        """

        cursor.execute(sql, {
            "P_USER_NAME": username,
            "P_PASSWORD": password
        })

        result = cursor.fetchone()
        return result[0] if result[0] else 0

    finally:
        cursor.close()
        conn.close()

# def styleInformation(from_date, to_date):
#     conn = oracledb.connect(user=DB_USER, password=DB_PASS, dsn=DB_DSN)   
#     try:
#         with conn.cursor() as cursor:
#             sql = '''   SELECT DATA_STATUS,
#          STYLE_RPT_STATUS,
#          UNIT,
#          COMPANY_UNIT,
#          R_ADD_LOCATION,
#          OUR_REF_ID,
#          BULLETIN_NO,
#          ACTIVE_STATUS,
#          LINE_NAME,
#          PLANNED_EFF,
#          R_SMV,
#          SMV_ID,
#          R_PID_01,
#          GMT_QTY,
#          GMT_ITEM,
#          G_ITEM_CODE,
#          BUYER_SEASON_ID,
#          SEASON_CODE,
#          SEASON_DETAIL,
#          CONF_ORDER_DATE,
#          TAG_DATE,
#          TAG_BY,
#          NO_OF_USES,
#          ORDER_TYPE,
#          ORDER_LEAD_TIMES,
#          BULK_OFFER_QTY,
#          MASTER_STYLE_NO,
#          STYLE_DESCRIPTION,
#          BUYER_BRAND,
#          R_BODY_WASH_COLOR,
#          GMT_ITEM_ID,
#          ORDER_UOM_ID,
#          MERCHANDISER_LEADER_ID,
#          MERCHANT_TEAM_LEADER,
#          FABRIC_ID,
#          CAD_NO,
#          CAD_ID,
#          CAD_SUBMIT_DATE,
#          UNIT_FULL_NAME,
#          R_LOCATION_ID,
#          UNIT_MS,
#          FAB_DETAIL,
#          SAM_DEV,
#          SAMPLE_DEV_MERCHANT_ID,
#          BUYER_CODE,
#          BULLETIN_DATE,
#          BULLETIN_SUB_DATE,
#          R_USER_ID,
#          ROW_STATUS_CDT,
#          CHK_MATCH_PARAM_ID,
#          SUB_BY_ID,
#          SUB_DATE,
#          SUBMITTED_BY,
#          INQUERY_DATE,
#          TARGET_PRICE,
#          PRIORITY_LEVEL,
#          QUOT_SUB_DATE,
#          SAMPL_SUB_DATE,
#          R_FABRIC_TYPE,
#          COLOR_TYPE_ID,
#          COLOR_TYPE,
#          DESIGN,
#          QUALITY,
#          SAM_CNT,
#          REF_STYLE_ID,
#          ACCEPT_DATE,
#          ACCOUNT_HOLDER_ID,
#          ACTION_BY,
#          ACTION_BY_ID,
#          ACTION_DATE,
#          ACTION_NAME,
#          ACTION_SERIAL,
#          ADJ_MARGIN_PCT,
#          APPROVAL_STATUS,
#          APPROVED_BY,
#          APPROVED_BY_ID,
#          APPROVED_DATE,
#          AUDIT_RCV_STATUS,
#          CBU,
#          CM,
#          COMM_TYPE,
#          COMMERCIAL_COST_PCT,
#          COST_TYPE,
#          QTN_CREATOR,
#          CREATOR_ID,
#          CURR_ID,
#          CURR_RATE,
#          QTN_DELIVERY_DATE,
#          QTN_ENT_DATE,
#          EST_QTY,
#          F_COMM_PC,
#          F_COMM_VAL,
#          FIRST_DEL,
#          Q_GMT_ITEM_NAME,
#          Q_GMT_TYPE,
#          GROSS_FOB,
#          L_COMM_PC,
#          L_COMM_VAL,
#          LINE_COST,
#          NET_FOB,
#          OTHERS_COST,
#          OUR_ID,
#          OUR_REF,
#          OUR_REFS_ID,
#          POSSIBILITIES,
#          PPH_QUOTED,
#          PROFIT_PCT,
#          QUOTATION_DATE,
#          QUOTATION_TYPE,
#          RECOMMEND_BY,
#          RECOMMEND_BY_ID,
#          RECOMMEND_DATE,
#          REPORTING_BOSS_ID,
#          REQ_FOB,
#          SEND_TO_AUDIT_DATE,
#          SHALL_TYPE,
#          STATUS_DESC,
#          SUBMIT_BY_ID,
#          SUBMIT_DATE,
#          TARGET_FOB,
#          STYLE_REFERENCE,
#          DEPARTMENT,
#          SIZE_RANGE,
#          PROJECTED_QUANTITY,
#          SEASON,
#          PID_02,
#          DEL_DT,
#          PO_NUMBER,
#          PO_QTY,
#          PO_RCV_DATE,
#          SIZE_NAME,
#          COLOR_NAME,
#          SIZE_QTY,
#          BUYER_RATE,
#          FACTORY_RATE,
#          SHIP_CLEARENCE_DATE,
#          PUBLISH_SHIP_DATE,
#          SUPPLIER_NAME,
#          SUPPLIER_ID,
#          FABRIC_ITEM_ID,
#          ITEM_HEAD,
#          ITEM_DESC,
#          WIDTH,
#          USED_PLACE,
#          FABRIC_CODE,
#          FABRIC_NAME,
#          NOTES,
#          FABRIC_SUPPLIER_ID,
#          FABRIC_SUPPLIER_NAME,
#          FABRIC_SUPPLIER_SHORT_NAME,
#          NOMINEE_STATUS,
#          NAME_ST_ID,
#          ACT_CONSUMP,
#          WASTAGE_PC,
#          TOTAL_CONSUMP,
#          UNIT_ID,
#          UNIT_NAME,
#          UNIT_RATE,
#          QUOTED_RATE,
#          SHRINKAGE_PCT,
#          CON_YM,
#          PRICE_YM,
#          FRAC_FACTOR,
#          ACTUAL_QTY,
#          REQ_FINISH,
#          WASTAGE_PC_YARN,
#          GSM,
#          FC_PER,
#          FABRICATION,
#          COMPOSITION,
#          NET_COST,
#          OFFER_PRICE,
#          MARGIN,
#          G_PIC IMAGE
#     FROM STYLE_API_VU
#    WHERE INQUERY_DATE >= :from_date AND INQUERY_DATE <= :TO_DATE
# ORDER BY OUR_REF_ID
#             '''
#             cursor.execute(sql, from_date=from_date, to_date=to_date) 
#             columns = [col[0] for col in cursor.description]            
#             results = [dict(zip(columns, row)) for row in cursor.fetchall()]            
#             return results
#     finally:
#         conn.close() 

def ourRefInformationBr(from_date, to_date):
    conn = oracledb.connect(user=DB_USER, password=DB_PASS, dsn=DB_DSN)   
    try:
        with conn.cursor() as cursor:
            sql = '''SELECT*
                     FROM VU_OUR_REF_SCBD_API
                     WHERE INQUERY_DATE >= :from_date AND SHIP_CLEARENCE_DATE <= :to_date
                     ORDER BY OUR_REF'''
            
            cursor.execute(sql, from_date=from_date, to_date=to_date) 
            columns = [col[0] for col in cursor.description]            
            
            results = []
            for row in cursor.fetchall():
                row_dict = dict(zip(columns, row))
                
                # Check if G_PIC exists and is not None
                if row_dict.get('G_PIC'):
                    try:
                        # Read the BLOB and encode to Base64 string
                        image_data = row_dict['G_PIC'].read()
                        row_dict['G_PIC'] = base64.b64encode(image_data).decode('utf-8')
                    except Exception:
                        row_dict['G_PIC'] = None # Fallback if read fails
                
                results.append(row_dict)
                
            return results
    finally:
        conn.close() 
        
def styleInformationBr(from_date, to_date):
    conn = oracledb.connect(user=DB_USER, password=DB_PASS, dsn=DB_DSN)   
    try:
        with conn.cursor() as cursor:
            sql = '''SELECT*
                     FROM STYLE_API_VU_DETAILS_BR
                     WHERE SHIP_CLEARENCE_DATE >= :from_date AND SHIP_CLEARENCE_DATE <= :to_date
                     ORDER BY OUR_REF_ID'''
            
            cursor.execute(sql, from_date=from_date, to_date=to_date) 
            columns = [col[0] for col in cursor.description]            
            
            results = []
            for row in cursor.fetchall():
                row_dict = dict(zip(columns, row))
                
                # Check if G_PIC exists and is not None
                if row_dict.get('G_PIC'):
                    try:
                        # Read the BLOB and encode to Base64 string
                        image_data = row_dict['G_PIC'].read()
                        row_dict['G_PIC'] = base64.b64encode(image_data).decode('utf-8')
                    except Exception:
                        row_dict['G_PIC'] = None # Fallback if read fails
                
                results.append(row_dict)
                
            return results
    finally:
        conn.close() 
    
def poWiseShipped(from_date, to_date):
    conn = oracledb.connect(user=DB_USER, password=DB_PASS, dsn=DB_DSN)   
    try:
        with conn.cursor() as cursor:
            sql = '''  SELECT SUM (NVL (d1.EXP_QTY, 0))                         Shiped_qty,
                                    SUM ((NVL (d1.FOB, 0) * NVL (d1.EXP_QTY, 0)))     Shiped_value,
                                    s.lot_no PO_NO
                                FROM data71 d,
                                    data72 d1,
                                    (SELECT d2.pid, o.LOCATION_ID, lot_no
                                        FROM DATA01 D1, DATA02 D2, our_refs o
                                    WHERE D1.PID = D2.PID_01 AND D1.OUR_REF_ID = o.ID) s
                            WHERE     d.pid = d1.PID_71
                                    AND d1.PID_02 = s.PID
                                    AND  EX_FACT_DT >= :from_date AND EX_FACT_DT <= :to_date
                            GROUP BY  s.lot_no
                            '''
            
            cursor.execute(sql, from_date=from_date, to_date=to_date) 
            columns = [col[0] for col in cursor.description]            
            
            results = []
            for row in cursor.fetchall():
                row_dict = dict(zip(columns, row))
                
                # Check if G_PIC exists and is not None
                if row_dict.get('G_PIC'):
                    try:
                        # Read the BLOB and encode to Base64 string
                        image_data = row_dict['G_PIC'].read()
                        row_dict['G_PIC'] = base64.b64encode(image_data).decode('utf-8')
                    except Exception:
                        row_dict['G_PIC'] = None # Fallback if read fails
                
                results.append(row_dict)
                
            return results
    finally:
        conn.close() 
        

def styleInformation(from_date, to_date):
    conn = oracledb.connect(user=DB_USER, password=DB_PASS, dsn=DB_DSN)   
    try:
        with conn.cursor() as cursor:
            sql = '''SELECT DATA_STATUS, STYLE_RPT_STATUS, UNIT, COMPANY_UNIT, R_ADD_LOCATION, 
                            OUR_REF_ID, BULLETIN_NO, ACTIVE_STATUS, LINE_NAME, PLANNED_EFF, 
                            R_SMV, SMV_ID, R_PID_01, GMT_QTY, GMT_ITEM, G_ITEM_CODE, 
                            BUYER_SEASON_ID, SEASON_CODE, SEASON_DETAIL, CONF_ORDER_DATE, 
                            TAG_DATE, TAG_BY, NO_OF_USES, ORDER_TYPE, ORDER_LEAD_TIMES, 
                            BULK_OFFER_QTY, MASTER_STYLE_NO, STYLE_DESCRIPTION, BUYER_BRAND, 
                            R_BODY_WASH_COLOR, GMT_ITEM_ID, ORDER_UOM_ID, MERCHANDISER_LEADER_ID, 
                            MERCHANT_TEAM_LEADER, FABRIC_ID, CAD_NO, CAD_ID, CAD_SUBMIT_DATE, 
                            UNIT_FULL_NAME, R_LOCATION_ID, UNIT_MS, FAB_DETAIL, SAM_DEV, 
                            SAMPLE_DEV_MERCHANT_ID, BUYER_CODE, BULLETIN_DATE, BULLETIN_SUB_DATE, 
                            R_USER_ID, ROW_STATUS_CDT, CHK_MATCH_PARAM_ID, SUB_BY_ID, SUB_DATE, 
                            SUBMITTED_BY, INQUERY_DATE, TARGET_PRICE, PRIORITY_LEVEL, 
                            QUOT_SUB_DATE, SAMPL_SUB_DATE, R_FABRIC_TYPE, COLOR_TYPE_ID, 
                            COLOR_TYPE, DESIGN, QUALITY, SAM_CNT, REF_STYLE_ID, ACCEPT_DATE, 
                            ACCOUNT_HOLDER_ID, ACTION_BY, ACTION_BY_ID, ACTION_DATE, ACTION_NAME, 
                            ACTION_SERIAL, ADJ_MARGIN_PCT, APPROVAL_STATUS, APPROVED_BY, 
                            APPROVED_BY_ID, APPROVED_DATE, AUDIT_RCV_STATUS, CBU, CM, COMM_TYPE, 
                            COMMERCIAL_COST_PCT, COST_TYPE, QTN_CREATOR, CREATOR_ID, CURR_ID, 
                            CURR_RATE, QTN_DELIVERY_DATE, QTN_ENT_DATE, EST_QTY, F_COMM_PC, 
                            F_COMM_VAL, FIRST_DEL, Q_GMT_ITEM_NAME, Q_GMT_TYPE, GROSS_FOB, 
                            L_COMM_PC, L_COMM_VAL, LINE_COST, NET_FOB, OTHERS_COST, OUR_ID, 
                            OUR_REF, OUR_REFS_ID, POSSIBILITIES, PPH_QUOTED, PROFIT_PCT, 
                            QUOTATION_DATE, QUOTATION_TYPE, RECOMMEND_BY, RECOMMEND_BY_ID, 
                            RECOMMEND_DATE, REPORTING_BOSS_ID, REQ_FOB, SEND_TO_AUDIT_DATE, 
                            SHALL_TYPE, STATUS_DESC, SUBMIT_BY_ID, SUBMIT_DATE, TARGET_FOB, 
                            STYLE_REFERENCE, DEPARTMENT, SIZE_RANGE, PROJECTED_QUANTITY, SEASON, 
                            PID_02, DEL_DT, PO_NUMBER, PO_QTY,PO_VALUE, PO_RCV_DATE, SIZE_NAME, COLOR_NAME, 
                            SIZE_QTY, BUYER_RATE, FACTORY_RATE, SHIP_CLEARENCE_DATE, 
                            PUBLISH_SHIP_DATE, SUPPLIER_NAME, SUPPLIER_ID, FABRIC_ITEM_ID, 
                            ITEM_HEAD, ITEM_DESC, WIDTH, USED_PLACE, FABRIC_CODE, FABRIC_NAME, 
                            NOTES, FABRIC_SUPPLIER_ID, FABRIC_SUPPLIER_NAME, FABRIC_SUPPLIER_SHORT_NAME, 
                            NOMINEE_STATUS, NAME_ST_ID, ACT_CONSUMP, WASTAGE_PC, TOTAL_CONSUMP, 
                            UNIT_ID, UNIT_NAME, UNIT_RATE, QUOTED_RATE, SHRINKAGE_PCT, CON_YM, 
                            PRICE_YM, FRAC_FACTOR, ACTUAL_QTY, REQ_FINISH, WASTAGE_PC_YARN, GSM, 
                            FC_PER, FABRICATION, COMPOSITION, NET_COST, OFFER_PRICE, MARGIN,Product_category,Vendor_Name,Customer_Name,Product_Group,
                            G_PIC
                     FROM STYLE_API_VU
                     WHERE SHIP_CLEARENCE_DATE >= :from_date AND SHIP_CLEARENCE_DATE <= :to_date
                     ORDER BY OUR_REF_ID'''
            
            cursor.execute(sql, from_date=from_date, to_date=to_date) 
            columns = [col[0] for col in cursor.description]            
            
            results = []
            for row in cursor.fetchall():
                row_dict = dict(zip(columns, row))
                
                # Check if G_PIC exists and is not None
                if row_dict.get('G_PIC'):
                    try:
                        # Read the BLOB and encode to Base64 string
                        image_data = row_dict['G_PIC'].read()
                        row_dict['G_PIC'] = base64.b64encode(image_data).decode('utf-8')
                    except Exception:
                        row_dict['G_PIC'] = None # Fallback if read fails
                
                results.append(row_dict)
                
            return results
    finally:
        conn.close() 


def basApi(COMPANY, LOCATION, CUSTOMER, DEPARTMENT, TEAM_LEADER, PRODUCT_CLASS, YEAR, BRAND_NAME):
    conn = oracledb.connect(user=DB_USER, password=DB_PASS, dsn=DB_DSN,)   
    try:
        with conn.cursor() as cursor:
            sql = """
                SELECT B.UNIT_NAME           COMPANY,
                    C.LOCATION_NAME       LOCATION,
                    A.CUSTOMER,
                    A.BRAND_NAME,
                    D.BUYER_DEPT_NAME     BUYER_DEPT,
                    U.USER_FULL_NAME      TEAM_LEADER,
                    GBL.NAME              AS PRODUCT_CLASS,
                    A.YEAR,
                    A.LY_TOTAL_SHIPPED,
                    A.TY_SHIPPED,
                    A.TY_ORDER_IN_HAND,
                    A.PIPELINE_VALUE      TY_PIPELINE_VALUE,
                    A.ACHIEVED_TOTAL      YTD_ACHIEVED_TOTAL,
                    A.YTD_VARIANCE_TO_TARGET,
                    A.FURTHER_EXPECTED,
                    A.TY_TOTAL_EXPECTED,
                    A.TARGET_PLAN,
                    A.EXP_VAR_TO_TARGET
                FROM BAS_API_VU             A,
                    UNIT_DEPT_TBL          B,
                    GBL_COMPANY_LOCATIONS  C,
                    BUYER_DEPT_TBL         D,
                    USER_TBL               U,
                    GBL_PRODUCT_CLASS      GBL
                WHERE     A.COMPANY = B.UNIT_DEPT_NO(+)
                    AND A.LOCATION = C.ID(+)
                    AND A.BUYER_DEPT = D.ID(+)
                    AND A.TEAM_LEADER = U.USER_ID(+)
                    AND A.PRODUCT_CLASS = GBL.ID(+)
                    AND NVL (B.UNIT_NAME, '~') =
                        NVL ( :COMPANY, NVL (B.UNIT_NAME, '~'))   
                    AND NVL (C.LOCATION_NAME, '~') =
                        NVL ( :LOCATION, NVL (C.LOCATION_NAME, '~'))    
                    AND NVL (A.CUSTOMER, '~') =
                        NVL ( :CUSTOMER, NVL (A.CUSTOMER, '~'))            
                    AND NVL (D.BUYER_DEPT_NAME, '~') =
                        NVL ( :DEPARTMENT, NVL (D.BUYER_DEPT_NAME, '~'))   
                    AND NVL (U.USER_FULL_NAME, '~') =
                        NVL ( :TEAM_LEADER, NVL (U.USER_FULL_NAME, '~')) 
                    AND NVL (GBL.NAME, '~') =      NVL ( :PRODUCT_CLASS, NVL (GBL.NAME, '~'))           
                    AND NVL (A.YEAR, 0) = NVL ( :YEAR, NVL (A.YEAR, 0))      
                    AND NVL (A.BRAND_NAME, '~') =
                        NVL ( :BRAND_NAME, NVL (A.BRAND_NAME, '~'))      
                   
                     """
            
            cursor.execute(sql,COMPANY=COMPANY, LOCATION=LOCATION, CUSTOMER=CUSTOMER, DEPARTMENT=DEPARTMENT, TEAM_LEADER=TEAM_LEADER, PRODUCT_CLASS=PRODUCT_CLASS, YEAR=YEAR, BRAND_NAME=BRAND_NAME ) 
            columns = [col[0] for col in cursor.description]            
            
            results = []
            for row in cursor.fetchall():
                row_dict = dict(zip(columns, row))               
                results.append(row_dict)
            return results
    finally:
        conn.close() 


def parse_recipients(value):
    if not value:
        return []
    if isinstance(value, list):
        return value
    return [email.strip() for email in value.split(",") if email.strip()]


@app.route("/")
def index():    
    return jsonify({
            "from": "erp@dreussworldwide.com",
            "to": "nannu@xactidea.com",
            "cc":"",
            "bcc":"",
            "subject": "Person wants to meet with you!",
            "body": " wants to meet with  persons.",
            "html_body":"<h1>wants to meet with  persons</h1>"
            })
    
# @app.route("/api/orders", methods=["POST"])
# def orders():
#     username = request.args.get("username")
#     password = request.args.get("password")
#     ch=check_username_password(username, password)
#     if ch == 0:
#         return jsonify({"error": "Unauthorized"}), 401
#     from_date_str = request.args.get("from_date")
#     to_date_str   = request.args.get("to_date")

#     today = datetime.today().date()

#     if from_date_str:
#         from_date = datetime.strptime(from_date_str, "%Y-%m-%d").date()
#     else:
#         from_date = today

#     if to_date_str:
#         to_date = datetime.strptime(to_date_str, "%Y-%m-%d").date()
#     else:
#         to_date = today
#     data = styleInformation(from_date, to_date)
#     return data


@app.route("/api/orders", methods=["POST"])
def orders():
    data = request.get_json()

    username = data.get("username")
    password = data.get("password")

    ch = check_username_password(username, password)
    if ch == 0:
        return jsonify({"error": "Unauthorized"}), 401

    from_date_str = data.get("from_date")
    to_date_str   = data.get("to_date")

    today = datetime.today().date()

    if from_date_str:
        from_date = datetime.strptime(from_date_str, "%Y-%m-%d").date()
    else:
        from_date = today

    if to_date_str:
        to_date = datetime.strptime(to_date_str, "%Y-%m-%d").date()
    else:
        to_date = today

    result = styleInformation(from_date, to_date)
    return jsonify(result)

@app.route("/api/orders_details", methods=["POST"])
def orders_details():
    data = request.get_json()

    username = data.get("username")
    password = data.get("password")

    ch = check_username_password(username, password)
    if ch == 0:
        return jsonify({"error": "Unauthorized"}), 401

    from_date_str = data.get("from_date")
    to_date_str   = data.get("to_date")

    today = datetime.today().date()

    if from_date_str:
        from_date = datetime.strptime(from_date_str, "%Y-%m-%d").date()
    else:
        from_date = today

    if to_date_str:
        to_date = datetime.strptime(to_date_str, "%Y-%m-%d").date()
    else:
        to_date = today

    result = styleInformationBr(from_date, to_date)
    return jsonify(result)

@app.route("/api/style_scbd", methods=["POST"])
def style_scbd():
    data = request.get_json()

    username = data.get("username")
    password = data.get("password")

    ch = check_username_password(username, password)
    if ch == 0:
        return jsonify({"error": "Unauthorized"}), 401

    from_date_str = data.get("from_date")
    to_date_str   = data.get("to_date")

    today = datetime.today().date()

    if from_date_str:
        from_date = datetime.strptime(from_date_str, "%Y-%m-%d").date()
    else:
        from_date = today

    if to_date_str:
        to_date = datetime.strptime(to_date_str, "%Y-%m-%d").date()
    else:
        to_date = today

    result = ourRefInformationBr(from_date, to_date)
    return jsonify(result)

@app.route("/api/po_wise_shipped", methods=["POST"])
def po_wise_shipped():
    data = request.get_json()

    username = data.get("username")
    password = data.get("password")

    ch = check_username_password(username, password)
    if ch == 0:
        return jsonify({"error": "Unauthorized"}), 401

    from_date_str = data.get("from_date")
    to_date_str   = data.get("to_date")

    today = datetime.today().date()

    if from_date_str:
        from_date = datetime.strptime(from_date_str, "%Y-%m-%d").date()
    else:
        from_date = today

    if to_date_str:
        to_date = datetime.strptime(to_date_str, "%Y-%m-%d").date()
    else:
        to_date = today

    result = poWiseShipped(from_date, to_date)
    return jsonify(result)

@app.route("/api/bas", methods=["POST"])
def bas():
    data = request.get_json()

    username = data.get("username")
    password = data.get("password")

    ch = check_username_password(username, password)
    if ch == 0:
        return jsonify({"error": "Unauthorized"}), 401

    COMPANY = data.get("COMPANY")   
    LOCATION = data.get("LOCATION")   
    CUSTOMER = data.get("CUSTOMER")   
    DEPARTMENT = data.get("DEPARTMENT")   
    TEAM_LEADER = data.get("TEAM_LEADER")   
    PRODUCT_CLASS = data.get("PRODUCT_CLASS")   
    YEAR = data.get("YEAR")   
    BRAND_NAME = data.get("BRAND_NAME") 
     
    result = basApi(COMPANY=COMPANY, LOCATION=LOCATION, CUSTOMER=CUSTOMER, DEPARTMENT=DEPARTMENT, TEAM_LEADER=TEAM_LEADER, PRODUCT_CLASS=PRODUCT_CLASS, YEAR=YEAR, BRAND_NAME=BRAND_NAME)
    return jsonify(result)

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
            
        with smtplib.SMTP("smtp.office365.com", 587) as smtp:
            smtp.starttls()
            smtp.login(SMTP_USERNAME, SMTP_PASSWORD)
            smtp.send_message(msg, from_addr=SMTP_USERNAME, to_addrs=all_recipients)

        return jsonify({"success": True, "message": "Email sent successfully"})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# if __name__ == "__main__":    
#     app.run(debug=True)
    
if __name__ == "__main__":
    app.run(host='54.251.182.183', port=5000, debug=True)
