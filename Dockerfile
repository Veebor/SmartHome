FROM python:3.7

ADD GUI /gui

ADD cert.pem cert.pem

ADD privkey.pem privkey.pem

RUN pip install tornado

EXPOSE 8080

CMD ["python", "/gui/test.py"]
