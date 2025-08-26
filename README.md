
# ![Bakraload Logo](https://img.icons8.com/color-pixels/38/goat.png) Bakraload: Universal Social Media Downloader



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
- **Rate Limiting & Security**: Built-in protection against abuse.

---

## 🗂️ Project Structure

```text
bakraload/
│
├── app.py                
├── requirements.txt      # Python dependencies
├── README.md             # Project documentation
│
├── downloads/            # All downloaded files/folders (auto-created)
│
├── static/
│   ├── css/
│   │   └── styles.css     
│   └── js/
│       └── script.js     
│
└── templates/
    └── index.html        
```

---

## ⚡ Quick Start

1. **Clone the repo:**
   ```bash
   git clone <your-repo-url>
   cd bakraload
   ```
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Run the app:**
   ```bash
   python app.py
   ```
4. **Open in browser:**
   Visit [http://localhost:5000](http://localhost:5000)

---

## 🛡️ Security & Best Practices
- CORS, HTTPS (Talisman), and rate limiting enabled by default.
- No metadata/comments are saved for Instagram reels/posts by default, but you can enable it.
- For production, restrict CORS and enable HTTPS enforcement.

---

## 📦 Supported Platforms
- YouTube (videos, shorts, playlists)
- Instagram (posts, reels, stories, IGTV)
- TikTok
- Twitter/X
- Facebook
- Reddit
- ...and more!

---

## ✨ Credits
- [yt-dlp](https://github.com/yt-dlp/yt-dlp)
- [Instaloader](https://instaloader.github.io/)
- [Flask](https://flask.palletsprojects.com/)

---

## 📝 License
MIT License. For educational and personal use only. Respect the terms of service of each platform.
