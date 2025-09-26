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

```bash
git clone https://github.com/your-username/videoflix_backend.git
cd videoflix_backend















OLD:


Videoflix Backend












A Django REST Framework backend for Videoflix, a video streaming platform.
This project provides authentication, user profiles, and protected video streaming endpoints (HLS .m3u8 manifests and .ts chunks).
It is containerized with Docker, using PostgreSQL as the database and Redis as a cache/message broker.

🚀 Features

Authentication: User signup & login (token/JWT support)

Profiles: Basic profile management for registered users

Video Streaming: HLS playlist (.m3u8) + video chunk (.ts) endpoints

Access Control: Configurable (public or authenticated)

Dockerized: Run with one command (docker-compose up)

Redis: Ready for caching / async tasks (e.g. Celery integration)

🛠️ Tech Stack

Backend: Django 5 + Django REST Framework

Database: PostgreSQL

Cache / Broker: Redis

Media Handling: HLS (.m3u8, .ts)

Containerization: Docker & Docker Compose

Testing: Pytest + DRF test utilities

📦 Installation & Setup
Prerequisites

Docker

Docker Compose

Clone the repo
git clone https://github.com/your-username/videoflix_backend.git
cd videoflix_backend

Environment variables

Create a .env file in the project root:

DJANGO_SECRET_KEY=your-secret-key
DEBUG=True
POSTGRES_DB=videoflix
POSTGRES_USER=videoflix_user
POSTGRES_PASSWORD=videoflix_password
POSTGRES_HOST=db
POSTGRES_PORT=5432
REDIS_HOST=redis
REDIS_PORT=6379

Run with Docker
docker-compose up --build


This will start:

Backend → http://localhost:8000

PostgreSQL → on internal Docker network

Redis → on internal Docker network

📡 API Endpoints (examples)

Authentication:

POST /api/registration/   # Register
POST /api/login/          # Login


Profile:

GET /api/profile/{id}/


Videos:

GET /api/video/{id}/{quality}/index.m3u8   # HLS playlist
GET /api/video/{id}/{quality}/{chunk}.ts   # Video chunks

🎥 Frontend Integration

The backend serves HLS streams that can be played in the browser with a plain HTML/JS player.
Example using hls.js
:

<video id="video" controls></video>
<script src="https://cdn.jsdelivr.net/npm/hls.js@latest"></script>
<script>
  const video = document.getElementById('video');
  const hls = new Hls();
  hls.loadSource('http://localhost:8000/api/video/1/720p/index.m3u8');
  hls.attachMedia(video);
</script>

✅ Development Checklist

 API endpoints reachable

 Authentication working (token/JWT)

 HLS manifests served with correct headers (application/vnd.apple.mpegurl)

 TS chunks served with correct headers (video/mp2t)

 Range requests supported (206 Partial Content)

 Dockerized setup with PostgreSQL + Redis

🧪 Running Tests

Run tests inside the backend container:

docker-compose run backend pytest

📖 Notes

For production, configure:

Nginx for efficient static/video serving (X-Accel-Redirect recommended)

Proper CORS settings (django-cors-headers)

Signed URLs or pre-signed tokens for secure video access

📜 License

MIT License – feel free to use and adapt.

👉 D
