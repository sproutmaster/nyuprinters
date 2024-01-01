FROM python:3.11-bullseye

RUN apt update \
  && rm -rf /var/lib/apt/lists/ \
  && pip3 install -r requirements.txt

COPY . /nyup
WORKDIR /nyup

CMD gunicorn -b 0.0.0.0:5000 -w 8 main:app
