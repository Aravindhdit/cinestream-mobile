#!/usr/bin/env python3
"""
CineStream Android App
Mobile-optimized movie streaming application for Android devices
"""

import os
import sys
import threading
import time
import json
import mimetypes
import re
from urllib.parse import quote, unquote
from pathlib import Path

# Kivy imports for Android app
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.uix.progressbar import ProgressBar
from kivy.uix.image import Image
from kivy.uix.video import Video
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.utils import platform
from kivy.logger import Logger

# Flask imports for embedded server
from flask import Flask, render_template_string, request, Response, send_file, jsonify

# Android-specific imports
if platform == 'android':
    from android.permissions import request_permissions, Permission
    from android.storage import primary_external_storage_path, secondary_external_storage_path
    from jnius import autoclass
    PythonActivity = autoclass('org.kivy.android.PythonActivity')

class MovieStreamer:
    """Core movie streaming functionality"""
    
    def __init__(self):
        self.movies_folder = self.get_movies_folder()
        self.watch_progress = {}
        self.progress_file = os.path.join(self.get_app_folder(), 'watch_progress.json')
        self.load_progress()
        
        # Initialize Flask app
        self.app = Flask(__name__)
        self.app.secret_key = 'cinestream_mobile_secret_key_2025'
        self.setup_routes()
        
    def get_app_folder(self):
        """Get app-specific folder for data storage"""
        if platform == 'android':
            # Use internal storage for app data
            return '/data/data/org.cinestream.app/files'
        else:
            return os.path.expanduser('~/.cinestream')
            
    def get_movies_folder(self):
        """Get movies folder based on platform"""
        if platform == 'android':
            # Use external storage for movies
            primary_path = primary_external_storage_path()
            movies_paths = [
                os.path.join(primary_path, 'Movies'),
                os.path.join(primary_path, 'DCIM', 'Movies'),
                os.path.join(primary_path, 'Download', 'Movies'),
                '/storage/emulated/0/Movies',
                '/storage/emulated/0/Download/Movies',
                '/sdcard/Movies',
                '/sdcard/Download/Movies'
            ]
            
            # Try to find an existing movies folder
            for path in movies_paths:
                if os.path.exists(path):
                    return path
                    
            # Create Movies folder in primary storage
            movies_folder = os.path.join(primary_path, 'Movies')
            os.makedirs(movies_folder, exist_ok=True)
            return movies_folder
        else:
            # For desktop testing
            return os.path.join(os.getcwd(), 'movies')
    
    def load_progress(self):
        """Load watch progress from file"""
        try:
            if os.path.exists(self.progress_file):
                with open(self.progress_file, 'r') as f:
                    self.watch_progress = json.load(f)
        except Exception as e:
            Logger.error(f'Error loading progress: {e}')
            self.watch_progress = {}
    
    def save_progress(self):
        """Save watch progress to file"""
        try:
            os.makedirs(os.path.dirname(self.progress_file), exist_ok=True)
            with open(self.progress_file, 'w') as f:
                json.dump(self.watch_progress, f, indent=2)
        except Exception as e:
            Logger.error(f'Error saving progress: {e}')
    
    def get_movies(self):
        """Get list of movies from the movies folder"""
        movies = []
        
        if not os.path.exists(self.movies_folder):
            return movies
            
        video_extensions = {
            '.mp4', '.avi', '.mkv', '.mov', '.wmv', 
            '.flv', '.webm', '.m4v', '.3gp', '.mpg', '.mpeg'
        }
        
        try:
            for filename in os.listdir(self.movies_folder):
                filepath = os.path.join(self.movies_folder, filename)
                
                if os.path.isfile(filepath):
                    name, ext = os.path.splitext(filename)
                    
                    if ext.lower() in video_extensions:
                        # Get file size
                        size_bytes = os.path.getsize(filepath)
                        size_gb = round(size_bytes / (1024**3), 2)
                        
                        # Get watch progress
                        progress = self.watch_progress.get(filename, {})
                        watch_percentage = progress.get('percentage', 0)
                        
                        movies.append({
                            'name': name,
                            'filename': filename,
                            'size': size_gb,
                            'watch_percentage': watch_percentage,
                            'is_watched': watch_percentage > 90,
                            'is_watching': 5 < watch_percentage < 90,
                            'download_url': f'/download/{quote(filename)}'
                        })
                        
        except Exception as e:
            Logger.error(f'Error scanning movies: {e}')
            
        return sorted(movies, key=lambda x: x['name'])
    
    def setup_routes(self):
        """Setup Flask routes for the embedded server"""
        
        @self.app.route('/')
        def index():
            movies = self.get_movies()
            return self.render_mobile_homepage(movies)
        
        @self.app.route('/player/<filename>')
        def player(filename):
            return self.render_mobile_player(filename)
        
        @self.app.route('/stream/<filename>')
        def stream_video(filename):
            return self.stream_video_file(filename)
        
        @self.app.route('/download/<filename>')
        def download_movie(filename):
            return self.download_movie_file(filename)
        
        @self.app.route('/save-progress', methods=['POST'])
        def save_progress_endpoint():
            return self.save_progress_endpoint()
    
    def render_mobile_homepage(self, movies):
        """Render mobile-optimized homepage"""
        html_template = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
            <title>CineStream Mobile</title>
            <style>
                * {
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                    -webkit-tap-highlight-color: transparent;
                }
                
                body {
                    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
                    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
                    color: white;
                    min-height: 100vh;
                    overflow-x: hidden;
                }
                
                .header {
                    background: linear-gradient(135deg, rgba(255, 107, 107, 0.1), rgba(78, 205, 196, 0.1));
                    padding: 30px 20px;
                    text-align: center;
                    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
                    backdrop-filter: blur(10px);
                }
                
                .logo {
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    gap: 15px;
                    margin-bottom: 15px;
                }
                
                .logo-icon {
                    font-size: 2.5rem;
                    animation: rotate 10s linear infinite;
                }
                
                .logo h1 {
                    font-size: 2.5rem;
                    font-weight: 800;
                    background: linear-gradient(135deg, #ff6b6b, #4ecdc4, #45b7d1);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                    background-clip: text;
                }
                
                .subtitle {
                    font-size: 1.1rem;
                    color: rgba(255, 255, 255, 0.8);
                    font-weight: 300;
                    margin-bottom: 20px;
                }
                
                .dolby-badges {
                    display: flex;
                    gap: 15px;
                    justify-content: center;
                    flex-wrap: wrap;
                }
                
                .dolby-badge {
                    background: rgba(255, 255, 255, 0.1);
                    border: 1px solid rgba(255, 255, 255, 0.2);
                    border-radius: 25px;
                    padding: 8px 16px;
                    font-size: 0.85rem;
                    font-weight: 600;
                    backdrop-filter: blur(10px);
                    display: flex;
                    align-items: center;
                    gap: 8px;
                }
                
                .dolby-badge.vision {
                    border-color: rgba(255, 107, 107, 0.4);
                    background: rgba(255, 107, 107, 0.1);
                    color: #ff6b6b;
                }
                
                .dolby-badge.atmos {
                    border-color: rgba(102, 126, 234, 0.4);
                    background: rgba(102, 126, 234, 0.1);
                    color: #667eea;
                }
                
                .movies-section {
                    padding: 30px 20px;
                }
                
                .section-title {
                    font-size: 1.8rem;
                    font-weight: 700;
                    margin-bottom: 25px;
                    text-align: center;
                    color: white;
                }
                
                .movies-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
                    gap: 20px;
                    max-width: 1200px;
                    margin: 0 auto;
                }
                
                .movie-card {
                    background: rgba(255, 255, 255, 0.05);
                    border-radius: 20px;
                    overflow: hidden;
                    transition: all 0.4s ease;
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    backdrop-filter: blur(10px);
                }
                
                .movie-card:active {
                    transform: scale(0.95);
                }
                
                .movie-poster {
                    height: 180px;
                    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 30%, #0f3460 70%, #1e3c72 100%);
                    position: relative;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    overflow: hidden;
                    border-bottom: 3px solid transparent;
                    border-image: linear-gradient(90deg, #ff6b6b, #4ecdc4, #45b7d1) 1;
                }
                
                .movie-poster::before {
                    content: '🎬';
                    font-size: 4rem;
                    opacity: 0.4;
                    position: absolute;
                    z-index: 2;
                    animation: cinematicFloat 4s ease-in-out infinite;
                    filter: drop-shadow(0 0 15px rgba(255, 107, 107, 0.5));
                }
                
                .movie-overlay {
                    position: absolute;
                    top: 0;
                    left: 0;
                    right: 0;
                    bottom: 0;
                    background: linear-gradient(to bottom, rgba(0,0,0,0.2) 0%, transparent 30%, transparent 70%, rgba(0,0,0,0.8) 100%);
                    display: flex;
                    flex-direction: column;
                    justify-content: space-between;
                    padding: 15px;
                    z-index: 3;
                }
                
                .dolby-indicators {
                    display: flex;
                    gap: 8px;
                    align-self: flex-start;
                }
                
                .dolby-mini {
                    padding: 4px 8px;
                    border-radius: 6px;
                    font-size: 0.7rem;
                    font-weight: 700;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.3);
                    backdrop-filter: blur(10px);
                }
                
                .dolby-mini.vision {
                    background: linear-gradient(135deg, rgba(255, 107, 107, 0.9), rgba(238, 90, 36, 0.9));
                    color: white;
                    border: 1px solid rgba(255, 107, 107, 0.5);
                }
                
                .dolby-mini.atmos {
                    background: linear-gradient(135deg, rgba(102, 126, 234, 0.9), rgba(118, 75, 162, 0.9));
                    color: white;
                    border: 1px solid rgba(102, 126, 234, 0.5);
                }
                
                .quality-badge {
                    align-self: flex-end;
                    background: linear-gradient(135deg, rgba(0,0,0,0.8), rgba(20,20,20,0.9));
                    color: #4ecdc4;
                    padding: 6px 12px;
                    border-radius: 8px;
                    font-size: 0.8rem;
                    font-weight: 700;
                    border: 1px solid rgba(78, 205, 196, 0.3);
                    box-shadow: 0 2px 12px rgba(0,0,0,0.4);
                    backdrop-filter: blur(10px);
                    text-shadow: 0 0 8px rgba(78, 205, 196, 0.5);
                }
                
                .progress-bar {
                    position: absolute;
                    bottom: 0;
                    left: 0;
                    height: 6px;
                    background: linear-gradient(90deg, #ff6b6b, #4ecdc4);
                    transition: width 0.3s ease;
                    border-radius: 0 0 0 15px;
                    box-shadow: 0 0 15px rgba(255, 107, 107, 0.5);
                    z-index: 4;
                }
                
                .movie-info {
                    padding: 20px;
                }
                
                .movie-title {
                    font-size: 1.2rem;
                    font-weight: 700;
                    margin-bottom: 10px;
                    color: white;
                    line-height: 1.4;
                }
                
                .movie-details {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 15px;
                }
                
                .movie-size {
                    display: flex;
                    align-items: center;
                    gap: 8px;
                    color: rgba(255, 255, 255, 0.7);
                    font-size: 0.9rem;
                }
                
                .status-badge {
                    padding: 4px 12px;
                    border-radius: 12px;
                    font-size: 0.8rem;
                    font-weight: 600;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                }
                
                .status-watched {
                    background: linear-gradient(135deg, #4ecdc4, #45b7d1);
                    color: white;
                }
                
                .status-watching {
                    background: linear-gradient(135deg, #ff6b6b, #ee5a24);
                    color: white;
                }
                
                .movie-actions {
                    display: flex;
                    gap: 12px;
                }
                
                .btn {
                    padding: 12px 20px;
                    border-radius: 12px;
                    text-decoration: none;
                    font-weight: 600;
                    font-size: 0.9rem;
                    display: flex;
                    align-items: center;
                    gap: 8px;
                    transition: all 0.3s ease;
                    text-align: center;
                    justify-content: center;
                    touch-action: manipulation;
                    min-height: 48px;
                }
                
                .btn-play {
                    background: linear-gradient(135deg, #ff6b6b, #ee5a24);
                    color: white;
                    flex: 1;
                    box-shadow: 0 4px 15px rgba(255, 107, 107, 0.3);
                }
                
                .btn-play:active {
                    transform: scale(0.95);
                    box-shadow: 0 2px 8px rgba(255, 107, 107, 0.5);
                }
                
                .btn-download {
                    background: rgba(255, 255, 255, 0.1);
                    color: white;
                    border: 1px solid rgba(255, 255, 255, 0.2);
                    padding: 12px;
                    min-width: 48px;
                }
                
                .no-movies {
                    text-align: center;
                    padding: 60px 20px;
                    color: rgba(255, 255, 255, 0.7);
                }
                
                .no-movies h2 {
                    font-size: 1.5rem;
                    margin-bottom: 15px;
                    color: white;
                }
                
                @keyframes rotate {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(360deg); }
                }
                
                @keyframes cinematicFloat {
                    0%, 100% { 
                        transform: translateY(0px) rotate(0deg) scale(1); 
                        opacity: 0.4;
                    }
                    50% { 
                        transform: translateY(-15px) rotate(2deg) scale(1.1); 
                        opacity: 0.6;
                    }
                }
                
                @media (max-width: 480px) {
                    .logo h1 {
                        font-size: 2rem;
                    }
                    
                    .movies-grid {
                        grid-template-columns: 1fr;
                        gap: 15px;
                    }
                    
                    .movie-poster {
                        height: 160px;
                    }
                    
                    .movie-info {
                        padding: 15px;
                    }
                }
            </style>
        </head>
        <body>
            <div class="header">
                <div class="logo">
                    <div class="logo-icon">🎬</div>
                    <h1>CineStream</h1>
                </div>
                <p class="subtitle">Premium Mobile Cinema Experience</p>
                <div class="dolby-badges">
                    <div class="dolby-badge vision">
                        🎯 Dolby Vision
                    </div>
                    <div class="dolby-badge atmos">
                        🔊 Dolby Atmos
                    </div>
                    <div class="dolby-badge">
                        📱 Mobile Optimized
                    </div>
                </div>
            </div>
            
            <div class="movies-section">
                <h2 class="section-title">Your Cinema Library</h2>
                
                {% if movies %}
                    <div class="movies-grid">
                        {% for movie in movies %}
                        <div class="movie-card">
                            <div class="movie-poster">
                                {% if movie.watch_percentage > 0 %}
                                <div class="progress-bar" style="width: {{ movie.watch_percentage }}%;"></div>
                                {% endif %}
                                <div class="movie-overlay">
                                    <div class="dolby-indicators">
                                        <span class="dolby-mini vision">DV</span>
                                        <span class="dolby-mini atmos">DA</span>
                                    </div>
                                    <div class="quality-badge">HD</div>
                                </div>
                            </div>
                            <div class="movie-info">
                                <h3 class="movie-title">{{ movie.name }}</h3>
                                <div class="movie-details">
                                    <div class="movie-size">
                                        📁 {{ movie.size }} GB
                                    </div>
                                    {% if movie.is_watched %}
                                        <div class="status-badge status-watched">Watched</div>
                                    {% elif movie.is_watching %}
                                        <div class="status-badge status-watching">{{ movie.watch_percentage|int }}%</div>
                                    {% endif %}
                                </div>
                                <div class="movie-actions">
                                    <a href="/player/{{ movie.filename|urlencode }}" class="btn btn-play">
                                        ▶️ Play
                                    </a>
                                    <a href="{{ movie.download_url }}" class="btn btn-download" download>
                                        💾
                                    </a>
                                </div>
                            </div>
                        </div>
                        {% endfor %}
                    </div>
                {% else %}
                    <div class="no-movies">
                        <h2>🎬 No Movies Found</h2>
                        <p>Add your movie files to the Movies folder to start streaming.<br>
                        Supported formats: MP4, AVI, MKV, MOV, WMV, 3GP</p>
                        <p style="margin-top: 15px; font-size: 0.9rem;">
                            Movies folder: {{ movies_folder }}
                        </p>
                    </div>
                {% endif %}
            </div>
        </body>
        </html>
        """
        
        return render_template_string(html_template, movies=movies, movies_folder=self.movies_folder)
    
    def render_mobile_player(self, filename):
        """Render mobile video player"""
        movie_path = os.path.join(self.movies_folder, filename)
        if not os.path.exists(movie_path):
            return "Movie not found", 404
        
        # Get watch progress
        progress = self.watch_progress.get(filename, {})
        resume_time = progress.get('current_time', 0)
        movie_name = os.path.splitext(filename)[0]
        
        # Mobile-optimized player template would go here
        # For brevity, using a simple player
        player_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>CineStream - {movie_name}</title>
            <style>
                body {{ margin: 0; padding: 0; background: #000; }}
                video {{ width: 100vw; height: 100vh; object-fit: contain; }}
            </style>
        </head>
        <body>
            <video controls autoplay playsinline>
                <source src="/stream/{quote(filename)}" type="video/mp4">
            </video>
            <script>
                const video = document.querySelector('video');
                video.currentTime = {resume_time};
                
                // Save progress every 10 seconds
                setInterval(() => {{
                    if (!video.paused) {{
                        fetch('/save-progress', {{
                            method: 'POST',
                            headers: {{'Content-Type': 'application/json'}},
                            body: JSON.stringify({{
                                filename: '{filename}',
                                current_time: video.currentTime,
                                duration: video.duration
                            }})
                        }});
                    }}
                }}, 10000);
            </script>
        </body>
        </html>
        """
        
        return player_template
    
    def stream_video_file(self, filename):
        """Stream video file with range support"""
        try:
            filepath = os.path.join(self.movies_folder, filename)
            if not os.path.exists(filepath):
                return "File not found", 404
            
            # Handle range requests for mobile streaming
            range_header = request.headers.get('Range', None)
            if not range_header:
                return send_file(filepath)
            
            file_size = os.path.getsize(filepath)
            byte_start = 0
            byte_end = file_size - 1
            
            match = re.search(r'bytes=(\d+)-(\d*)', range_header)
            if match:
                byte_start = int(match.group(1))
                if match.group(2):
                    byte_end = int(match.group(2))
            
            content_length = byte_end - byte_start + 1
            
            def generate():
                with open(filepath, 'rb') as f:
                    f.seek(byte_start)
                    remaining = content_length
                    chunk_size = 8192
                    
                    while remaining:
                        read_size = min(chunk_size, remaining)
                        data = f.read(read_size)
                        if not data:
                            break
                        remaining -= len(data)
                        yield data
            
            headers = {
                'Content-Range': f'bytes {byte_start}-{byte_end}/{file_size}',
                'Accept-Ranges': 'bytes',
                'Content-Length': str(content_length),
                'Content-Type': 'video/mp4',
            }
            
            return Response(generate(), 206, headers)
            
        except Exception as e:
            Logger.error(f'Streaming error: {e}')
            return "Streaming error", 500
    
    def download_movie_file(self, filename):
        """Download movie file"""
        try:
            filepath = os.path.join(self.movies_folder, filename)
            if os.path.exists(filepath):
                return send_file(filepath, as_attachment=True, download_name=filename)
            else:
                return "File not found", 404
        except Exception as e:
            Logger.error(f'Download error: {e}')
            return "Download error", 500
    
    def save_progress_endpoint(self):
        """Save watch progress endpoint"""
        try:
            data = request.get_json()
            filename = data.get('filename')
            current_time = data.get('current_time', 0)
            duration = data.get('duration', 0)
            
            if filename and duration > 0:
                percentage = (current_time / duration) * 100
                
                if filename not in self.watch_progress:
                    self.watch_progress[filename] = {}
                
                self.watch_progress[filename].update({
                    'current_time': current_time,
                    'duration': duration,
                    'percentage': percentage,
                    'last_watched': time.strftime('%Y-%m-%d %H:%M:%S')
                })
                
                self.save_progress()
            
            return jsonify({'status': 'success'})
        except Exception as e:
            Logger.error(f'Save progress error: {e}')
            return jsonify({'status': 'error'}), 500

class CineStreamApp(App):
    """Main Kivy application class"""
    
    def build(self):
        Window.fullscreen = 'auto'
        Window.orientation = 'all'
        
        # Request permissions on Android
        if platform == 'android':
            self.request_android_permissions()
        
        # Initialize movie streamer
        self.streamer = MovieStreamer()
        
        # Start Flask server in background thread
        self.start_flask_server()
        
        # Create main layout
        return self.create_main_layout()
    
    def request_android_permissions(self):
        """Request necessary Android permissions"""
        permissions = [
            Permission.READ_EXTERNAL_STORAGE,
            Permission.WRITE_EXTERNAL_STORAGE,
            Permission.INTERNET,
            Permission.ACCESS_NETWORK_STATE,
            Permission.WAKE_LOCK
        ]
        request_permissions(permissions)
    
    def start_flask_server(self):
        """Start Flask server in background thread"""
        def run_server():
            try:
                self.streamer.app.run(host='127.0.0.1', port=5000, debug=False, threaded=True)
            except Exception as e:
                Logger.error(f'Flask server error: {e}')
        
        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()
        
        # Wait a moment for server to start
        time.sleep(2)
    
    def create_main_layout(self):
        """Create the main app layout"""
        layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
        
        # Header
        header = BoxLayout(orientation='horizontal', size_hint_y=None, height=80)
        
        logo_label = Label(
            text='🎬 CineStream Mobile',
            font_size='24sp',
            color=(1, 1, 1, 1),
            bold=True
        )
        header.add_widget(logo_label)
        
        # Refresh button
        refresh_btn = Button(
            text='🔄 Refresh',
            size_hint_x=None,
            width=120,
            background_color=(1, 0.42, 0.42, 1)
        )
        refresh_btn.bind(on_press=self.refresh_movies)
        header.add_widget(refresh_btn)
        
        layout.add_widget(header)
        
        # Movies info
        self.info_label = Label(
            text=f'Movies folder: {self.streamer.movies_folder}',
            font_size='14sp',
            color=(0.8, 0.8, 0.8, 1),
            size_hint_y=None,
            height=40,
            text_size=(None, None)
        )
        layout.add_widget(self.info_label)
        
        # Movies list
        self.create_movies_list(layout)
        
        # Web viewer button
        web_btn = Button(
            text='🌐 Open Web Interface',
            size_hint_y=None,
            height=60,
            background_color=(0.3, 0.8, 0.8, 1),
            font_size='18sp'
        )
        web_btn.bind(on_press=self.open_web_interface)
        layout.add_widget(web_btn)
        
        return layout
    
    def create_movies_list(self, parent_layout):
        """Create scrollable movies list"""
        # Movies scroll view
        scroll = ScrollView()
        
        self.movies_layout = GridLayout(
            cols=1,
            size_hint_y=None,
            spacing=10,
            padding=10
        )
        self.movies_layout.bind(minimum_height=self.movies_layout.setter('height'))
        
        scroll.add_widget(self.movies_layout)
        parent_layout.add_widget(scroll)
        
        # Load movies
        self.load_movies()
    
    def load_movies(self):
        """Load and display movies"""
        self.movies_layout.clear_widgets()
        
        movies = self.streamer.get_movies()
        
        if not movies:
            no_movies_label = Label(
                text='No movies found\\nAdd movies to: ' + self.streamer.movies_folder,
                font_size='16sp',
                color=(0.8, 0.8, 0.8, 1),
                halign='center',
                size_hint_y=None,
                height=120,
                text_size=(None, None)
            )
            self.movies_layout.add_widget(no_movies_label)
            return
        
        for movie in movies:
            movie_layout = BoxLayout(
                orientation='horizontal',
                size_hint_y=None,
                height=80,
                padding=10,
                spacing=10
            )
            
            # Movie info
            info_layout = BoxLayout(orientation='vertical')
            
            title_label = Label(
                text=movie['name'],
                font_size='16sp',
                color=(1, 1, 1, 1),
                bold=True,
                halign='left',
                size_hint_y=None,
                height=30,
                text_size=(None, None)
            )
            
            details_label = Label(
                text=f"{movie['size']} GB",
                font_size='12sp',
                color=(0.7, 0.7, 0.7, 1),
                halign='left',
                size_hint_y=None,
                height=20,
                text_size=(None, None)
            )
            
            info_layout.add_widget(title_label)
            info_layout.add_widget(details_label)
            
            # Progress bar
            if movie['watch_percentage'] > 0:
                progress = ProgressBar(
                    max=100,
                    value=movie['watch_percentage'],
                    size_hint_y=None,
                    height=20
                )
                info_layout.add_widget(progress)
            
            movie_layout.add_widget(info_layout)
            
            # Play button
            play_btn = Button(
                text='▶️ Play',
                size_hint_x=None,
                width=100,
                background_color=(1, 0.42, 0.42, 1)
            )
            play_btn.bind(on_press=lambda x, filename=movie['filename']: self.play_movie(filename))
            movie_layout.add_widget(play_btn)
            
            self.movies_layout.add_widget(movie_layout)
    
    def refresh_movies(self, instance):
        """Refresh movies list"""
        self.load_movies()
    
    def play_movie(self, filename):
        """Play movie using web interface"""
        import webbrowser
        url = f'http://127.0.0.1:5000/player/{quote(filename)}'
        
        if platform == 'android':
            # Use Android intent to open URL
            try:
                from jnius import autoclass
                Intent = autoclass('android.content.Intent')
                Uri = autoclass('android.net.Uri')
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                
                intent = Intent()
                intent.setAction(Intent.ACTION_VIEW)
                intent.setData(Uri.parse(url))
                PythonActivity.mActivity.startActivity(intent)
            except Exception as e:
                Logger.error(f'Error opening movie: {e}')
        else:
            webbrowser.open(url)
    
    def open_web_interface(self, instance):
        """Open web interface"""
        import webbrowser
        url = 'http://127.0.0.1:5000'
        
        if platform == 'android':
            # Use Android intent to open URL
            try:
                from jnius import autoclass
                Intent = autoclass('android.content.Intent')
                Uri = autoclass('android.net.Uri')
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                
                intent = Intent()
                intent.setAction(Intent.ACTION_VIEW)
                intent.setData(Uri.parse(url))
                PythonActivity.mActivity.startActivity(intent)
            except Exception as e:
                Logger.error(f'Error opening web interface: {e}')
        else:
            webbrowser.open(url)

if __name__ == '__main__':
    CineStreamApp().run()