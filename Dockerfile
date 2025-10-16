FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install -y docker-cli && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN useradd -m dockuser
RUN chown -R dockuser:dockuser /app
USER dockuser



# RUN /app/docker/build_docker.sh

EXPOSE 8001

CMD ["fastapi", "run", "main.py", "--port", "8001" ]