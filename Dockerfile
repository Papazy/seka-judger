FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
  gcc \
  g++ \
  openjdk-17-jdk \
  python3 \
  python3-pip \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["fastapi", "run", "main.py", "--port", "8001" ]

