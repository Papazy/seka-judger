# 🚀 Simple Deployment Guide - SEKA Judger

Panduan deployment paling sederhana untuk SEKA Judger - **hanya butuh 3 langkah!**

---

## 📋 Prerequisites

- Docker installed
- Port 8001 available
- Internet connection (untuk pull images)

---

## 🎯 Quick Start (3 Steps)

### 1️⃣ Build Docker Image

```bash
docker build -t seka-judger .
```

### 2️⃣ Run Container

```bash
docker run -d \
  --name seka-judger \
  -p 8001:8001 \
  -v /var/run/docker.sock:/var/run/docker.sock \
  seka-judger
```

### 3️⃣ Test API

Buka browser: http://localhost:8001/docs

**DONE! ✅** Aplikasi sudah jalan.

---

## 📝 Penjelasan Singkat

### Port Mapping
```bash
-p 8001:8001
```
- Map port 8001 container → port 8001 host
- Akses via: `http://localhost:8001`

### Docker Socket
```bash
-v /var/run/docker.sock:/var/run/docker.sock
```
- Memberikan akses ke Docker di host
- **Diperlukan** agar judger bisa menjalankan code di container terpisah
- ⚠️ **Development Only** - tidak untuk production server yang public

### Detached Mode
```bash
-d
```
- Container berjalan di background
- Tidak akan stop saat terminal ditutup

---

## 🛠️ Perintah Berguna

### Lihat Logs
```bash
docker logs seka-judger
```

### Follow Logs (real-time)
```bash
docker logs -f seka-judger
```

### Stop Container
```bash
docker stop seka-judger
```

### Start Container
```bash
docker start seka-judger
```

### Restart Container
```bash
docker restart seka-judger
```

### Hapus Container
```bash
docker stop seka-judger
docker rm seka-judger
```

### Rebuild & Run (jika ada perubahan code)
```bash
# Stop & hapus container lama
docker stop seka-judger
docker rm seka-judger

# Build ulang
docker build -t seka-judger .

# Run lagi
docker run -d \
  --name seka-judger \
  -p 8001:8001 \
  -v /var/run/docker.sock:/var/run/docker.sock \
  seka-judger
```

---

## 🔍 Troubleshooting

### ❌ Port sudah digunakan
```
Error: Bind for 0.0.0.0:8001 failed: port is already allocated
```

**Solusi 1:** Gunakan port lain
```bash
docker run -d --name seka-judger -p 8002:8001 \
  -v /var/run/docker.sock:/var/run/docker.sock seka-judger
```

**Solusi 2:** Stop container yang pakai port 8001
```bash
docker ps  # cari container yang pakai port 8001
docker stop <container-id>
```

---

### ❌ Container name sudah ada
```
Error: The container name "/seka-judger" is already in use
```

**Solusi:**
```bash
docker rm seka-judger
# atau
docker rm -f seka-judger  # force remove (stop + remove)
```

---

### ❌ Docker command tidak ditemukan di dalam container
```
ERROR: [Errno 2] No such file or directory: 'docker'
```

**Penyebab:** Dockerfile tidak install `docker.io`

**Solusi:** Pastikan Dockerfile Anda seperti ini:
```dockerfile
FROM python:3.12-slim
RUN apt-get update && apt-get install -y \
  gcc \
  g++ \
  default-jdk \
  python3 \
  python3-pip \
  docker.io \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8001
CMD ["fastapi", "run", "main.py", "--port", "8001"]
```

Kemudian rebuild:
```bash
docker build -t seka-judger .
```

---

### ❌ Permission denied untuk Docker socket
```
ERROR: permission denied while trying to connect to Docker daemon
```

**Solusi (macOS/Linux):**
```bash
sudo chmod 666 /var/run/docker.sock
```

**Atau jalankan dengan sudo:**
```bash
sudo docker run -d --name seka-judger -p 8001:8001 \
  -v /var/run/docker.sock:/var/run/docker.sock seka-judger
```

---

### ❌ Container crash/restart terus
```bash
# Lihat error logs
docker logs seka-judger

# Lihat status
docker ps -a | grep seka-judger
```

**Solusi umum:**
1. Pastikan `requirements.txt` lengkap
2. Pastikan `main.py` tidak error
3. Test manual:
```bash
docker run -it --rm seka-judger bash
# di dalam container:
python main.py
```

---

## 🧪 Test Manual

### 1. Cek Container Status
```bash
docker ps
```
Output harus ada container `seka-judger` dengan status `Up`

### 2. Cek Logs
```bash
docker logs seka-judger
```
Harus ada output seperti:
```
INFO   Uvicorn running on http://0.0.0.0:8001
```

### 3. Test API
```bash
curl http://localhost:8001/health
```

### 4. Test dengan Browser
Buka: http://localhost:8001/docs

---

## 📦 Deploy ke Server

### Copy ke Server
```bash
# Zip project
tar -czf seka-judger.tar.gz .

# Copy ke server
scp seka-judger.tar.gz user@your-server:/home/user/

# SSH ke server
ssh user@your-server

# Extract
tar -xzf seka-judger.tar.gz
cd seka-judger

# Build & Run (sama seperti lokal)
docker build -t seka-judger .
docker run -d --name seka-judger -p 8001:8001 \
  -v /var/run/docker.sock:/var/run/docker.sock seka-judger
```

### Auto-restart saat Server Reboot
```bash
docker run -d \
  --name seka-judger \
  --restart unless-stopped \
  -p 8001:8001 \
  -v /var/run/docker.sock:/var/run/docker.sock \
  seka-judger
```

---

## 🔒 Security Notes

### ⚠️ WARNING: Docker Socket Access

Mounting `/var/run/docker.sock` memberikan **full access** ke Docker daemon.

**Safe untuk:**
- ✅ Development lokal di laptop/PC pribadi
- ✅ Testing di VM isolasi
- ✅ Server internal yang tidak public

**TIDAK AMAN untuk:**
- ❌ Production server yang public
- ❌ Shared hosting
- ❌ Server dengan data sensitif

**Untuk production:** Gunakan panduan lengkap di `DEPLOY.md` dengan security yang lebih baik.

---

## 🎓 Summary

**Minimal command untuk deploy:**

```bash
# Build
docker build -t seka-judger .

# Run
docker run -d --name seka-judger -p 8001:8001 \
  -v /var/run/docker.sock:/var/run/docker.sock \
  seka-judger

# Check
docker logs seka-judger

# Access
open http://localhost:8001/docs
```

**That's it!** 🎉

---

## 📞 Need Help?

- Logs: `docker logs seka-judger`
- Status: `docker ps -a`
- Restart: `docker restart seka-judger`
- Full guide: `DEPLOY.md`

---

**Happy Coding! 🚀**
