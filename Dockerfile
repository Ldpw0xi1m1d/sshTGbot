FROM python:3.11-alpine

RUN apk add --no-cache openssh-client

RUN mkdir -p /root/.ssh && \
    ssh-keyscan -p 33564 host.docker.internal >> /root/.ssh/known_hosts 2>/dev/null || true

WORKDIR /srvbot

COPY dependencies.txt .
RUN pip install --no-cache-dir -r dependencies.txt

COPY . .

CMD ["python", "srvbot.py"]