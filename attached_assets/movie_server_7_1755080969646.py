from flask import Flask, render_template_string, send_file, jsonify, request, Response
import os
import mimetypes
import re
import json
import time
from urllib.parse import quote
import socket

app = Flask(__name__)

# Configuration
MOVIES_FOLDER = r"D:\!Movies!"
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
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>CineStream - Premium Movie Experience</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                background: #0a0a0a;
                color: #ffffff;
                overflow-x: hidden;
                line-height: 1.6;
            }
            
            .hero-section {
                background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f0f23 100%);
                position: relative;
                padding: 80px 0;
                overflow: hidden;
            }
            
            .hero-section::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grid" width="10" height="10" patternUnits="userSpaceOnUse"><path d="M 10 0 L 0 0 0 10" fill="none" stroke="%23ffffff" stroke-width="0.05" opacity="0.1"/></pattern></defs><rect width="100" height="100" fill="url(%23grid)"/></svg>');
                opacity: 0.3;
            }
            
            .container {
                max-width: 1400px;
                margin: 0 auto;
                padding: 0 30px;
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
                gap: 20px;
                margin-bottom: 30px;
            }
            
            .logo-icon {
                width: 80px;
                height: 80px;
                background: linear-gradient(135deg, #ff6b6b, #4ecdc4, #45b7d1);
                border-radius: 20px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 2rem;
                box-shadow: 0 20px 40px rgba(255, 107, 107, 0.3);
                animation: pulse 2s ease-in-out infinite alternate;
            }
            
            @keyframes pulse {
                0% { transform: scale(1); box-shadow: 0 20px 40px rgba(255, 107, 107, 0.3); }
                100% { transform: scale(1.05); box-shadow: 0 25px 50px rgba(255, 107, 107, 0.5); }
            }
            
            .logo h1 {
                font-size: 3.5rem;
                font-weight: 800;
                background: linear-gradient(135deg, #ffffff, #a8edea, #fed6e3);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                letter-spacing: -2px;
            }
            
            .subtitle {
                font-size: 1.3rem;
                color: rgba(255, 255, 255, 0.7);
                margin-bottom: 20px;
            }
            
            .dolby-badges {
                display: flex;
                gap: 20px;
                justify-content: center;
                flex-wrap: wrap;
            }
            
            .badge {
                padding: 8px 16px;
                background: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 25px;
                font-size: 0.9rem;
                font-weight: 600;
                backdrop-filter: blur(10px);
                display: flex;
                align-items: center;
                gap: 8px;
            }
            
            .content-section {
                background: #0a0a0a;
                padding: 60px 0;
            }
            
            .section-title {
                font-size: 2rem;
                font-weight: 700;
                margin-bottom: 30px;
                color: #ffffff;
            }
            
            .movies-grid {
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
                gap: 30px;
                margin-top: 40px;
            }
            
            .movie-card {
                background: linear-gradient(145deg, #1a1a2e 0%, #16213e 100%);
                border-radius: 20px;
                overflow: hidden;
                position: relative;
                transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
                border: 1px solid rgba(255, 255, 255, 0.1);
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
            }
            
            .movie-card:hover {
                transform: translateY(-10px) scale(1.02);
                box-shadow: 0 25px 60px rgba(255, 107, 107, 0.2);
                border-color: rgba(255, 107, 107, 0.3);
            }
            
            .movie-poster {
                height: 180px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
                position: relative;
                display: flex;
                align-items: center;
                justify-content: center;
                overflow: hidden;
            }
            
            .movie-poster::before {
                content: '🎬';
                font-size: 4rem;
                opacity: 0.3;
                position: absolute;
                animation: float 3s ease-in-out infinite;
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
                border-radius: 0 0 0 20px;
            }
            
            .movie-info {
                padding: 25px;
            }
            
            .movie-title {
                font-size: 1.3rem;
                font-weight: 700;
                margin-bottom: 12px;
                color: #ffffff;
                line-height: 1.3;
                display: -webkit-box;
                -webkit-line-clamp: 2;
                -webkit-box-orient: vertical;
                overflow: hidden;
            }
            
            .movie-details {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 20px;
                color: rgba(255, 255, 255, 0.6);
                font-size: 0.9rem;
            }
            
            .movie-size {
                display: flex;
                align-items: center;
                gap: 5px;
            }
            
            .status-badge {
                padding: 4px 12px;
                border-radius: 15px;
                font-size: 0.8rem;
                font-weight: 600;
                text-transform: uppercase;
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
                gap: 12px;
            }
            
            .btn {
                padding: 12px 20px;
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
                box-shadow: 0 8px 25px rgba(255, 107, 107, 0.3);
            }
            
            .btn-play:hover {
                transform: translateY(-2px);
                box-shadow: 0 12px 35px rgba(255, 107, 107, 0.4);
            }
            
            .btn-download {
                background: rgba(255, 255, 255, 0.1);
                color: #ffffff;
                border: 1px solid rgba(255, 255, 255, 0.2);
                backdrop-filter: blur(10px);
            }
            
            .btn-download:hover {
                background: rgba(255, 255, 255, 0.15);
                transform: translateY(-2px);
            }
            
            .no-movies {
                text-align: center;
                padding: 100px 20px;
                color: rgba(255, 255, 255, 0.6);
            }
            
            .no-movies h2 {
                margin-bottom: 20px;
                color: #ffffff;
                font-size: 2rem;
            }
            
            @media (max-width: 768px) {
                .container {
                    padding: 0 20px;
                }
                
                .logo h1 {
                    font-size: 2.5rem;
                }
                
                .movies-grid {
                    grid-template-columns: 1fr;
                    gap: 20px;
                }
                
                .movie-actions {
                    flex-direction: column;
                }
                
                .dolby-badges {
                    flex-direction: column;
                    align-items: center;
                }
            }
            
            .stats-bar {
                background: rgba(255, 255, 255, 0.05);
                padding: 20px;
                border-radius: 15px;
                margin-bottom: 40px;
                display: flex;
                justify-content: space-around;
                text-align: center;
            }
            
            .stat {
                display: flex;
                flex-direction: column;
            }
            
            .stat-number {
                font-size: 2rem;
                font-weight: 800;
                color: #ff6b6b;
            }
            
            .stat-label {
                font-size: 0.9rem;
                color: rgba(255, 255, 255, 0.6);
                text-transform: uppercase;
                letter-spacing: 1px;
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
                    <p class="subtitle">Premium Home Theater Experience</p>
                    <div class="dolby-badges">
                        <div class="badge">🔊 Dolby Audio</div>
                        <div class="badge">📱 Multi-Device</div>
                        <div class="badge">⚡ 4K Ready</div>
                        <div class="badge">🎯 Smart Resume</div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="content-section">
            <div class="container">
                {% if movies %}
                    <div class="stats-bar">
                        <div class="stat">
                            <div class="stat-number">{{ movies|length }}</div>
                            <div class="stat-label">Movies</div>
                        </div>
                        <div class="stat">
                            <div class="stat-number">{{ movies|selectattr('is_watching')|list|length }}</div>
                            <div class="stat-label">Watching</div>
                        </div>
                        <div class="stat">
                            <div class="stat-number">{{ movies|selectattr('is_watched')|list|length }}</div>
                            <div class="stat-label">Completed</div>
                        </div>
                    </div>
                    
                    {% if movies|selectattr('is_watching')|list %}
                    <h2 class="section-title">Continue Watching</h2>
                    <div class="movies-grid">
                        {% for movie in movies if movie.is_watching %}
                        <div class="movie-card">
                            <div class="movie-poster">
                                <div class="progress-bar" style="width: {{ movie.watch_percentage }}%"></div>
                            </div>
                            <div class="movie-info">
                                <h3 class="movie-title">{{ movie.name }}</h3>
                                <div class="movie-details">
                                    <div class="movie-size">💾 {{ movie.size }} GB</div>
                                    <div class="status-badge status-watching">{{ movie.watch_percentage|int }}% watched</div>
                                </div>
                                <div class="movie-actions">
                                    <a href="/player/{{ movie.filename | urlencode }}" class="btn btn-play">
                                        ▶️ Resume
                                    </a>
                                    <a href="{{ movie.download_url }}" class="btn btn-download" download>
                                        ⬇️
                                    </a>
                                </div>
                            </div>
                        </div>
                        {% endfor %}
                    </div>
                    {% endif %}
                    
                    <h2 class="section-title" style="margin-top: 60px;">All Movies</h2>
                    <div class="movies-grid">
                        {% for movie in movies %}
                        <div class="movie-card">
                            <div class="movie-poster">
                                {% if movie.watch_percentage > 0 %}
                                <div class="progress-bar" style="width: {{ movie.watch_percentage }}%"></div>
                                {% endif %}
                            </div>
                            <div class="movie-info">
                                <h3 class="movie-title">{{ movie.name }}</h3>
                                <div class="movie-details">
                                    <div class="movie-size">💾 {{ movie.size }} GB</div>
                                    {% if movie.is_watched %}
                                    <div class="status-badge status-watched">Completed</div>
                                    {% elif movie.is_watching %}
                                    <div class="status-badge status-watching">{{ movie.watch_percentage|int }}%</div>
                                    {% endif %}
                                </div>
                                <div class="movie-actions">
                                    <a href="/player/{{ movie.filename | urlencode }}" class="btn btn-play">
                                        {% if movie.watch_percentage > 5 %}▶️ Resume{% else %}▶️ Play{% endif %}
                                    </a>
                                    <a href="{{ movie.download_url }}" class="btn btn-download" download>
                                        ⬇️
                                    </a>
                                </div>
                            </div>
                        </div>
                        {% endfor %}
                    </div>
                {% else %}
                    <div class="no-movies">
                        <h2>No movies found</h2>
                        <p>No supported movie files found in D:\!Movies!</p>
                    </div>
                {% endif %}
            </div>
        </div>
    </body>
    </html>
    """
    
    return render_template_string(html_template, movies=movies)

@app.route('/player/<filename>')
def player(filename):
    """Advanced movie player with resume functionality"""
    if not any(filename.lower().endswith(ext) for ext in ALLOWED_EXTENSIONS):
        return "Invalid file type", 400
    
    movie_path = os.path.join(MOVIES_FOLDER, filename)
    if not os.path.exists(movie_path):
        return "Movie not found", 404
    
    movie_name = os.path.splitext(filename)[0]
    stream_url = f"/stream/{quote(filename)}"
    download_url = f"/download/{quote(filename)}"
    
    # Get resume time
    progress = watch_progress.get(filename, {})
    resume_time = progress.get('time', 0)
    
    player_template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{{ movie_name }} - CineStream Player</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                background: #000;
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                overflow: hidden;
                position: relative;
            }
            
            .player-container {
                position: relative;
                width: 100vw;
                height: 100vh;
                display: flex;
                flex-direction: column;
            }
            
            .top-bar {
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                background: linear-gradient(180deg, rgba(0,0,0,0.8) 0%, transparent 100%);
                padding: 20px 30px;
                z-index: 1000;
                display: flex;
                justify-content: space-between;
                align-items: center;
                opacity: 0;
                transform: translateY(-100%);
                transition: all 0.3s ease;
            }
            
            .player-container:hover .top-bar,
            .player-container.controls-visible .top-bar {
                opacity: 1;
                transform: translateY(0);
            }
            
            .movie-info {
                color: white;
            }
            
            .movie-title {
                font-size: 1.8rem;
                font-weight: 700;
                margin-bottom: 5px;
                background: linear-gradient(135deg, #ffffff, #a8edea);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }
            
            .movie-meta {
                display: flex;
                gap: 20px;
                color: rgba(255, 255, 255, 0.7);
                font-size: 0.9rem;
            }
            
            .quality-badge {
                background: linear-gradient(135deg, #ff6b6b, #ee5a24);
                padding: 4px 12px;
                border-radius: 15px;
                font-size: 0.8rem;
                font-weight: 600;
                color: white;
            }
            
            .player-controls {
                display: flex;
                gap: 15px;
                align-items: center;
            }
            
            .control-btn {
                background: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
                color: white;
                padding: 12px 20px;
                border-radius: 12px;
                text-decoration: none;
                font-weight: 600;
                font-size: 0.9rem;
                transition: all 0.3s ease;
                backdrop-filter: blur(10px);
                display: flex;
                align-items: center;
                gap: 8px;
                cursor: pointer;
            }
            
            .control-btn:hover {
                background: rgba(255, 255, 255, 0.2);
                transform: translateY(-2px);
            }
            
            .btn-primary {
                background: linear-gradient(135deg, #667eea, #764ba2);
                border-color: transparent;
            }
            
            .video-wrapper {
                flex: 1;
                position: relative;
                display: flex;
                justify-content: center;
                align-items: center;
                background: #000;
            }
            
            video {
                width: 100%;
                height: 100%;
                object-fit: contain;
                outline: none;
            }
            
            .video-overlay {
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: rgba(0, 0, 0, 0.3);
                display: flex;
                justify-content: center;
                align-items: center;
                opacity: 0;
                transition: all 0.3s ease;
                pointer-events: none;
            }
            
            .play-button {
                width: 120px;
                height: 120px;
                background: rgba(255, 255, 255, 0.9);
                border-radius: 50%;
                display: flex;
                justify-content: center;
                align-items: center;
                font-size: 3rem;
                color: #333;
                cursor: pointer;
                pointer-events: auto;
                transition: all 0.3s ease;
                box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
            }
            
            .play-button:hover {
                transform: scale(1.1);
                background: rgba(255, 255, 255, 1);
            }
            
            video:not([autoplay]) + .video-overlay {
                opacity: 1;
            }
            
            .bottom-bar {
                position: absolute;
                bottom: 0;
                left: 0;
                right: 0;
                background: linear-gradient(0deg, rgba(0,0,0,0.9) 0%, transparent 100%);
                padding: 30px;
                z-index: 1000;
                opacity: 0;
                transform: translateY(100%);
                transition: all 0.3s ease;
            }
            
            .player-container:hover .bottom-bar,
            .player-container.controls-visible .bottom-bar {
                opacity: 1;
                transform: translateY(0);
            }
            
            .progress-section {
                margin-bottom: 20px;
            }
            
            .time-info {
                display: flex;
                justify-content: space-between;
                color: rgba(255, 255, 255, 0.8);
                font-size: 0.9rem;
                margin-bottom: 8px;
            }
            
            .video-controls {
                display: flex;
                justify-content: center;
                align-items: center;
                gap: 25px;
                color: white;
            }
            
            .control-icon {
                cursor: pointer;
                padding: 10px;
                border-radius: 50%;
                background: rgba(255, 255, 255, 0.1);
                transition: all 0.3s ease;
                display: flex;
                align-items: center;
                justify-content: center;
                width: 50px;
                height: 50px;
            }
            
            .control-icon:hover {
                background: rgba(255, 255, 255, 0.2);
                transform: scale(1.1);
            }
            
            .play-pause-btn {
                width: 60px;
                height: 60px;
                background: linear-gradient(135deg, #ff6b6b, #ee5a24);
                font-size: 1.5rem;
            }
            
            .loading-screen {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: #000;
                display: flex;
                justify-content: center;
                align-items: center;
                z-index: 2000;
                flex-direction: column;
                gap: 30px;
            }
            
            .loading-spinner {
                width: 60px;
                height: 60px;
                border: 3px solid rgba(255, 255, 255, 0.1);
                border-top: 3px solid #ff6b6b;
                border-radius: 50%;
                animation: spin 1s linear infinite;
            }
            
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            
            .loading-text {
                color: white;
                font-size: 1.2rem;
                font-weight: 600;
            }
            
            .resume-notification {
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                background: rgba(0, 0, 0, 0.9);
                color: white;
                padding: 25px 35px;
                border-radius: 15px;
                z-index: 1500;
                text-align: center;
                backdrop-filter: blur(20px);
                border: 1px solid rgba(255, 255, 255, 0.1);
                display: none;
            }
            
            .resume-notification.show {
                display: block;
                animation: slideIn 0.3s ease;
            }
            
            @keyframes slideIn {
                from { opacity: 0; transform: translate(-50%, -60%); }
                to { opacity: 1; transform: translate(-50%, -50%); }
            }
            
            .resume-buttons {
                display: flex;
                gap: 15px;
                margin-top: 20px;
                justify-content: center;
            }
            
            .resume-btn {
                padding: 10px 20px;
                border: none;
                border-radius: 8px;
                cursor: pointer;
                font-weight: 600;
                transition: all 0.3s ease;
            }
            
            .resume-btn.primary {
                background: linear-gradient(135deg, #ff6b6b, #ee5a24);
                color: white;
            }
            
            .resume-btn.secondary {
                background: rgba(255, 255, 255, 0.1);
                color: white;
                border: 1px solid rgba(255, 255, 255, 0.2);
            }
            
            @media (max-width: 768px) {
                .top-bar {
                    padding: 15px 20px;
                }
                
                .movie-title {
                    font-size: 1.3rem;
                }
                
                .movie-meta {
                    flex-direction: column;
                    gap: 5px;
                }
                
                .player-controls {
                    flex-wrap: wrap;
                    justify-content: center;
                }
                
                .video-controls {
                    gap: 15px;
                }
                
                .control-icon {
                    width: 45px;
                    height: 45px;
                }
                
                .play-pause-btn {
                    width: 55px;
                    height: 55px;
                }
                
                .resume-notification {
                    margin: 0 20px;
                    padding: 20px 25px;
                }
                
                .resume-buttons {
                    flex-direction: column;
                }
            }
        </style>
    </head>
    <body>
        <div class="loading-screen" id="loadingScreen">
            <div class="loading-spinner"></div>
            <div class="loading-text">Loading your cinema experience...</div>
        </div>
        
        <div class="player-container" id="playerContainer">
            <div class="top-bar">
                <div class="movie-info">
                    <h1 class="movie-title">{{ movie_name }}</h1>
                    <div class="movie-meta">
                        <span>🎬 Premium Quality</span>
                        <span>🔊 Surround Sound</span>
                        <div class="quality-badge">HD</div>
                    </div>
                </div>
                <div class="player-controls">
                    <a href="/" class="control-btn btn-primary">← Library</a>
                    <a href="{{ download_url }}" class="control-btn" download>⬇️ Download</a>
                    <button class="control-btn" onclick="toggleFullscreen()">⛶ Fullscreen</button>
                </div>
            </div>
            
            <div class="video-wrapper">
                <video id="movieVideo" preload="metadata" crossorigin="anonymous">
                    <source src="{{ stream_url }}" type="video/mp4">
                    Your browser does not support the video tag.
                </video>
                
                <div class="video-overlay">
                    <div class="play-button" onclick="playVideo()">▶️</div>
                </div>
            </div>
            
            <div class="bottom-bar">
                <div class="progress-section">
                    <div class="time-info">
                        <span id="currentTime">0:00</span>
                        <span id="duration">0:00</span>
                    </div>
                </div>
                
                <div class="video-controls">
                    <div class="control-icon" onclick="skipTime(-10)">⏪</div>
                    <div class="control-icon play-pause-btn" onclick="togglePlay()" id="playPauseBtn">▶️</div>
                    <div class="control-icon" onclick="skipTime(10)">⏩</div>
                    <div class="control-icon" onclick="toggleMute()" id="muteBtn">🔊</div>
                    <div class="control-icon" onclick="toggleFullscreen()">⛶</div>
                </div>
            </div>
        </div>
        
        <div class="resume-notification" id="resumeNotification">
            <h3>Resume Playback?</h3>
            <p>You were watching this movie at <span id="resumeTime"></span></p>
            <div class="resume-buttons">
                <button class="resume-btn primary" onclick="resumePlayback()">Resume</button>
                <button class="resume-btn secondary" onclick="startFromBeginning()">Start Over</button>
            </div>
        </div>
        
        <script>
            const video = document.getElementById('movieVideo');
            const playPauseBtn = document.getElementById('playPauseBtn');
            const muteBtn = document.getElementById('muteBtn');
            const currentTimeSpan = document.getElementById('currentTime');
            const durationSpan = document.getElementById('duration');
            const playerContainer = document.getElementById('playerContainer');
            const loadingScreen = document.getElementById('loadingScreen');
            const resumeNotification = document.getElementById('resumeNotification');
            const resumeTimeSpan = document.getElementById('resumeTime');
            
            let resumeTime = {{ resume_time }};
            let controlsTimeout;
            let isFullscreen = false;
            
            // Format time helper
            function formatTime(seconds) {
                const hrs = Math.floor(seconds / 3600);
                const mins = Math.floor((seconds % 3600) / 60);
                const secs = Math.floor(seconds % 60);
                
                if (hrs > 0) {
                    return `${hrs}:${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
                }
                return `${mins}:${secs.toString().padStart(2, '0')}`;
            }
            
            // Show resume notification
            function showResumeNotification() {
                if (resumeTime > 30) {
                    resumeTimeSpan.textContent = formatTime(resumeTime);
                    resumeNotification.classList.add('show');
                } else {
                    video.play();
                }
            }
            
            // Resume playback
            function resumePlayback() {
                video.currentTime = resumeTime;
                video.play();
                resumeNotification.classList.remove('show');
            }
            
            // Start from beginning
            function startFromBeginning() {
                video.currentTime = 0;
                video.play();
                resumeNotification.classList.remove('show');
            }
            
            // Play video
            function playVideo() {
                if (resumeTime > 30) {
                    showResumeNotification();
                } else {
                    video.play();
                }
            }
            
            // Toggle play/pause
            function togglePlay() {
                if (video.paused) {
                    video.play();
                } else {
                    video.pause();
                }
            }
            
            // Skip time
            function skipTime(seconds) {
                video.currentTime += seconds;
                saveProgress();
            }
            
            // Toggle mute
            function toggleMute() {
                video.muted = !video.muted;
                muteBtn.textContent = video.muted ? '🔇' : '🔊';
            }
            
            // Toggle fullscreen
            function toggleFullscreen() {
                if (!isFullscreen) {
                    if (playerContainer.requestFullscreen) {
                        playerContainer.requestFullscreen();
                    } else if (playerContainer.webkitRequestFullscreen) {
                        playerContainer.webkitRequestFullscreen();
                    } else if (playerContainer.mozRequestFullScreen) {
                        playerContainer.mozRequestFullScreen();
                    }
                } else {
                    if (document.exitFullscreen) {
                        document.exitFullscreen();
                    } else if (document.webkitExitFullscreen) {
                        document.webkitExitFullscreen();
                    } else if (document.mozCancelFullScreen) {
                        document.mozCancelFullScreen();
                    }
                }
            }
            
            // Save progress
            function saveProgress() {
                const currentTime = video.currentTime;
                const duration = video.duration;
                const percentage = (currentTime / duration) * 100;
                
                fetch('/save-progress', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        filename: '{{ filename }}',
                        time: currentTime,
                        duration: duration,
                        percentage: percentage
                    })
                });
            }
            
            // Show/hide controls
            function showControls() {
                playerContainer.classList.add('controls-visible');
                clearTimeout(controlsTimeout);
                controlsTimeout = setTimeout(() => {
                    if (!video.paused) {
                        playerContainer.classList.remove('controls-visible');
                    }
                }, 3000);
            }
            
            // Video event listeners
            video.addEventListener('loadstart', () => {
                loadingScreen.style.display = 'flex';
            });
            
            video.addEventListener('canplay', () => {
                loadingScreen.style.display = 'none';
                durationSpan.textContent = formatTime(video.duration);
                if (resumeTime > 30) {
                    showResumeNotification();
                }
            });
            
            video.addEventListener('play', () => {
                playPauseBtn.textContent = '⏸️';
                document.querySelector('.video-overlay').style.opacity = '0';
            });
            
            video.addEventListener('pause', () => {
                playPauseBtn.textContent = '▶️';
                showControls();
            });
            
            video.addEventListener('timeupdate', () => {
                currentTimeSpan.textContent = formatTime(video.currentTime);
                
                // Save progress every 10 seconds
                if (Math.floor(video.currentTime) % 10 === 0) {
                    saveProgress();
                }
            });
            
            video.addEventListener('ended', () => {
                // Mark as completed
                saveProgress();
                playPauseBtn.textContent = '🔄';
            });
            
            // Mouse movement
            document.addEventListener('mousemove', showControls);
            document.addEventListener('click', showControls);
            
            // Keyboard shortcuts
            document.addEventListener('keydown', (e) => {
                switch(e.key.toLowerCase()) {
                    case ' ':
                        e.preventDefault();
                        togglePlay();
                        break;
                    case 'f':
                        e.preventDefault();
                        toggleFullscreen();
                        break;
                    case 'm':
                        e.preventDefault();
                        toggleMute();
                        break;
                    case 'arrowleft':
                        e.preventDefault();
                        skipTime(-10);
                        break;
                    case 'arrowright':
                        e.preventDefault();
                        skipTime(10);
                        break;
                    case 'arrowup':
                        e.preventDefault();
                        video.volume = Math.min(1, video.volume + 0.1);
                        break;
                    case 'arrowdown':
                        e.preventDefault();
                        video.volume = Math.max(0, video.volume - 0.1);
                        break;
                    case 'escape':
                        if (resumeNotification.classList.contains('show')) {
                            resumeNotification.classList.remove('show');
                        }
                        break;
                }
                showControls();
            });
            
            // Fullscreen change
            document.addEventListener('fullscreenchange', () => {
                isFullscreen = !!document.fullscreenElement;
            });
            
            document.addEventListener('webkitfullscreenchange', () => {
                isFullscreen = !!document.webkitFullscreenElement;
            });
            
            document.addEventListener('mozfullscreenchange', () => {
                isFullscreen = !!document.mozFullScreenElement;
            });
            
            // Double click for fullscreen
            video.addEventListener('dblclick', toggleFullscreen);
            
            // Touch controls for mobile
            let touchStartX = 0;
            let touchStartY = 0;
            
            video.addEventListener('touchstart', (e) => {
                touchStartX = e.touches[0].clientX;
                touchStartY = e.touches[0].clientY;
                showControls();
            });
            
            video.addEventListener('touchmove', (e) => {
                e.preventDefault();
            });
            
            video.addEventListener('touchend', (e) => {
                const touchEndX = e.changedTouches[0].clientX;
                const touchEndY = e.changedTouches[0].clientY;
                
                const deltaX = touchEndX - touchStartX;
                const deltaY = touchEndY - touchStartY;
                
                if (Math.abs(deltaX) > Math.abs(deltaY)) {
                    if (Math.abs(deltaX) > 50) {
                        if (deltaX > 0) {
                            skipTime(10);
                        } else {
                            skipTime(-10);
                        }
                    }
                } else {
                    if (Math.abs(deltaY) < 30 && Math.abs(deltaX) < 30) {
                        togglePlay();
                    }
                }
            });
            
            // Initialize
            showControls();
        </script>
    </body>
    </html>
    """
    
    return render_template_string(player_template, 
                                movie_name=movie_name, 
                                stream_url=stream_url, 
                                download_url=download_url,
                                filename=filename,
                                resume_time=resume_time)

@app.route('/save-progress', methods=['POST'])
def save_progress_route():
    """Save movie watching progress"""
    data = request.get_json()
    filename = data.get('filename')
    time = data.get('time', 0)
    duration = data.get('duration', 0)
    percentage = data.get('percentage', 0)
    
    if filename:
        watch_progress[filename] = {
            'time': time,
            'duration': duration,
            'percentage': percentage,
            'last_watched': int(time.time()) if time else None
        }
        save_progress()
    
    return jsonify({'status': 'success'})

@app.route('/stream/<filename>')
def stream_video(filename):
    """Stream video with range support for seeking"""
    movie_path = os.path.join(MOVIES_FOLDER, filename)
    if not os.path.exists(movie_path):
        return "Movie not found", 404
    
    # Get file info
    file_size = os.path.getsize(movie_path)
    
    # Handle range requests for video seeking
    range_header = request.headers.get('Range', None)
    if not range_header:
        # No range request, send entire file
        def generate():
            with open(movie_path, 'rb') as f:
                while True:
                    chunk = f.read(8192)
                    if not chunk:
                        break
                    yield chunk
        
        # Determine MIME type
        mime_type = mimetypes.guess_type(movie_path)[0] or 'application/octet-stream'
        
        response = Response(generate(), mimetype=mime_type)
        response.headers['Accept-Ranges'] = 'bytes'
        response.headers['Content-Length'] = str(file_size)
        return response
    
    # Parse range header
    byte_start = 0
    byte_end = file_size - 1
    
    match = re.search(r'bytes=(\d+)-(\d*)', range_header)
    if match:
        byte_start = int(match.group(1))
        if match.group(2):
            byte_end = int(match.group(2))
    
    # Ensure valid range
    if byte_start >= file_size:
        return "Range not satisfiable", 416
    
    if byte_end >= file_size:
        byte_end = file_size - 1
    
    content_length = byte_end - byte_start + 1
    
    def generate_chunk():
        with open(movie_path, 'rb') as f:
            f.seek(byte_start)
            remaining = content_length
            while remaining:
                chunk_size = min(8192, remaining)
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                remaining -= len(chunk)
                yield chunk
    
    # Determine MIME type
    mime_type = mimetypes.guess_type(movie_path)[0] or 'application/octet-stream'
    
    response = Response(generate_chunk(), 
                      status=206,
                      mimetype=mime_type,
                      direct_passthrough=True)
    
    response.headers['Content-Range'] = f'bytes {byte_start}-{byte_end}/{file_size}'
    response.headers['Accept-Ranges'] = 'bytes'
    response.headers['Content-Length'] = str(content_length)
    response.headers['Cache-Control'] = 'no-cache'
    
    return response

@app.route('/download/<filename>')
def download_movie(filename):
    """Download movie file"""
    movie_path = os.path.join(MOVIES_FOLDER, filename)
    if not os.path.exists(movie_path):
        return "Movie not found", 404
    
    return send_file(movie_path, as_attachment=True, download_name=filename)

if __name__ == '__main__':
    local_ip = get_local_ip()
    port = 5000
    
    print("\n" + "="*60)
    print("🎬 CINESTREAM - PREMIUM MOVIE SERVER")
    print("="*60)
    print(f"📁 Movies folder: {os.path.abspath(MOVIES_FOLDER)}")
    print(f"🌐 Local access: http://localhost:{port}")
    print(f"📱 Network access: http://{local_ip}:{port}")
    print("="*60)
    print("🎯 Premium Features:")
    print("  • Smart Resume - Continue where you left off")
    print("  • Modern Cinema UI - Dolby-inspired design")  
    print("  • Full Keyboard Controls - Space, F, M, Arrows")
    print("  • Mobile Optimized - Touch gestures support")
    print("  • Progress Tracking - Automatic save every 10s")
    print("="*60)
    
    # Count movies in folder
    try:
        movie_count = len([f for f in os.listdir(MOVIES_FOLDER) 
                          if any(f.lower().endswith(ext) for ext in ALLOWED_EXTENSIONS)])
        print(f"🎬 {movie_count} movies ready for premium streaming")
    except:
        print("❌ Could not access movies folder")
    print("="*60)
    
    # Run the server
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)
                