python3.12 -m venv .venv
source .venv/bin/activate

lsof -i :5000

ps aux | grep python


[1] 1332106
[2] 1332107


nohup bash -c "source .venv/bin/activate && export FLASK_APP=app.py && flask run --host=0.0.0.0 --port=5000" > flask_log.txt 2>&1 &nohup python apex.py > apex.log 2>&1 &