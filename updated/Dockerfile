FROM python:3.11-alpine

COPY . /updated
WORKDIR /updated

RUN pip3 install -r requirements.txt
CMD ["python3", "main.py"]
