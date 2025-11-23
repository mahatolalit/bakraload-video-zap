from flask import Flask, request, render_template, jsonify, send_file, abort
import os
import tempfile
import threading
import requests
import json
import re
from datetime import datetime
import yt_dlp
import instaloader
from werkzeug.utils import secure_filename
import zipfile
import shutil
import secrets
# Security imports
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_cors import CORS
from flask_talisman import Talisman


app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', secrets.token_hex(32))
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max request size

# Security: CORS, Talisman, Limiter
allowed_origins = os.getenv('ALLOWED_ORIGINS', '*').split(',')
CORS(app, resources={r"/*": {"origins": allowed_origins}})

# Enable HTTPS enforcement in production
force_https = os.getenv('FORCE_HTTPS', 'False').lower() == 'true'
if force_https:
    Talisman(app, content_security_policy={
        'default-src': "'self'",
        'script-src': ["'self'", "'unsafe-inline'"],
        'style-src': ["'self'", "'unsafe-inline'"],
    })
else:
    Talisman(app, content_security_policy=None, force_https=False)

# Rate limiting
rate_limit_per_minute = os.getenv('RATE_LIMIT_PER_MINUTE', '30')
rate_limit_per_hour = os.getenv('RATE_LIMIT_PER_HOUR', '200')
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=[f"{rate_limit_per_minute}/minute", f"{rate_limit_per_hour}/hour"],
    storage_uri=os.getenv('REDIS_URL', 'memory://')
)

class UniversalDownloader:
    # Allowed URL schemes and regex for validation
    URL_REGEX = re.compile(r'^(https?://)[\w\-\.]+(\.[a-z]{2,})(:[0-9]+)?(/[\w\-\./?%&=]*)?$', re.IGNORECASE)
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    def is_valid_url(self, url):
        # Only allow http/https and basic domain validation
        if not url or not isinstance(url, str):
            return False
        if not url.lower().startswith(('http://', 'https://')):
            return False
        if not self.URL_REGEX.match(url):
            return False
        return True

    def detect_platform(self, url):
        """Detect the platform from URL"""
        url = url.lower()
        if 'youtube.com' in url or 'youtu.be' in url:
            return 'youtube'
        elif 'instagram.com' in url:
            return 'instagram'
        elif 'facebook.com' in url or 'fb.watch' in url:
            return 'facebook'
        elif 'twitter.com' in url or 'x.com' in url:
            return 'twitter'
        elif 'tiktok.com' in url:
            return 'tiktok'
        elif 'pinterest.com' in url:
            return 'pinterest'
        elif 'linkedin.com' in url:
            return 'linkedin'
        elif 'snapchat.com' in url:
            return 'snapchat'
        elif 'reddit.com' in url:
            return 'reddit'
        elif 'twitch.tv' in url:
            return 'twitch'
        else:
            return 'unknown'
        
    def create_safe_filename(self, filename, max_length=100):
        """Create a safe filename"""
        # Remove invalid characters
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        filename = filename.strip()
        if len(filename) > max_length:
            filename = filename[:max_length]
        return filename
    
    def download_youtube_content(self, url, path, format_type='default'):
        """Download YouTube videos, shorts, playlists"""
        try:
            # Check if ffmpeg is available
            if not shutil.which('ffmpeg'):
                return {'status': 'error', 'message': 'ffmpeg is not installed or not in PATH. 1080p downloads require ffmpeg.'}
            
            # Set format based on user selection
            if format_type == 'mp3':
                ydl_opts = {
                    'outtmpl': os.path.join(path, '%(uploader)s - %(title)s.%(ext)s'),
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                    'ignoreerrors': True,
                }
            elif format_type == 'mp4':
                ydl_opts = {
                    'outtmpl': os.path.join(path, '%(uploader)s - %(title)s.%(ext)s'),
                    'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                    'merge_output_format': 'mp4',
                    'ignoreerrors': True,
                }
            else:  # default
                ydl_opts = {
                    'outtmpl': os.path.join(path, '%(uploader)s - %(title)s.%(ext)s'),
                    'format': 'bestvideo[height<=1080]+bestaudio/best[height<=1080]',
                    'writesubtitles': True,
                    'writeautomaticsub': True,
                    'subtitleslangs': ['en'],
                    'ignoreerrors': True,
                    'merge_output_format': 'mp4',
                }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                if 'entries' in info:  # Playlist
                    titles = [entry.get('title', 'Unknown') for entry in info['entries'] if entry]
                    playlist_title = info.get('title', 'YouTube_Playlist')
                    return {
                        'status': 'success',
                        'message': f'Downloaded {len(titles)} videos from playlist',
                        'titles': titles[:5],  # Show first 5 titles
                        'type': 'playlist',
                        'playlist_title': playlist_title
                    }
                else:  # Single video
                    return {
                        'status': 'success',
                        'message': 'YouTube content downloaded successfully!',
                        'title': info.get('title', 'Unknown'),
                        'uploader': info.get('uploader', 'Unknown'),
                        'type': 'video'
                    }
        except Exception as e:
            return {'status': 'error', 'message': f'YouTube error: {str(e)}'}
    
    def download_instagram_content(self, url, path):
        """Download Instagram posts, reels, stories, IGTV"""
        try:
            loader = instaloader.Instaloader(
                dirname_pattern=path,
                filename_pattern='{profile}_{mediaid}_{date_utc}',
                download_videos=True,
                download_video_thumbnails=False,
                download_geotags=False,
                download_comments=False,  # Do not download comments
                save_metadata=False,      # Do not save metadata JSON
                compress_json=False       # Do not compress JSON (no JSON will be saved)
            )
            
            # Handle different Instagram URL types
            if '/stories/' in url:
                # Story URL
                username = self.extract_instagram_username(url)
                if username:
                    profile = instaloader.Profile.from_username(loader.context, username)
                    for story in loader.get_stories([profile.userid]):
                        for item in story.get_items():
                            loader.download_storyitem(item, target=username)
                    return {
                        'status': 'success',
                        'message': f'Instagram stories downloaded for {username}',
                        'type': 'stories'
                    }
            elif '/reel/' in url or '/p/' in url or '/tv/' in url:
                # Post, Reel, or IGTV
                shortcode = self.extract_instagram_shortcode(url)
                post = instaloader.Post.from_shortcode(loader.context, shortcode)
                
                loader.download_post(post, target=post.owner_username)
                
                content_type = 'reel' if post.is_video else 'post'
                if post.typename == 'GraphSidecar':
                    content_type = 'carousel'
                return {
                    'status': 'success',
                    'message': f'Instagram {content_type} downloaded successfully!',
                    'username': post.owner_username,
                    'type': content_type
                }
            else:
                # Profile URL - download recent posts
                username = self.extract_instagram_username(url)
                profile = instaloader.Profile.from_username(loader.context, username)
                
                count = 0
                for post in profile.get_posts():
                    if count >= 10:  # Limit to 10 recent posts
                        break
                    loader.download_post(post, target=username)
                    count += 1
                
                return {
                    'status': 'success',
                    'message': f'Downloaded {count} recent posts from {username}',
                    'type': 'profile'
                }
                
        except Exception as e:
            return {'status': 'error', 'message': f'Instagram error: {str(e)}'}
    
    def download_tiktok_content(self, url, path, format_type='default'):
        """Download TikTok videos"""
        try:
            if format_type == 'mp3':
                ydl_opts = {
                    'outtmpl': os.path.join(path, 'TikTok_%(uploader)s_%(title)s.%(ext)s'),
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                }
            else:
                ydl_opts = {
                    'outtmpl': os.path.join(path, 'TikTok_%(uploader)s_%(title)s.%(ext)s'),
                    'format': 'best',
                }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                return {
                    'status': 'success',
                    'message': 'TikTok video downloaded successfully!',
                    'title': info.get('title', 'TikTok Video'),
                    'uploader': info.get('uploader', 'Unknown'),
                    'type': 'video'
                }
        except Exception as e:
            return {'status': 'error', 'message': f'TikTok error: {str(e)}'}
    
    def download_twitter_content(self, url, path, format_type='default'):
        """Download Twitter/X videos, images, threads"""
        try:
            if format_type == 'mp3':
                ydl_opts = {
                    'outtmpl': os.path.join(path, 'Twitter_%(uploader)s_%(title)s.%(ext)s'),
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                }
            else:
                ydl_opts = {
                    'outtmpl': os.path.join(path, 'Twitter_%(uploader)s_%(title)s.%(ext)s'),
                    'writesubtitles': True,
                }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                return {
                    'status': 'success',
                    'message': 'Twitter content downloaded successfully!',
                    'title': info.get('title', 'Twitter Content'),
                    'uploader': info.get('uploader', 'Unknown'),
                    'type': 'tweet'
                }
        except Exception as e:
            return {'status': 'error', 'message': f'Twitter error: {str(e)}'}
    
    def download_facebook_content(self, url, path, format_type='default'):
        """Download Facebook videos, posts"""
        try:
            if format_type == 'mp3':
                ydl_opts = {
                    'outtmpl': os.path.join(path, 'Facebook_%(title)s.%(ext)s'),
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                }
            else:
                ydl_opts = {
                    'outtmpl': os.path.join(path, 'Facebook_%(title)s.%(ext)s'),
                    'format': 'best',
                }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                return {
                    'status': 'success',
                    'message': 'Facebook content downloaded successfully!',
                    'title': info.get('title', 'Facebook Content'),
                    'type': 'video'
                }
        except Exception as e:
            return {'status': 'error', 'message': f'Facebook error: {str(e)}'}
    
    def download_reddit_content(self, url, path, format_type='default'):
        """Download Reddit videos, images, gifs"""
        try:
            if format_type == 'mp3':
                ydl_opts = {
                    'outtmpl': os.path.join(path, 'Reddit_%(title)s.%(ext)s'),
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                }
            else:
                ydl_opts = {
                    'outtmpl': os.path.join(path, 'Reddit_%(title)s.%(ext)s'),
                }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                return {
                    'status': 'success',
                    'message': 'Reddit content downloaded successfully!',
                    'title': info.get('title', 'Reddit Post'),
                    'type': 'post'
                }
        except Exception as e:
            return {'status': 'error', 'message': f'Reddit error: {str(e)}'}
    
    def download_generic_content(self, url, path, format_type='default'):
        """Download from any supported platform using yt-dlp"""
        try:
            if format_type == 'mp3':
                ydl_opts = {
                    'outtmpl': os.path.join(path, '%(extractor)s_%(title)s.%(ext)s'),
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                }
            else:
                ydl_opts = {
                    'outtmpl': os.path.join(path, '%(extractor)s_%(title)s.%(ext)s'),
                    'format': 'best',
                }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                return {
                    'status': 'success',
                    'message': 'Content downloaded successfully!',
                    'title': info.get('title', 'Unknown'),
                    'extractor': info.get('extractor', 'Unknown'),
                    'type': 'media'
                }
        except Exception as e:
            return {'status': 'error', 'message': f'Download error: {str(e)}'}
    
    def extract_instagram_shortcode(self, url):
        """Extract shortcode from Instagram URL"""
        patterns = [
            r'/p/([^/?]+)',
            r'/reel/([^/?]+)',
            r'/tv/([^/?]+)'
        ]
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
    
    def extract_instagram_username(self, url):
        """Extract username from Instagram URL"""
        match = re.search(r'instagram\.com/([^/?]+)', url)
        if match:
            return match.group(1)
        return None
    
    def download_content(self, url, format_type='default'):
        """Main download function. Returns (download_dir, file_list, error_msg, info_dict)"""
        platform = self.detect_platform(url)
        if not self.is_valid_url(url):
            return None, None, 'Invalid or unsupported URL.', None
        temp_dir = tempfile.mkdtemp(prefix=f"bakraload_{platform}_")
        try:
            if platform == 'youtube':
                result = self.download_youtube_content(url, temp_dir, format_type)
            elif platform == 'instagram':
                result = self.download_instagram_content(url, temp_dir)
            elif platform == 'tiktok':
                result = self.download_tiktok_content(url, temp_dir, format_type)
            elif platform == 'twitter':
                result = self.download_twitter_content(url, temp_dir, format_type)
            elif platform == 'facebook':
                result = self.download_facebook_content(url, temp_dir, format_type)
            elif platform == 'reddit':
                result = self.download_reddit_content(url, temp_dir, format_type)
            else:
                result = self.download_generic_content(url, temp_dir, format_type)
            # If result is error dict, return error
            if isinstance(result, dict) and result.get('status') == 'error':
                shutil.rmtree(temp_dir, ignore_errors=True)
                return None, None, result.get('message', 'Download error.'), None
            # List downloaded files
            file_list = []
            for root, dirs, files in os.walk(temp_dir):
                for f in files:
                    file_list.append(os.path.join(root, f))
            if not file_list:
                shutil.rmtree(temp_dir, ignore_errors=True)
                return None, None, 'No downloadable content found.', None
            return temp_dir, file_list, None, result
        except Exception as e:
            shutil.rmtree(temp_dir, ignore_errors=True)
            return None, None, 'An error occurred while processing your request.', None

# Initialize downloader
downloader = UniversalDownloader()

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

from flask import after_this_request

@app.route('/download', methods=['POST'])
@limiter.limit("10/minute")
def download():
    """Handle download requests and return file/zip directly"""
    try:
        data = request.get_json()
        url = data.get('url', '').strip()
        format_type = data.get('format', 'default')
        if not url:
            return jsonify({'status': 'error', 'message': 'No URL provided.'}), 400
        temp_dir, file_list, error, info = downloader.download_content(url, format_type)
        if error:
            return jsonify({'status': 'error', 'message': error}), 400
        # If only one file, serve it directly
        if len(file_list) == 1:
            file_path = file_list[0]
            filename = os.path.basename(file_path)
            @after_this_request
            def cleanup(response):
                shutil.rmtree(temp_dir, ignore_errors=True)
                return response
            return send_file(file_path, as_attachment=True, download_name=filename, mimetype='application/octet-stream')
        # If multiple files, zip them
        else:
            # Use playlist title if available, otherwise default name
            zip_filename = 'download.zip'
            if info and isinstance(info, dict):
                if info.get('type') == 'playlist':
                    playlist_title = info.get('playlist_title', 'Playlist')
                    # Sanitize playlist title for filename
                    safe_title = re.sub(r'[<>:"/\\|?*]', '_', playlist_title)
                    safe_title = safe_title.strip()[:100]  # Limit length
                    if safe_title:
                        zip_filename = f"{safe_title}.zip"
            
            zip_path = os.path.join(temp_dir, zip_filename)
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for f in file_list:
                    arcname = os.path.relpath(f, temp_dir)
                    zipf.write(f, arcname)
            @after_this_request
            def cleanup(response):
                shutil.rmtree(temp_dir, ignore_errors=True)
                return response
            return send_file(zip_path, as_attachment=True, download_name=zip_filename, mimetype='application/zip')
    except Exception as e:
        return jsonify({'status': 'error', 'message': 'Server error.'}), 500

@app.route('/bulk-download', methods=['POST'])
@limiter.limit("3/minute")
def bulk_download():
    """Handle bulk download requests and return a zip"""
    try:
        data = request.get_json()
        urls = data.get('urls', [])
        format_type = data.get('format', 'default')
        if not urls:
            return jsonify({'status': 'error', 'message': 'No URLs provided.'}), 400
        temp_dir = tempfile.mkdtemp(prefix="bakraload_bulk_")
        all_files = []
        errors = []
        for idx, url in enumerate(urls):
            sub_dir = os.path.join(temp_dir, f'item_{idx+1}')
            os.makedirs(sub_dir, exist_ok=True)
            d_temp, file_list, error, info = downloader.download_content(url, format_type)
            if error:
                errors.append(f"URL {idx+1}: {error}")
                continue
            # Move files from d_temp to sub_dir
            for f in file_list:
                dest = os.path.join(sub_dir, os.path.basename(f))
                shutil.move(f, dest)
            shutil.rmtree(d_temp, ignore_errors=True)
            for f in os.listdir(sub_dir):
                all_files.append(os.path.join(sub_dir, f))
        if not all_files:
            shutil.rmtree(temp_dir, ignore_errors=True)
            return jsonify({'status': 'error', 'message': 'No downloadable content found.\\n' + '\\n'.join(errors)}), 400
        
        # Generate random 6-digit hash for bulk downloads
        import random
        random_hash = ''.join(random.choices('0123456789ABCDEF', k=6))
        zip_filename = f'Bulk_vid_{random_hash}.zip'
        zip_path = os.path.join(temp_dir, zip_filename)
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(temp_dir):
                for f in files:
                    if f.endswith('.zip'):
                        continue
                    abs_path = os.path.join(root, f)
                    arcname = os.path.relpath(abs_path, temp_dir)
                    zipf.write(abs_path, arcname)
        @after_this_request
        def cleanup(response):
            shutil.rmtree(temp_dir, ignore_errors=True)
            return response
        return send_file(zip_path, as_attachment=True, download_name=zip_filename, mimetype='application/zip')
    except Exception as e:
        return jsonify({'status': 'error', 'message': 'Bulk download error.'}), 500

@app.route('/supported-platforms')
def supported_platforms():
    """List supported platforms"""
    platforms = {
        'video_platforms': [
            'YouTube (videos, shorts, playlists)',
            'TikTok',
            'Twitter/X',
            'Facebook',
            'Instagram (Reels, IGTV)',
            'Reddit',
            'Twitch',
            'Vimeo',
            'Dailymotion'
        ],
        'social_platforms': [
            'Instagram (Posts, Stories, Reels, IGTV)',
            'Twitter/X (Tweets, Threads)',
            'Facebook (Posts, Videos)',
            'Reddit (Posts, Images, Videos)',
            'LinkedIn (Posts)',
            'Pinterest (Pins)'
        ],
        'features': [
            'Auto-platform detection',
            'Bulk downloads',
            'Stories download',
            'Playlist support',
            'High quality downloads',
            'Metadata preservation',
            'Subtitle downloads'
        ]
    }
    return jsonify(platforms)

if __name__ == '__main__':
    print("=" * 60)
    print("BAKRALOAD")
    print("The Universal Social Media Downloader")
    print("=" * 60)
    print("Starting server...")
    print("Supported platforms: YouTube, Instagram, TikTok, Twitter/X, Facebook, Reddit, and more!")
    print("Features: Stories, Reels, Posts, Videos, Bulk downloads")
    
    port = int(os.getenv('PORT', 5000))
    host = os.getenv('HOST', '0.0.0.0')
    debug = os.getenv('DEBUG', 'False').lower() == 'true'
    
    print(f"Server running on: http://{host}:{port}")
    print("=" * 60)
    
    if debug:
        print("WARNING: Running in DEBUG mode. Do not use in production!")
    
    app.run(host=host, port=port, debug=debug)