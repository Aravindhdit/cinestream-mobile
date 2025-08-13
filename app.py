from flask import Flask, render_template_string, send_file, jsonify, request, Response
import os
import mimetypes
import re
import json
import time
from urllib.parse import quote
import socket
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")

# Configuration
MOVIES_FOLDER = os.environ.get("MOVIES_FOLDER", "./movies")
ALLOWED_EXTENSIONS = {'.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v'}
PROGRESS_FILE = "watch_progress.json"

def get_local_ip():
    """Get the local IP address"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except:
        return "127.0.0.1"

def load_progress():
    """Load watch progress from file"""
    try:
        if os.path.exists(PROGRESS_FILE):
            with open(PROGRESS_FILE, 'r') as f:
                return json.load(f)
    except:
        pass
    return {}

def save_progress():
    """Save watch progress to file"""
    try:
        with open(PROGRESS_FILE, 'w') as f:
            json.dump(watch_progress, f)
    except:
        pass

# Global progress tracking
watch_progress = load_progress()

def get_movies():
    """Get all movies from the movies folder"""
    movies = []
    
    # Create movies folder if it doesn't exist
    if not os.path.exists(MOVIES_FOLDER):
        os.makedirs(MOVIES_FOLDER)
        return movies
    
    for filename in os.listdir(MOVIES_FOLDER):
        if any(filename.lower().endswith(ext) for ext in ALLOWED_EXTENSIONS):
            filepath = os.path.join(MOVIES_FOLDER, filename)
            file_size = os.path.getsize(filepath)
            file_size_gb = round(file_size / (1024 * 1024 * 1024), 2)
            
            # Get watch progress
            progress = watch_progress.get(filename, {})
            watch_percentage = progress.get('percentage', 0)
            last_watched = progress.get('last_watched', None)
            
            movies.append({
                'filename': filename,
                'name': os.path.splitext(filename)[0],
                'size': file_size_gb,
                'url': f"/stream/{quote(filename)}",
                'download_url': f"/download/{quote(filename)}",
                'watch_percentage': watch_percentage,
                'last_watched': last_watched,
                'is_watched': watch_percentage > 90,
                'is_watching': 5 < watch_percentage < 90
            })
    
    return sorted(movies, key=lambda x: x['name'].lower())

@app.route('/')
def index():
    """Main page showing all movies"""
    movies = get_movies()
    
    html_template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
        <title>CineStream - Premium Mobile Cinema</title>
        <link rel="stylesheet" href="/static/mobile-player.css">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
                -webkit-tap-highlight-color: transparent;
            }
            
            body {
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                background: #000000;
                color: #ffffff;
                overflow-x: hidden;
                line-height: 1.6;
                touch-action: manipulation;
            }
            
            .hero-section {
                background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 30%, #16213e 70%, #0f0f23 100%);
                position: relative;
                padding: 60px 0 40px 0;
                overflow: hidden;
                min-height: 50vh;
            }
            
            .hero-section::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: radial-gradient(circle at 50% 50%, rgba(255, 107, 107, 0.1) 0%, transparent 70%);
                animation: breathe 4s ease-in-out infinite;
            }
            
            @keyframes breathe {
                0%, 100% { opacity: 0.3; transform: scale(1); }
                50% { opacity: 0.6; transform: scale(1.1); }
            }
            
            .container {
                max-width: 1400px;
                margin: 0 auto;
                padding: 0 20px;
                position: relative;
                z-index: 2;
            }
            
            .header {
                display: flex;
                align-items: center;
                justify-content: center;
                flex-direction: column;
                text-align: center;
            }
            
            .logo {
                display: flex;
                align-items: center;
                gap: 15px;
                margin-bottom: 25px;
                flex-direction: column;
            }
            
            @media (min-width: 768px) {
                .logo { flex-direction: row; gap: 20px; }
            }
            
            .logo-icon {
                width: 70px;
                height: 70px;
                background: linear-gradient(135deg, #ff6b6b, #4ecdc4, #45b7d1);
                border-radius: 20px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 1.8rem;
                box-shadow: 0 15px 35px rgba(255, 107, 107, 0.4);
                animation: pulse 2s ease-in-out infinite alternate;
                touch-action: manipulation;
            }
            
            @media (min-width: 768px) {
                .logo-icon {
                    width: 80px;
                    height: 80px;
                    font-size: 2rem;
                }
            }
            
            @keyframes pulse {
                0% { transform: scale(1); box-shadow: 0 15px 35px rgba(255, 107, 107, 0.4); }
                100% { transform: scale(1.05); box-shadow: 0 20px 45px rgba(255, 107, 107, 0.6); }
            }
            
            .logo h1 {
                font-size: 2.5rem;
                font-weight: 800;
                background: linear-gradient(135deg, #ffffff, #a8edea, #fed6e3);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                letter-spacing: -1px;
                margin-bottom: 10px;
            }
            
            @media (min-width: 768px) {
                .logo h1 {
                    font-size: 3.5rem;
                    letter-spacing: -2px;
                    margin-bottom: 0;
                }
            }
            
            .subtitle {
                font-size: 1.1rem;
                color: rgba(255, 255, 255, 0.7);
                margin-bottom: 25px;
                text-align: center;
            }
            
            @media (min-width: 768px) {
                .subtitle { font-size: 1.3rem; }
            }
            
            .dolby-badges {
                display: flex;
                gap: 15px;
                justify-content: center;
                flex-wrap: wrap;
            }
            
            .badge {
                padding: 10px 18px;
                background: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 25px;
                font-size: 0.85rem;
                font-weight: 600;
                backdrop-filter: blur(10px);
                display: flex;
                align-items: center;
                gap: 8px;
                touch-action: manipulation;
                transition: all 0.3s ease;
            }
            
            .badge:hover {
                background: rgba(255, 255, 255, 0.15);
                transform: translateY(-2px);
            }
            
            @media (min-width: 768px) {
                .badge {
                    padding: 8px 16px;
                    font-size: 0.9rem;
                }
            }
            
            .content-section {
                background: #0a0a0a;
                padding: 40px 0 60px 0;
                min-height: 50vh;
            }
            
            .section-title {
                font-size: 1.8rem;
                font-weight: 700;
                margin-bottom: 30px;
                color: #ffffff;
                text-align: center;
            }
            
            @media (min-width: 768px) {
                .section-title {
                    font-size: 2rem;
                    text-align: left;
                }
            }
            
            .movies-grid {
                display: grid;
                grid-template-columns: 1fr;
                gap: 20px;
                margin-top: 30px;
            }
            
            @media (min-width: 480px) {
                .movies-grid {
                    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
                    gap: 25px;
                }
            }
            
            @media (min-width: 768px) {
                .movies-grid {
                    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
                    gap: 30px;
                }
            }
            
            .movie-card {
                background: linear-gradient(145deg, #1a1a2e 0%, #16213e 100%);
                border-radius: 15px;
                overflow: hidden;
                position: relative;
                transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
                border: 1px solid rgba(255, 255, 255, 0.1);
                box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
                touch-action: manipulation;
            }
            
            @media (min-width: 768px) {
                .movie-card {
                    border-radius: 20px;
                    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
                }
            }
            
            .movie-card:hover {
                transform: translateY(-8px) scale(1.02);
                box-shadow: 0 20px 50px rgba(255, 107, 107, 0.2);
                border-color: rgba(255, 107, 107, 0.3);
            }
            
            @media (min-width: 768px) {
                .movie-card:hover {
                    transform: translateY(-10px) scale(1.02);
                    box-shadow: 0 25px 60px rgba(255, 107, 107, 0.2);
                }
            }
            
            .movie-poster {
                height: 140px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
                position: relative;
                display: flex;
                align-items: center;
                justify-content: center;
                overflow: hidden;
            }
            
            @media (min-width: 768px) {
                .movie-poster { height: 180px; }
            }
            
            .movie-poster::before {
                content: '🎬';
                font-size: 3rem;
                opacity: 0.3;
                position: absolute;
                animation: float 3s ease-in-out infinite;
            }
            
            @media (min-width: 768px) {
                .movie-poster::before { font-size: 4rem; }
            }
            
            @keyframes float {
                0%, 100% { transform: translateY(0px); }
                50% { transform: translateY(-10px); }
            }
            
            .progress-bar {
                position: absolute;
                bottom: 0;
                left: 0;
                height: 4px;
                background: linear-gradient(90deg, #ff6b6b, #4ecdc4);
                transition: width 0.3s ease;
                border-radius: 0 0 0 15px;
            }
            
            @media (min-width: 768px) {
                .progress-bar { border-radius: 0 0 0 20px; }
            }
            
            .movie-info {
                padding: 20px;
            }
            
            @media (min-width: 768px) {
                .movie-info { padding: 25px; }
            }
            
            .movie-title {
                font-size: 1.2rem;
                font-weight: 700;
                margin-bottom: 12px;
                color: #ffffff;
                line-height: 1.3;
                display: -webkit-box;
                -webkit-line-clamp: 2;
                -webkit-box-orient: vertical;
                overflow: hidden;
            }
            
            @media (min-width: 768px) {
                .movie-title { font-size: 1.3rem; }
            }
            
            .movie-details {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 20px;
                color: rgba(255, 255, 255, 0.6);
                font-size: 0.85rem;
                flex-wrap: wrap;
                gap: 10px;
            }
            
            @media (min-width: 768px) {
                .movie-details {
                    font-size: 0.9rem;
                    flex-wrap: nowrap;
                    gap: 0;
                }
            }
            
            .movie-size {
                display: flex;
                align-items: center;
                gap: 5px;
            }
            
            .status-badge {
                padding: 6px 12px;
                border-radius: 15px;
                font-size: 0.75rem;
                font-weight: 600;
                text-transform: uppercase;
            }
            
            @media (min-width: 768px) {
                .status-badge {
                    padding: 4px 12px;
                    font-size: 0.8rem;
                }
            }
            
            .status-watching {
                background: rgba(255, 193, 7, 0.2);
                color: #ffc107;
                border: 1px solid rgba(255, 193, 7, 0.3);
            }
            
            .status-watched {
                background: rgba(40, 167, 69, 0.2);
                color: #28a745;
                border: 1px solid rgba(40, 167, 69, 0.3);
            }
            
            .movie-actions {
                display: flex;
                gap: 10px;
                flex-direction: column;
            }
            
            @media (min-width: 480px) {
                .movie-actions {
                    flex-direction: row;
                    gap: 12px;
                }
            }
            
            .btn {
                padding: 14px 20px;
                border: none;
                border-radius: 12px;
                text-decoration: none;
                font-weight: 600;
                font-size: 0.9rem;
                cursor: pointer;
                transition: all 0.3s ease;
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 8px;
                position: relative;
                overflow: hidden;
                touch-action: manipulation;
                min-height: 48px;
            }
            
            .btn::before {
                content: '';
                position: absolute;
                top: 0;
                left: -100%;
                width: 100%;
                height: 100%;
                background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent);
                transition: left 0.5s;
            }
            
            .btn:hover::before {
                left: 100%;
            }
            
            .btn-play {
                background: linear-gradient(135deg, #ff6b6b, #ee5a24);
                color: white;
                flex: 1;
                box-shadow: 0 6px 20px rgba(255, 107, 107, 0.3);
            }
            
            .btn-play:hover {
                transform: translateY(-2px);
                box-shadow: 0 10px 30px rgba(255, 107, 107, 0.4);
            }
            
            .btn-download {
                background: rgba(255, 255, 255, 0.1);
                color: #ffffff;
                border: 1px solid rgba(255, 255, 255, 0.2);
                backdrop-filter: blur(10px);
                flex: 1;
            }
            
            @media (min-width: 480px) {
                .btn-download { flex: 0 0 auto; }
            }
            
            .btn-download:hover {
                background: rgba(255, 255, 255, 0.15);
                transform: translateY(-2px);
            }
            
            .no-movies {
                text-align: center;
                padding: 80px 20px;
                color: rgba(255, 255, 255, 0.6);
            }
            
            @media (min-width: 768px) {
                .no-movies { padding: 100px 20px; }
            }
            
            .no-movies h2 {
                margin-bottom: 15px;
                color: #ffffff;
                font-size: 1.8rem;
            }
            
            @media (min-width: 768px) {
                .no-movies h2 { font-size: 2rem; margin-bottom: 20px; }
            }
            
            .no-movies p {
                font-size: 1rem;
                line-height: 1.6;
                max-width: 500px;
                margin: 0 auto;
            }
            
            /* Touch-friendly improvements */
            @media (hover: none) and (pointer: coarse) {
                .movie-card:hover {
                    transform: none;
                    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
                    border-color: rgba(255, 255, 255, 0.1);
                }
                
                .btn:hover {
                    transform: none;
                }
                
                .btn-play:hover {
                    box-shadow: 0 6px 20px rgba(255, 107, 107, 0.3);
                }
                
                .badge:hover {
                    background: rgba(255, 255, 255, 0.1);
                    transform: none;
                }
            }
        </style>
    </head>
    <body>
        <div class="hero-section">
            <div class="container">
                <div class="header">
                    <div class="logo">
                        <div class="logo-icon">🎬</div>
                        <h1>CineStream</h1>
                    </div>
                    <p class="subtitle">Premium Mobile Cinema Experience</p>
                    <div class="dolby-badges">
                        <div class="badge">
                            <i class="fas fa-film"></i>
                            <span>Dolby Vision</span>
                        </div>
                        <div class="badge">
                            <i class="fas fa-volume-up"></i>
                            <span>Dolby Atmos</span>
                        </div>
                        <div class="badge">
                            <i class="fas fa-mobile-alt"></i>
                            <span>Mobile Optimized</span>
                        </div>
                        <div class="badge">
                            <i class="fas fa-hd-video"></i>
                            <span>4K Ready</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="content-section">
            <div class="container">
                <h2 class="section-title">
                    <i class="fas fa-video" style="margin-right: 10px; color: #ff6b6b;"></i>
                    Your Cinema Library
                </h2>
                
                {% if movies %}
                    <div class="movies-grid">
                        {% for movie in movies %}
                        <div class="movie-card">
                            <div class="movie-poster">
                                {% if movie.watch_percentage > 0 %}
                                <div class="progress-bar" style="width: {{ movie.watch_percentage }}%;"></div>
                                {% endif %}
                            </div>
                            <div class="movie-info">
                                <h3 class="movie-title">{{ movie.name }}</h3>
                                <div class="movie-details">
                                    <div class="movie-size">
                                        <i class="fas fa-file-video"></i>
                                        <span>{{ movie.size }} GB</span>
                                    </div>
                                    {% if movie.is_watched %}
                                        <div class="status-badge status-watched">Watched</div>
                                    {% elif movie.is_watching %}
                                        <div class="status-badge status-watching">{{ movie.watch_percentage|int }}%</div>
                                    {% endif %}
                                </div>
                                <div class="movie-actions">
                                    <a href="/play/{{ movie.filename|urlencode }}" class="btn btn-play">
                                        <i class="fas fa-play"></i>
                                        <span>Play</span>
                                    </a>
                                    <a href="{{ movie.download_url }}" class="btn btn-download" download>
                                        <i class="fas fa-download"></i>
                                    </a>
                                </div>
                            </div>
                        </div>
                        {% endfor %}
                    </div>
                {% else %}
                    <div class="no-movies">
                        <h2><i class="fas fa-film" style="color: #ff6b6b; margin-right: 15px;"></i>No Movies Found</h2>
                        <p>Add your movie files to the movies directory to start streaming. Supported formats: MP4, AVI, MKV, MOV, WMV, FLV, WebM, M4V</p>
                    </div>
                {% endif %}
            </div>
        </div>
    </body>
    </html>
    """
    
    return render_template_string(html_template, movies=movies)

@app.route('/play/<filename>')
def play_movie(filename):
    """Movie player page with enhanced mobile features"""
    movie_path = os.path.join(MOVIES_FOLDER, filename)
    if not os.path.exists(movie_path):
        return "Movie not found", 404
    
    # Get watch progress
    progress = watch_progress.get(filename, {})
    resume_time = progress.get('current_time', 0)
    watch_percentage = progress.get('percentage', 0)
    
    movie_name = os.path.splitext(filename)[0]
    
    html_template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
        <title>{{ movie_name }} - CineStream</title>
        <link rel="stylesheet" href="/static/mobile-player.css">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
                -webkit-tap-highlight-color: transparent;
            }
            
            body {
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                background: #000000;
                color: #ffffff;
                overflow: hidden;
                touch-action: manipulation;
            }
            
            .player-container {
                position: relative;
                width: 100vw;
                height: 100vh;
                background: #000000;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            
            .cinematic-bars {
                position: absolute;
                left: 0;
                right: 0;
                background: #000000;
                z-index: 5;
                transition: all 0.8s cubic-bezier(0.25, 0.46, 0.45, 0.94);
                opacity: 0;
            }
            
            .cinematic-bars.active {
                opacity: 1;
            }
            
            .cinematic-bars.top {
                top: 0;
                height: 12vh;
                box-shadow: 0 5px 20px rgba(0,0,0,0.8);
            }
            
            .cinematic-bars.bottom {
                bottom: 0;
                height: 12vh;
                box-shadow: 0 -5px 20px rgba(0,0,0,0.8);
            }
            
            .theater-vignette {
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: radial-gradient(ellipse at center, transparent 30%, rgba(0,0,0,0.3) 70%, rgba(0,0,0,0.8) 100%);
                z-index: 4;
                opacity: 0;
                transition: opacity 0.8s ease;
                pointer-events: none;
            }
            
            .theater-vignette.active {
                opacity: 1;
            }
            
            #movieVideo {
                width: 100%;
                height: 100%;
                object-fit: contain;
                background: #000000;
                outline: none;
            }
            
            .mobile-controls {
                position: absolute;
                bottom: 0;
                left: 0;
                right: 0;
                background: linear-gradient(to top, rgba(0,0,0,0.9) 0%, rgba(0,0,0,0.7) 50%, transparent 100%);
                padding: 20px;
                z-index: 10;
                transition: all 0.5s ease;
                transform: translateY(0);
                touch-action: manipulation;
            }
            
            .mobile-controls.hidden {
                transform: translateY(100%);
                opacity: 0;
            }
            
            .controls-row {
                display: flex;
                align-items: center;
                gap: 15px;
                margin-bottom: 15px;
            }
            
            .control-btn {
                background: rgba(255,255,255,0.2);
                border: none;
                border-radius: 50%;
                width: 48px;
                height: 48px;
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                font-size: 18px;
                cursor: pointer;
                transition: all 0.3s ease;
                touch-action: manipulation;
                backdrop-filter: blur(10px);
            }
            
            .control-btn:hover {
                background: rgba(255,255,255,0.3);
                transform: scale(1.1);
            }
            
            .play-pause-btn {
                width: 60px;
                height: 60px;
                background: linear-gradient(135deg, #ff6b6b, #ee5a24);
                font-size: 24px;
            }
            
            .progress-container {
                flex: 1;
                margin: 0 10px;
                position: relative;
            }
            
            .progress-bar {
                width: 100%;
                height: 8px;
                background: rgba(255,255,255,0.2);
                border-radius: 4px;
                cursor: pointer;
                position: relative;
                overflow: hidden;
            }
            
            .progress-fill {
                height: 100%;
                background: linear-gradient(90deg, #ff6b6b, #4ecdc4);
                border-radius: 4px;
                transition: width 0.3s ease;
                position: relative;
            }
            
            .progress-buffer {
                position: absolute;
                top: 0;
                left: 0;
                height: 100%;
                background: rgba(255,255,255,0.3);
                border-radius: 4px;
                transition: width 0.3s ease;
            }
            
            .time-display {
                color: rgba(255,255,255,0.8);
                font-size: 14px;
                font-weight: 500;
                min-width: 80px;
                text-align: center;
            }
            
            .quality-selector {
                position: relative;
            }
            
            .quality-btn {
                background: rgba(255,255,255,0.2);
                border: none;
                border-radius: 8px;
                padding: 8px 12px;
                color: white;
                font-size: 12px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
                touch-action: manipulation;
                backdrop-filter: blur(10px);
            }
            
            .quality-dropdown {
                position: absolute;
                bottom: 50px;
                right: 0;
                background: rgba(0,0,0,0.9);
                border-radius: 8px;
                padding: 10px;
                display: none;
                flex-direction: column;
                gap: 5px;
                backdrop-filter: blur(20px);
                border: 1px solid rgba(255,255,255,0.1);
            }
            
            .quality-dropdown.active {
                display: flex;
            }
            
            .quality-option {
                background: transparent;
                border: none;
                color: white;
                padding: 8px 12px;
                border-radius: 6px;
                cursor: pointer;
                font-size: 12px;
                transition: all 0.3s ease;
                touch-action: manipulation;
            }
            
            .quality-option:hover, .quality-option.active {
                background: rgba(255,107,107,0.3);
            }
            
            .top-controls {
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                background: linear-gradient(to bottom, rgba(0,0,0,0.9) 0%, rgba(0,0,0,0.7) 50%, transparent 100%);
                padding: 20px;
                z-index: 10;
                display: flex;
                align-items: center;
                gap: 15px;
                transition: all 0.5s ease;
                transform: translateY(0);
            }
            
            .top-controls.hidden {
                transform: translateY(-100%);
                opacity: 0;
            }
            
            .back-btn {
                background: rgba(255,255,255,0.2);
                border: none;
                border-radius: 8px;
                padding: 10px 12px;
                color: white;
                font-size: 16px;
                cursor: pointer;
                transition: all 0.3s ease;
                touch-action: manipulation;
                backdrop-filter: blur(10px);
            }
            
            .movie-title {
                flex: 1;
                font-size: 18px;
                font-weight: 600;
                color: white;
                text-overflow: ellipsis;
                overflow: hidden;
                white-space: nowrap;
            }
            
            .overlay-message {
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                background: rgba(0,0,0,0.9);
                padding: 30px;
                border-radius: 15px;
                text-align: center;
                z-index: 20;
                backdrop-filter: blur(20px);
                border: 1px solid rgba(255,255,255,0.1);
                max-width: 90%;
                display: none;
            }
            
            .overlay-message.active {
                display: block;
                animation: fadeInScale 0.5s ease;
            }
            
            @keyframes fadeInScale {
                0% { opacity: 0; transform: translate(-50%, -50%) scale(0.8); }
                100% { opacity: 1; transform: translate(-50%, -50%) scale(1); }
            }
            
            .overlay-message h3 {
                margin-bottom: 15px;
                font-size: 20px;
                color: white;
            }
            
            .overlay-message p {
                color: rgba(255,255,255,0.8);
                line-height: 1.5;
                margin-bottom: 20px;
            }
            
            .overlay-buttons {
                display: flex;
                gap: 15px;
                justify-content: center;
                flex-wrap: wrap;
            }
            
            .overlay-btn {
                background: linear-gradient(135deg, #ff6b6b, #ee5a24);
                border: none;
                border-radius: 8px;
                padding: 12px 20px;
                color: white;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
                touch-action: manipulation;
            }
            
            .overlay-btn.secondary {
                background: rgba(255,255,255,0.2);
            }
            
            .dolby-overlay {
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: #000000;
                z-index: 30;
                display: none;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                animation: dolbyFade 3s ease-in-out;
            }
            
            .dolby-overlay.active {
                display: flex;
            }
            
            @keyframes dolbyFade {
                0%, 100% { opacity: 0; }
                20%, 80% { opacity: 1; }
            }
            
            .dolby-logo {
                font-size: 3rem;
                margin-bottom: 20px;
                background: linear-gradient(135deg, #ff6b6b, #4ecdc4, #45b7d1);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                animation: dolbyPulse 2s ease-in-out infinite;
            }
            
            @keyframes dolbyPulse {
                0%, 100% { transform: scale(1); }
                50% { transform: scale(1.1); }
            }
            
            .dolby-text {
                font-size: 1.5rem;
                font-weight: 600;
                text-align: center;
                color: white;
                opacity: 0.9;
            }
            
            /* Touch gesture indicators */
            .gesture-indicator {
                position: absolute;
                top: 50%;
                transform: translateY(-50%);
                background: rgba(255,255,255,0.1);
                padding: 15px;
                border-radius: 50%;
                font-size: 24px;
                color: white;
                opacity: 0;
                transition: all 0.3s ease;
                backdrop-filter: blur(10px);
                pointer-events: none;
            }
            
            .gesture-indicator.left {
                left: 50px;
            }
            
            .gesture-indicator.right {
                right: 50px;
            }
            
            .gesture-indicator.show {
                opacity: 1;
                animation: gestureHint 1s ease;
            }
            
            @keyframes gestureHint {
                0%, 100% { transform: translateY(-50%) scale(1); }
                50% { transform: translateY(-50%) scale(1.2); }
            }
            
            /* Responsive adjustments */
            @media (max-width: 480px) {
                .mobile-controls {
                    padding: 15px;
                }
                
                .control-btn {
                    width: 44px;
                    height: 44px;
                    font-size: 16px;
                }
                
                .play-pause-btn {
                    width: 56px;
                    height: 56px;
                    font-size: 22px;
                }
                
                .movie-title {
                    font-size: 16px;
                }
                
                .dolby-logo {
                    font-size: 2.5rem;
                }
                
                .dolby-text {
                    font-size: 1.2rem;
                }
            }
            
            @media (orientation: landscape) and (max-height: 500px) {
                .top-controls, .mobile-controls {
                    padding: 10px 20px;
                }
                
                .controls-row {
                    margin-bottom: 10px;
                }
                
                .cinematic-bars.top, .cinematic-bars.bottom {
                    height: 8vh;
                }
            }
        </style>
    </head>
    <body>
        <div class="player-container">
            <!-- Cinematic bars -->
            <div class="cinematic-bars top"></div>
            <div class="cinematic-bars bottom"></div>
            <div class="theater-vignette"></div>
            
            <!-- Video element -->
            <video id="movieVideo" controls playsinline webkit-playsinline>
                <source src="/stream/{{ filename|urlencode }}" type="video/mp4">
                Your browser does not support the video tag.
            </video>
            
            <!-- Top controls -->
            <div class="top-controls">
                <button class="back-btn" onclick="goBack()">
                    <i class="fas fa-arrow-left"></i>
                </button>
                <div class="movie-title">{{ movie_name }}</div>
                <button class="control-btn" onclick="toggleCinematicMode()">
                    <i class="fas fa-expand"></i>
                </button>
            </div>
            
            <!-- Mobile controls -->
            <div class="mobile-controls">
                <div class="controls-row">
                    <button class="control-btn play-pause-btn" onclick="togglePlayPause()">
                        <i class="fas fa-play" id="playIcon"></i>
                    </button>
                    <button class="control-btn" onclick="skipTime(-10)">
                        <i class="fas fa-backward"></i>
                    </button>
                    <button class="control-btn" onclick="skipTime(10)">
                        <i class="fas fa-forward"></i>
                    </button>
                    <div class="progress-container">
                        <div class="progress-bar" onclick="seekVideo(event)">
                            <div class="progress-buffer"></div>
                            <div class="progress-fill"></div>
                        </div>
                    </div>
                    <div class="time-display">
                        <span id="currentTime">0:00</span> / <span id="totalTime">0:00</span>
                    </div>
                    <button class="control-btn" onclick="toggleMute()">
                        <i class="fas fa-volume-up" id="volumeIcon"></i>
                    </button>
                    <button class="control-btn" onclick="toggleFullscreen()">
                        <i class="fas fa-expand" id="fullscreenIcon"></i>
                    </button>
                    <div class="quality-selector">
                        <button class="quality-btn" onclick="toggleQualityDropdown()">AUTO</button>
                        <div class="quality-dropdown">
                            <button class="quality-option active" data-quality="auto">Auto</button>
                            <button class="quality-option" data-quality="1080p">1080p</button>
                            <button class="quality-option" data-quality="720p">720p</button>
                            <button class="quality-option" data-quality="480p">480p</button>
                            <button class="quality-option" data-quality="360p">360p</button>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Gesture indicators -->
            <div class="gesture-indicator left">
                <i class="fas fa-backward"></i>
            </div>
            <div class="gesture-indicator right">
                <i class="fas fa-forward"></i>
            </div>
            
            <!-- Overlay messages -->
            <div class="overlay-message" id="resumeOverlay">
                <h3>Resume Watching?</h3>
                <p>You were at {{ (resume_time / 60) | int }}:{{ '%02d' | format((resume_time % 60) | int) }}</p>
                <div class="overlay-buttons">
                    <button class="overlay-btn" onclick="resumeMovie()">Resume</button>
                    <button class="overlay-btn secondary" onclick="startFromBeginning()">Start Over</button>
                </div>
            </div>
            
            <div class="overlay-message" id="endingOverlay">
                <h3>Movie Completed</h3>
                <p>Thanks for watching {{ movie_name }}!</p>
                <div class="overlay-buttons">
                    <button class="overlay-btn" onclick="goBack()">Back to Library</button>
                    <button class="overlay-btn secondary" onclick="watchAgain()">Watch Again</button>
                </div>
            </div>
            
            <!-- Dolby overlay -->
            <div class="dolby-overlay" id="dolbyOverlay">
                <div class="dolby-logo">🎬</div>
                <div class="dolby-text">DOLBY VISION • DOLBY ATMOS</div>
            </div>
        </div>
        
        <script src="/static/cinema-controls.js"></script>
        <script>
            // Global variables
            const video = document.getElementById('movieVideo');
            const resumeTime = {{ resume_time }};
            const filename = '{{ filename }}';
            let isControlsVisible = true;
            let controlsTimeout;
            let isCinematicMode = false;
            let progressSaveInterval;
            
            // Initialize player
            document.addEventListener('DOMContentLoaded', function() {
                initializePlayer();
                showDolbyAnimation();
                
                // Show resume overlay if there's progress
                if (resumeTime > 30) {
                    document.getElementById('resumeOverlay').classList.add('active');
                }
            });
            
            function initializePlayer() {
                // Video event listeners
                video.addEventListener('loadedmetadata', updateTotalTime);
                video.addEventListener('timeupdate', updateProgress);
                video.addEventListener('ended', handleMovieEnd);
                video.addEventListener('play', handlePlay);
                video.addEventListener('pause', handlePause);
                video.addEventListener('progress', updateBuffer);
                
                // Touch and gesture handlers
                setupTouchControls();
                setupKeyboardControls();
                
                // Auto-hide controls
                setupControlsAutoHide();
                
                // Start progress tracking
                startProgressTracking();
            }
            
            function showDolbyAnimation() {
                const dolbyOverlay = document.getElementById('dolbyOverlay');
                dolbyOverlay.classList.add('active');
                
                setTimeout(() => {
                    dolbyOverlay.classList.remove('active');
                }, 3000);
            }
            
            function resumeMovie() {
                video.currentTime = resumeTime;
                document.getElementById('resumeOverlay').classList.remove('active');
                video.play();
            }
            
            function startFromBeginning() {
                video.currentTime = 0;
                document.getElementById('resumeOverlay').classList.remove('active');
                video.play();
            }
            
            function togglePlayPause() {
                if (video.paused) {
                    video.play();
                } else {
                    video.pause();
                }
            }
            
            function handlePlay() {
                document.getElementById('playIcon').className = 'fas fa-pause';
                enableCinematicMode();
            }
            
            function handlePause() {
                document.getElementById('playIcon').className = 'fas fa-play';
            }
            
            function skipTime(seconds) {
                video.currentTime += seconds;
                showGestureIndicator(seconds > 0 ? 'right' : 'left');
            }
            
            function showGestureIndicator(direction) {
                const indicator = document.querySelector('.gesture-indicator.' + direction);
                indicator.classList.add('show');
                setTimeout(() => indicator.classList.remove('show'), 1000);
            }
            
            function seekVideo(event) {
                const progressBar = event.currentTarget;
                const clickX = event.offsetX;
                const width = progressBar.offsetWidth;
                const duration = video.duration;
                
                video.currentTime = (clickX / width) * duration;
            }
            
            function updateProgress() {
                const currentTime = video.currentTime;
                const duration = video.duration;
                const percentage = (currentTime / duration) * 100;
                
                document.querySelector('.progress-fill').style.width = percentage + '%';
                document.getElementById('currentTime').textContent = formatTime(currentTime);
            }
            
            function updateBuffer() {
                if (video.buffered.length > 0) {
                    const bufferedEnd = video.buffered.end(video.buffered.length - 1);
                    const duration = video.duration;
                    const bufferedPercentage = (bufferedEnd / duration) * 100;
                    
                    document.querySelector('.progress-buffer').style.width = bufferedPercentage + '%';
                }
            }
            
            function updateTotalTime() {
                document.getElementById('totalTime').textContent = formatTime(video.duration);
            }
            
            function formatTime(seconds) {
                const minutes = Math.floor(seconds / 60);
                const secs = Math.floor(seconds % 60);
                return minutes + ':' + (secs < 10 ? '0' : '') + secs;
            }
            
            function toggleMute() {
                video.muted = !video.muted;
                const icon = document.getElementById('volumeIcon');
                icon.className = video.muted ? 'fas fa-volume-mute' : 'fas fa-volume-up';
            }
            
            function toggleFullscreen() {
                if (!document.fullscreenElement) {
                    document.documentElement.requestFullscreen();
                    document.getElementById('fullscreenIcon').className = 'fas fa-compress';
                } else {
                    document.exitFullscreen();
                    document.getElementById('fullscreenIcon').className = 'fas fa-expand';
                }
            }
            
            function toggleCinematicMode() {
                isCinematicMode = !isCinematicMode;
                const bars = document.querySelectorAll('.cinematic-bars');
                const vignette = document.querySelector('.theater-vignette');
                
                bars.forEach(bar => bar.classList.toggle('active', isCinematicMode));
                vignette.classList.toggle('active', isCinematicMode);
            }
            
            function enableCinematicMode() {
                if (!isCinematicMode) {
                    toggleCinematicMode();
                }
            }
            
            function setupTouchControls() {
                let touchStartX = 0;
                let touchStartY = 0;
                
                video.addEventListener('touchstart', function(e) {
                    touchStartX = e.touches[0].clientX;
                    touchStartY = e.touches[0].clientY;
                    showControls();
                });
                
                video.addEventListener('touchmove', function(e) {
                    e.preventDefault();
                });
                
                video.addEventListener('touchend', function(e) {
                    const touchEndX = e.changedTouches[0].clientX;
                    const touchEndY = e.changedTouches[0].clientY;
                    const deltaX = touchEndX - touchStartX;
                    const deltaY = touchEndY - touchStartY;
                    
                    // Swipe gestures
                    if (Math.abs(deltaX) > Math.abs(deltaY) && Math.abs(deltaX) > 50) {
                        if (deltaX > 0) {
                            skipTime(10); // Swipe right - forward
                        } else {
                            skipTime(-10); // Swipe left - backward
                        }
                    } else if (Math.abs(deltaY) > 50) {
                        if (deltaY < 0) {
                            // Swipe up - show controls
                            showControls();
                        } else {
                            // Swipe down - hide controls
                            hideControls();
                        }
                    } else {
                        // Tap - toggle play/pause
                        togglePlayPause();
                    }
                });
            }
            
            function setupKeyboardControls() {
                document.addEventListener('keydown', function(e) {
                    switch(e.key) {
                        case ' ':
                            e.preventDefault();
                            togglePlayPause();
                            break;
                        case 'ArrowLeft':
                            skipTime(-10);
                            break;
                        case 'ArrowRight':
                            skipTime(10);
                            break;
                        case 'ArrowUp':
                            video.volume = Math.min(1, video.volume + 0.1);
                            break;
                        case 'ArrowDown':
                            video.volume = Math.max(0, video.volume - 0.1);
                            break;
                        case 'f':
                        case 'F':
                            toggleFullscreen();
                            break;
                        case 'm':
                        case 'M':
                            toggleMute();
                            break;
                        case 'c':
                        case 'C':
                            toggleCinematicMode();
                            break;
                    }
                    showControls();
                });
            }
            
            function setupControlsAutoHide() {
                const playerContainer = document.querySelector('.player-container');
                
                playerContainer.addEventListener('mousemove', showControls);
                playerContainer.addEventListener('touchstart', showControls);
                
                showControls(); // Show initially
            }
            
            function showControls() {
                isControlsVisible = true;
                document.querySelector('.top-controls').classList.remove('hidden');
                document.querySelector('.mobile-controls').classList.remove('hidden');
                
                // Auto-hide after 3 seconds
                clearTimeout(controlsTimeout);
                controlsTimeout = setTimeout(hideControls, 3000);
            }
            
            function hideControls() {
                if (!video.paused) {
                    isControlsVisible = false;
                    document.querySelector('.top-controls').classList.add('hidden');
                    document.querySelector('.mobile-controls').classList.add('hidden');
                }
            }
            
            function startProgressTracking() {
                progressSaveInterval = setInterval(saveProgress, 10000); // Save every 10 seconds
            }
            
            function saveProgress() {
                if (!video.paused && video.currentTime > 0) {
                    const currentTime = Math.floor(video.currentTime);
                    const duration = Math.floor(video.duration);
                    const percentage = Math.floor((currentTime / duration) * 100);
                    
                    fetch('/save-progress', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            filename: filename,
                            current_time: currentTime,
                            duration: duration,
                            percentage: percentage
                        })
                    });
                }
            }
            
            function handleMovieEnd() {
                // Mark as completed
                saveProgress();
                
                // Show ending overlay
                setTimeout(() => {
                    document.getElementById('endingOverlay').classList.add('active');
                    showDolbyAnimation();
                }, 1000);
                
                // Auto-return to library after 8 seconds
                setTimeout(() => {
                    goBack();
                }, 8000);
            }
            
            function watchAgain() {
                video.currentTime = 0;
                document.getElementById('endingOverlay').classList.remove('active');
                video.play();
            }
            
            function goBack() {
                clearInterval(progressSaveInterval);
                window.location.href = '/';
            }
            
            function toggleQualityDropdown() {
                const dropdown = document.querySelector('.quality-dropdown');
                dropdown.classList.toggle('active');
            }
            
            // Quality selector handlers
            document.querySelectorAll('.quality-option').forEach(option => {
                option.addEventListener('click', function() {
                    const quality = this.dataset.quality;
                    const qualityBtn = document.querySelector('.quality-btn');
                    
                    // Update button text
                    qualityBtn.textContent = quality.toUpperCase();
                    
                    // Update active state
                    document.querySelectorAll('.quality-option').forEach(opt => opt.classList.remove('active'));
                    this.classList.add('active');
                    
                    // Hide dropdown
                    document.querySelector('.quality-dropdown').classList.remove('active');
                    
                    // Here you would implement actual quality switching
                    console.log('Quality changed to:', quality);
                });
            });
            
            // Close dropdown when clicking outside
            document.addEventListener('click', function(e) {
                if (!e.target.closest('.quality-selector')) {
                    document.querySelector('.quality-dropdown').classList.remove('active');
                }
            });
        </script>
    </body>
    </html>
    """
    
    return render_template_string(html_template, filename=filename, movie_name=movie_name, resume_time=resume_time)

@app.route('/stream/<filename>')
def stream_movie(filename):
    """Stream movie with range request support for mobile"""
    movie_path = os.path.join(MOVIES_FOLDER, filename)
    if not os.path.exists(movie_path):
        return "Movie not found", 404
    
    # Get file info
    file_size = os.path.getsize(movie_path)
    
    # Handle range requests for mobile streaming
    range_header = request.headers.get('Range', None)
    if not range_header:
        # Return full file if no range requested
        return send_file(movie_path)
    
    # Parse range header
    byte_start = 0
    byte_end = file_size - 1
    
    match = re.search(r'bytes=(\d+)-(\d*)', range_header)
    if match:
        byte_start = int(match.group(1))
        if match.group(2):
            byte_end = int(match.group(2))
    
    # Ensure valid range
    byte_start = max(0, byte_start)
    byte_end = min(file_size - 1, byte_end)
    content_length = byte_end - byte_start + 1
    
    def generate():
        with open(movie_path, 'rb') as f:
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
    
    # Get MIME type
    mimetype = mimetypes.guess_type(filename)[0] or 'video/mp4'
    
    response = Response(
        generate(),
        206,  # Partial Content
        headers={
            'Content-Type': mimetype,
            'Accept-Ranges': 'bytes',
            'Content-Length': str(content_length),
            'Content-Range': f'bytes {byte_start}-{byte_end}/{file_size}',
            'Cache-Control': 'no-cache',
        }
    )
    
    return response

@app.route('/download/<filename>')
def download_movie(filename):
    """Download movie file"""
    movie_path = os.path.join(MOVIES_FOLDER, filename)
    if not os.path.exists(movie_path):
        return "Movie not found", 404
    
    return send_file(movie_path, as_attachment=True, download_name=filename)

@app.route('/save-progress', methods=['POST'])
def save_progress_endpoint():
    """Save watch progress"""
    data = request.get_json()
    filename = data.get('filename')
    current_time = data.get('current_time', 0)
    duration = data.get('duration', 0)
    percentage = data.get('percentage', 0)
    
    if filename:
        watch_progress[filename] = {
            'current_time': current_time,
            'duration': duration,
            'percentage': percentage,
            'last_watched': time.time()
        }
        save_progress()
    
    return jsonify({'status': 'success'})

# Serve static files
@app.route('/static/<path:filename>')
def static_files(filename):
    """Serve static files"""
    return send_file(f'static/{filename}')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
