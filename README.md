# 🎬 Videoflix Backend

![Python](https://img.shields.io/badge/Python-3.13-blue?logo=python&logoColor=white)  
![Django](https://img.shields.io/badge/Django-5.0-green?logo=django&logoColor=white)  
![DRF](https://img.shields.io/badge/DRF-REST%20Framework-red?logo=django&logoColor=white)  
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue?logo=postgresql&logoColor=white)  
![Redis](https://img.shields.io/badge/Redis-7-red?logo=redis&logoColor=white)  
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)  

---

A **Django REST Framework** backend for *Videoflix*, a video streaming platform.  
This project provides authentication, user profiles, and protected video streaming endpoints (HLS `.m3u8` manifests and `.ts` chunks).  
It is containerized with **Docker**, using **PostgreSQL** as the database and **Redis** as a cache/message broker.

---

## 🚀 Features

- 🔑 **Authentication** → Signup & login (token/JWT support)  
- 👤 **Profiles** → Basic profile management for registered users  
- 🎥 **Video Streaming** → HLS playlist (`.m3u8`) + video chunk (`.ts`) endpoints  
- 🔒 **Access Control** → Configurable (public or authenticated)  
- 🐳 **Dockerized** → Run with one command (`docker-compose up`)  
- ⚡ **Redis** → Ready for caching / async tasks (e.g. Celery integration)  

---

## 🛠️ Tech Stack

- **Backend**: Django 5 + Django REST Framework  
- **Database**: PostgreSQL  
- **Cache / Broker**: Redis  
- **Media Handling**: HLS (`.m3u8`, `.ts`)  
- **Containerization**: Docker & Docker Compose  
- **Testing**: Pytest + DRF test utilities  

---

## 📦 Installation & Setup

### 🔹 Prerequisites

- [Docker](https://docs.docker.com/get-docker/)  
- [Docker Compose](https://docs.docker.com/compose/)  

### 🔹 Clone the Repo

git clone https://github.com/your-username/videoflix_backend.git
cd videoflix_backend

---

## 🔹 Environment Variables  
Create a `.env` file in the project root with the following values:  

DJANGO_SECRET_KEY=your-secret-key  
DEBUG=True  

POSTGRES_DB=videoflix  
POSTGRES_USER=videoflix_user  
POSTGRES_PASSWORD=videoflix_password  
POSTGRES_HOST=db  
POSTGRES_PORT=5432  

REDIS_HOST=redis  
REDIS_PORT=6379  

---

## 🔹 Run with Docker  

Start the project with:  

docker-compose up --build


This starts:

📡 **Backend** → [http://localhost:8000](http://localhost:8000)  
🗄️ **PostgreSQL** → internal Docker network  
⚡ **Redis** → internal Docker network  

---

## 📡 API Endpoints (Examples)

### 🔑 Authentication  
- `POST /api/registration/` → Register  
- `POST /api/login/` → Login  

### 👤 Profile  
- `GET /api/profile/{id}/`  

### 🎥 Videos  
- `GET /api/video/{id}/{quality}/index.m3u8` → HLS playlist  
- `GET /api/video/{id}/{quality}/{chunk}.ts` → Video chunks  

---

## 🎥 Frontend Integration

HLS streams can be played in-browser using [hls.js](https://github.com/video-dev/hls.js):  

<video id="video" controls></video>
<script src="https://cdn.jsdelivr.net/npm/hls.js@latest"></script>
<script>
  const video = document.getElementById('video');
  const hls = new Hls();
  hls.loadSource('http://localhost:8000/api/video/1/720p/index.m3u8');
  hls.attachMedia(video);
</script>


## 🧪 Running Tests  

Run tests inside the backend container:  

docker-compose run backend pytest


## 📖 Notes for Production  

- 🌐 **Nginx** → Serve static/videos efficiently (`X-Accel-Redirect` recommended)  
- ⚙️ **CORS** → Use [django-cors-headers](https://github.com/adamchainz/django-cors-headers)  
- 🔑 **Video Security** → Signed URLs or pre-signed tokens  

---

## 📜 License  

**MIT License** – free to use and adapt.  
See the [LICENSE](./LICENSE) file for full text.  

---
