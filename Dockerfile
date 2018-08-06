FROM python:3.7

ADD GUI /gui

RUN pip install tornado

EXPOSE 8080

CMD ["python", "/gui/test.py"]
