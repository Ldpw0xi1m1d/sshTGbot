FROM python:3.11-alpine

# Установка SSH в Alpine
RUN apk add --no-cache openssh-client

WORKDIR /srvbot

COPY dependencies.txt .
RUN pip install --no-cache-dir -r dependencies.txt

COPY . .

CMD ["python", "srvbot.py"]