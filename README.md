
# ![Bakraload Logo](https://img.icons8.com/color-pixels/38/goat.png) Bakraload: Universal Social Media Video Downloader



A modern and beautiful web app to download videos, reels, stories, and more from all major social media platforms. Built with Flask, and supports bulk downloads and auto-detection.

---

## 🖼️ Preview

<div align="center">
   <img src="https://raw.githubusercontent.com/mahatolalit/assets/refs/heads/main/Screenshot%202025-08-26%20130026.png" alt="Bakraload Home Screenshot" width="80%" style="margin:8px; border-radius:12px; box-shadow:0 2px 16px #0002;" />
   <img src="https://raw.githubusercontent.com/mahatolalit/assets/refs/heads/main/Screenshot%202025-08-26%20130045.png" alt="Bakraload Downloads Screenshot" width="80%" style="margin:8px; border-radius:12px; box-shadow:0 2px 16px #0002;" />
  
   <br>
   <sub>Modern, minimal UI with dark theme and beautiful UX</sub>
</div>

---

## 🚀 Features
- **Auto Platform Detection**: Paste any link, and Bakraload detects the platform.
- **All Content Types**: Download videos, reels, stories, posts, and more.
- **Bulk Downloads**: Download multiple URLs at once.
- **Format Selection**: Choose between MP3 (audio), MP4 (video), or best quality.
- **Smart Naming**: Playlists are named after their title, bulk downloads use unique identifiers.
- **Rate Limiting & Security**: Built-in protection against abuse.
- **Production Ready**: Docker support with Gunicorn, Redis, and health checks.

---

## 🗂️ Project Structure

```text
bakraload/
│
├── app.py                # Main Flask application
├── wsgi.py              # WSGI entry point for production
├── requirements.txt     # Python dependencies
├── README.md            # Project documentation
├── Dockerfile           # Multi-stage Docker build
├── docker-compose.yml   # Docker Compose configuration
├── .dockerignore        # Docker build exclusions
├── .env.example         # Environment variables template
│
├── static/
│   ├── css/
│   │   └── styles.css   # Application styles
│   └── js/
│       └── script.js    # Frontend logic
│
└── templates/
    └── index.html       # Main UI
```

---

## ⚡ Quick Start

### Option 1: Docker (Recommended for Production)

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd bakraload
   ```

2. **Create environment file:**
   ```bash
   cp .env.example .env
   # Edit .env and set your SECRET_KEY
   ```

3. **Start with Docker Compose:**
   ```bash
   docker-compose up -d
   ```

4. **Access the application:**
   Visit [http://localhost:5000](http://localhost:5000)

5. **View logs:**
   ```bash
   docker-compose logs -f bakraload
   ```

6. **Stop the application:**
   ```bash
   docker-compose down
   ```

### Option 2: Docker Build Only

```bash
# Build the image
docker build -t bakraload:latest .

# Run the container
docker run -d -p 5000:5000 \
  -e SECRET_KEY=your-secret-key \
  --name bakraload \
  bakraload:latest
```

### Option 3: Local Development

1. **Clone the repo:**
   ```bash
   git clone <your-repo-url>
   cd bakraload
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install FFmpeg:**
   - **Windows**: Download from [ffmpeg.org](https://ffmpeg.org/download.html)
   - **Linux**: `sudo apt-get install ffmpeg`
   - **macOS**: `brew install ffmpeg`

5. **Set up environment:**
   ```bash
   cp .env.example .env
   # Edit .env file with your settings
   ```

6. **Run the app:**
   ```bash
   python app.py
   ```

7. **Open in browser:**
   Visit [http://localhost:5000](http://localhost:5000)

---

## 🔧 Configuration

Edit `.env` file to configure the application:

```env
# Security
SECRET_KEY=generate-with-openssl-rand-hex-32
FORCE_HTTPS=False
ALLOWED_ORIGINS=*

# Server
HOST=0.0.0.0
PORT=5000
DEBUG=False

# Rate Limiting
RATE_LIMIT_PER_MINUTE=30
RATE_LIMIT_PER_HOUR=200

# Optional: Redis for distributed rate limiting
REDIS_URL=redis://localhost:6379/0
```

---

## 🐳 Docker Configuration

### Environment Variables

The Docker setup supports the following environment variables:

- `SECRET_KEY`: Flask secret key (required)
- `DEBUG`: Enable debug mode (default: False)
- `FORCE_HTTPS`: Enable HTTPS enforcement (default: False)
- `ALLOWED_ORIGINS`: CORS allowed origins (default: *)
- `RATE_LIMIT_PER_MINUTE`: Rate limit per minute (default: 30)
- `RATE_LIMIT_PER_HOUR`: Rate limit per hour (default: 200)

### Production Deployment

For production deployment:

1. **Generate a strong secret key:**
   ```bash
   openssl rand -hex 32
   ```

2. **Update docker-compose.yml or .env:**
   ```yaml
   environment:
     - SECRET_KEY=your-generated-secret-key
     - FORCE_HTTPS=True
     - ALLOWED_ORIGINS=https://yourdomain.com
   ```

3. **Use a reverse proxy (nginx):**
   ```nginx
   server {
       listen 80;
       server_name yourdomain.com;
       
       location / {
           proxy_pass http://localhost:5000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

---

## 🛡️ Security & Best Practices

- CORS, HTTPS (Talisman), and rate limiting enabled by default.
- **CORS**: Configure `ALLOWED_ORIGINS` to restrict access to specific domains
- **HTTPS**: Enable `FORCE_HTTPS=True` in production with SSL/TLS certificates
- **Rate Limiting**: Uses Redis for distributed rate limiting in Docker setup
- **Secret Key**: Always generate a strong secret key for production
- **Non-root User**: Docker container runs as non-root user for security
- **Health Checks**: Built-in health checks for monitoring
- **Input Validation**: URL validation and sanitization on all inputs
- No metadata/comments are saved for Instagram reels/posts by default.

### Production Checklist

- [ ] Generate and set strong `SECRET_KEY`
- [ ] Set `DEBUG=False`
- [ ] Enable `FORCE_HTTPS=True` behind SSL termination
- [ ] Configure `ALLOWED_ORIGINS` to your domain
- [ ] Set up reverse proxy (nginx/Caddy)
- [ ] Configure firewall rules
- [ ] Set up monitoring and logging
- [ ] Regular updates of dependencies

---

## 📦 Supported Platforms

- YouTube (videos, shorts, playlists) with MP3/MP4 format selection
- Instagram (posts, reels, stories, IGTV)
- TikTok with audio extraction
- Twitter/X (videos, images)
- Facebook (posts, videos)
- Reddit (videos, images, gifs)
- And many more via yt-dlp!

---

## 🚀 Performance & Scalability

- **Multi-stage Docker builds**: Optimized image size
- **Gunicorn**: Production-grade WSGI server with 4 workers
- **Redis**: Distributed rate limiting and caching
- **Automatic cleanup**: Temporary files are cleaned after download
- **Health checks**: Container health monitoring
- **Horizontal scaling**: Can be deployed behind a load balancer

---

## 🐛 Troubleshooting

### FFmpeg Not Found
If you encounter "ffmpeg not installed" errors:
- Docker: FFmpeg is included in the image
- Local: Install FFmpeg manually for your OS

### Download Fails with 403 Error
This is usually due to platform restrictions. Try:
- Updating yt-dlp: `pip install -U yt-dlp`
- Using cookies (see yt-dlp documentation)

### Rate Limit Errors
Adjust rate limits in `.env`:
```env
RATE_LIMIT_PER_MINUTE=50
RATE_LIMIT_PER_HOUR=500
```

---

## ✨ Credits
- [yt-dlp](https://github.com/yt-dlp/yt-dlp)
- [Instaloader](https://instaloader.github.io/)
- [Flask](https://flask.palletsprojects.com/)

---

## 📝 License
MIT License. For educational and personal use only. Respect the terms of service of each platform.
