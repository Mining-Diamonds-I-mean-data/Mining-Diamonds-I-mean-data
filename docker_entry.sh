python3 -m venv venv
source venv/bin/activate
pip install wheel
pip install gunicorn flask
pip install -r requirements.txt
gunicorn --bind 0.0.0.0:6969 wsgi:app