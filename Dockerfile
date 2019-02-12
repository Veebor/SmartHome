FROM python:3.7

ADD GUI /gui

ADD cert.pem cert.pem

ADD privkey.pem privkey.pem

RUN pip install tornado

RUN pip install psycopg2

CMD ["python", "/gui/test.py"]
