FROM python:3.10-bullseye

RUN apt update \
  && apt install build-dep \
  && rm -rf /var/lib/apt/lists/ \
  && pip3 install -r requirements.txt

COPY . /nyup
WORKDIR /nyup

ENV DEBUG=0
ENV SECRET_KEY=$SECRET_KEY
ENV API_KEY=$API_KEY
ENV POSTGRES_URL=$POSTGRES_URL
ENV DISCORD=$DISCORD

CMD gunicorn -b 0.0.0.0:5000 -w 8 main:app
