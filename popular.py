import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime, timedelta
import oracledb
import os
import sys
import logging
import threading
import time
import tkinter as tk
from tkinter import messagebox
from tkcalendar import DateEntry

# ========================
# BASE DIR (PY vs EXE)
# ========================
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

LIB_DIR = os.path.join(BASE_DIR, "instantclient_19_19")

# ========================
# ORACLE THICK CLIENT
# ========================
try:
    oracledb.init_oracle_client(lib_dir=LIB_DIR)
except Exception as e:
    messagebox.showerror("Startup Error", f"Oracle client error:\n{e}")
    sys.exit(1)

# ========================
# FILES
# ========================
SYNC_FILE = os.path.join(BASE_DIR, "last_sync.txt")
LOG_FILE = os.path.join(BASE_DIR, "attendance_sync.log")
SCHEDULE_FILE = os.path.join(BASE_DIR, "schedule.txt")

# ========================
# CONFIG
# ========================
BIOTIME_IP = "192.168.199.35"
PORT = 8080
USERNAME = "xactidea"
PASSWORD = "xactidea@123"
API_URL = f"http://{BIOTIME_IP}:{PORT}/iclock/api/transactions/"

ORA_USER = "ideapopular"
ORA_PASS = "XIPOPULAR#2126#"
ORA_DSN = "192.168.199.121:1521/orclpdb"

PAGE_SIZE = 200
SCHEDULE_CHECK_INTERVAL = 300  # seconds
OVERLAP_MINUTES = 3

# ========================
# LOGGING
# ========================
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

# ========================
# HELPERS
# ========================
def safe_int(val):
    try:
        return int(val)
    except:
        return None

# ========================
# FETCH AND INSERT
# ========================
# ========================
def fetch_and_insert(start_time, end_time):
    """Fetch data from Biotime API and insert into Oracle"""
    rows = []
    page = 1
    try:
        while True:
            r = requests.get(
                API_URL,
                auth=HTTPBasicAuth(USERNAME, PASSWORD),
                params={
                    "page": page,
                    "page_size": PAGE_SIZE,
                    "start_time": start_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "end_time": end_time.strftime("%Y-%m-%d %H:%M:%S")
                },
                timeout=300
            )
            r.raise_for_status()
            data = r.json().get("data", [])
            if not data:
                break

            for d in data:
                card_no = d.get("card_no")
                # Use card_no as EMP_ID
                if not card_no or str(card_no).strip() == "":
                    emp_id = d.get("emp_code")
                else:
                    emp_id = card_no

                # rows.append((
                #     emp_id,
                #     d.get("punch_time"),
                #     safe_int(d.get("terminal_sn")),
                #     safe_int(d.get("verify_type")),
                #     1
                # ))
                rows.append((
                    emp_id,
                    d.get("punch_time"),
                    safe_int(d.get("terminal_sn")),
                    3,  #  punch type
                    334  # device type
                ))

            if not r.json().get("next"):
                break
            page += 1

        if rows:
            conn = oracledb.connect(user=ORA_USER, password=ORA_PASS, dsn=ORA_DSN)
            cur = conn.cursor()
            cur.executemany("""
                INSERT INTO HRM_RAWDATA_OLD
                (EMP_ID, RAW_DATA, MACHINE_ID, PUNCH_TYPE, DEVICE_TYPE)
                VALUES (:1, :2, :3, :4, :5)
            """, rows)
            conn.commit()
            cur.close()
            conn.close()

        # Save last sync time
        with open(SYNC_FILE, "w") as f:
            f.write(end_time.strftime("%Y-%m-%d %H:%M:%S"))

        return len(rows)
    except Exception as e:
        logging.error(f"Error during fetch and insert: {e}")
        return 0

# ========================
# SPINNER
# ========================
def show_loader():
    global spinner_angle
    spinner_angle = 0
    spinner.place(relx=0.5, rely=0.72, anchor="center")
    animate_spinner()

def hide_loader():
    spinner.place_forget()

def animate_spinner():
    global spinner_angle
    spinner.delete("all")
    spinner.create_arc(
        10, 10, 70, 70,
        start=spinner_angle,
        extent=270,
        outline="#00FFAA",
        width=5,
        style="arc"
    )
    spinner_angle = (spinner_angle - 10) % 360
    root.after(40, animate_spinner)

# ========================
# THREAD WRAPPER
# ========================
def run_task(start_time, end_time, show_msg=True):
    try:
        count = fetch_and_insert(start_time, end_time)
        if show_msg:
            root.after(0, lambda: messagebox.showinfo("Success", f"{count} records inserted"))
    except Exception as e:
        root.after(0, lambda: messagebox.showerror("Error", str(e)))
    finally:
        root.after(0, finish_task)

def finish_task():
    hide_loader()
    btn_manual.config(state="normal")
    if not auto_running:
        btn_auto.config(state="normal")

# ========================
# MANUAL BUTTON
# ========================
def manual_sync():
    btn_auto.config(state="disabled")
    btn_manual.config(state="disabled")
    show_loader()
    start_time = datetime.strptime(from_entry.get(), "%d/%m/%Y")
    end_time = datetime.strptime(to_entry.get(), "%d/%m/%Y") + timedelta(days=1)
    threading.Thread(target=run_task, args=(start_time, end_time), daemon=True).start()

# ========================
# SCHEDULE READER
# ========================
def read_schedule():
    if not os.path.exists(SCHEDULE_FILE):
        return []
    with open(SCHEDULE_FILE, "r") as f:
        lines = f.read().splitlines()
    return [line.strip() for line in lines if line.strip()]

def time_to_datetime(time_str):
    now = datetime.now()
    hour, minute = map(int, time_str.split(":"))
    return now.replace(hour=hour, minute=minute, second=0, microsecond=0)

# ========================
# GUI STATUS LABEL
# ========================
def update_status(text):
    # Thread-safe update of last scheduler log
    root.after(0, lambda: status_label.config(text=text))

# ========================
# SCHEDULED LOGGED SYNC
# ========================
def run_scheduled_sync(start_time, end_time, schedule_time_str):
    """Fetch data and log with schedule info"""
    start_msg = f"[SCHEDULED {schedule_time_str}] Starting scheduled sync"
    logging.info(start_msg)
    update_status(start_msg)  # show in GUI

    try:
        count = fetch_and_insert(start_time, end_time)
        done_msg = f"[SCHEDULED {schedule_time_str}] Inserted {count} records from {start_time} to {end_time}"
        logging.info(done_msg)
        update_status(done_msg)  # always show last scheduler log
    except Exception as e:
        error_msg = f"[SCHEDULED {schedule_time_str}] Error: {e}"
        logging.error(error_msg)
        update_status(error_msg)

# ========================
# AUTO SCHEDULER (CROSS-DAY)
# ========================

auto_running = False
last_run = set()

def auto_scheduler_loop():
    global last_run

    while auto_running:
        run_times = read_schedule()
        now = datetime.now()
        today_str = now.strftime("%Y-%m-%d")
        yesterday = now - timedelta(days=1)
        yesterday_str = yesterday.strftime("%Y-%m-%d")

        # Sort schedule times
        sorted_times = sorted(run_times)

        for i, t_str in enumerate(sorted_times):
            try:
                hour, minute = map(int, t_str.split(":"))
            except:
                continue

            run_dt = now.replace(hour=hour, minute=minute, second=0, microsecond=0)

            if now < run_dt:
                continue

            key = f"{today_str}_{t_str}"

            if key not in last_run:
                last_run.add(key)

                # ==========================
                # CROSS-DAY BLOCK LOGIC
                # ==========================

                if i == 0:
                    # First schedule of today
                    # Start from yesterday's LAST schedule time
                    if sorted_times:
                        last_time_yesterday = sorted_times[-1]
                        prev_hour, prev_minute = map(int, last_time_yesterday.split(":"))

                        start_time = yesterday.replace(
                            hour=prev_hour,
                            minute=prev_minute,
                            second=0,
                            microsecond=0
                        )
                    else:
                        start_time = run_dt.replace(hour=0, minute=0, second=0)

                else:
                    # Normal block continuation
                    prev_time_str = sorted_times[i - 1]
                    prev_hour, prev_minute = map(int, prev_time_str.split(":"))

                    start_time = run_dt.replace(
                        hour=prev_hour,
                        minute=prev_minute,
                        second=0,
                        microsecond=0
                    )

                end_time = run_dt

                logging.info(f"[AUTO {t_str}] Sync {start_time} → {end_time}")

                threading.Thread(
                    target=run_scheduled_sync,
                    args=(start_time, end_time, t_str),
                    daemon=True
                ).start()

        time.sleep(SCHEDULE_CHECK_INTERVAL)

def toggle_auto(event=None):
    global auto_running
    if not auto_running:
        auto_running = True
        btn_auto.config(text="STOP AUTO")
        threading.Thread(target=auto_scheduler_loop, daemon=True).start()
        logging.info("Auto scheduler started")
    else:
        stop_auto()

def stop_auto(event=None):
    global auto_running
    if auto_running:
        auto_running = False
        btn_auto.config(text="AUTO")
        logging.info("Auto scheduler stopped")

# ========================
# GUI
# ========================

root = tk.Tk()
root.title("Popular Attendance")
root.geometry("650x260")
root.configure(bg="#1E1E2F")

tk.Label(root, text="From Date", bg="#1E1E2F", fg="white",
         font=("Helvetica", 12, "bold")).grid(row=0, column=0, padx=110, pady=15)
tk.Label(root, text="To Date", bg="#1E1E2F", fg="white",
         font=("Helvetica", 12, "bold")).grid(row=0, column=1, padx=110, pady=15)

from_entry = DateEntry(root, width=15, date_pattern="dd/mm/yyyy")
from_entry.grid(row=1, column=0, padx=90)
to_entry = DateEntry(root, width=15, date_pattern="dd/mm/yyyy")
to_entry.grid(row=1, column=1, padx=90)

btn_auto = tk.Button(root, text="AUTO", bg="#28A745", fg="white", font=("Helvetica", 12, "bold"))
btn_auto.grid(row=2, column=0, padx=(110, 10), pady=15, sticky="ew")
btn_auto.bind("<Button-1>", toggle_auto)
btn_auto.bind("<Double-1>", stop_auto)

btn_manual = tk.Button(root, text="MANUAL", bg="#007BFF", fg="white",
                       font=("Helvetica", 12, "bold"), command=manual_sync)
btn_manual.grid(row=2, column=1, padx=(10, 110), pady=15, sticky="ew")

spinner = tk.Canvas(root, width=80, height=80, bg="#1E1E2F", highlightthickness=0)

# ====== STATUS LABEL ======
status_label = tk.Label(root, text="", bg="#1E1E2F", fg="white",
                        font=("Helvetica", 10), anchor="w", justify="left")
status_label.grid(row=3, column=0, columnspan=2, padx=20, pady=5, sticky="ew")

root.mainloop()
