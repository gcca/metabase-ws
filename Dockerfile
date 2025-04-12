FROM python:3.13-alpine

WORKDIR /app

COPY . .

RUN python3 -m venv /venv \
    && . /venv/bin/activate \
    && pip install --upgrade pip \
    && pip install -r requirements.txt

EXPOSE 8000

CMD ["/venv/bin/sanic", "metabase-ws", "-H0.0.0.0"]
