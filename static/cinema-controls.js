/**
 * Cinema Controls - Enhanced Mobile Movie Player
 * Provides touch gestures, keyboard controls, and cinematic features
 */

class CinemaControls {
    constructor(videoElement) {
        this.video = videoElement;
        this.isControlsVisible = true;
        this.controlsTimeout = null;
        this.isCinematicMode = false;
        this.progressSaveInterval = null;
        this.touchStartX = 0;
        this.touchStartY = 0;
        this.gestureThreshold = 50;
        this.volumeBeforeMute = 1;
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.setupTouchGestures();
        this.setupKeyboardControls();
        this.setupProgressTracking();
        this.setupQualityControls();
    }
    
    setupEventListeners() {
        // Video events
        this.video.addEventListener('loadedmetadata', () => this.updateTotalTime());
        this.video.addEventListener('timeupdate', () => this.updateProgress());
        this.video.addEventListener('ended', () => this.handleMovieEnd());
        this.video.addEventListener('play', () => this.handlePlay());
        this.video.addEventListener('pause', () => this.handlePause());
        this.video.addEventListener('progress', () => this.updateBuffer());
        this.video.addEventListener('volumechange', () => this.updateVolumeIcon());
        
        // Fullscreen events
        document.addEventListener('fullscreenchange', () => this.updateFullscreenIcon());
        document.addEventListener('webkitfullscreenchange', () => this.updateFullscreenIcon());
        document.addEventListener('mozfullscreenchange', () => this.updateFullscreenIcon());
        document.addEventListener('MSFullscreenChange', () => this.updateFullscreenIcon());
        
        // Mouse and touch events for auto-hide
        const playerContainer = document.querySelector('.player-container');
        playerContainer.addEventListener('mousemove', () => this.showControls());
        playerContainer.addEventListener('touchstart', () => this.showControls());
        
        // Window events
        window.addEventListener('beforeunload', () => this.cleanup());
        window.addEventListener('orientationchange', () => this.handleOrientationChange());
    }
    
    setupTouchGestures() {
        let lastTap = 0;
        
        this.video.addEventListener('touchstart', (e) => {
            this.touchStartX = e.touches[0].clientX;
            this.touchStartY = e.touches[0].clientY;
            this.showControls();
            
            // Double tap detection
            const currentTime = new Date().getTime();
            const tapLength = currentTime - lastTap;
            if (tapLength < 500 && tapLength > 0) {
                this.toggleFullscreen();
                e.preventDefault();
            }
            lastTap = currentTime;
        }, { passive: false });
        
        this.video.addEventListener('touchmove', (e) => {
            e.preventDefault();
        }, { passive: false });
        
        this.video.addEventListener('touchend', (e) => {
            const touchEndX = e.changedTouches[0].clientX;
            const touchEndY = e.changedTouches[0].clientY;
            const deltaX = touchEndX - this.touchStartX;
            const deltaY = touchEndY - this.touchStartY;
            const absDeltaX = Math.abs(deltaX);
            const absDeltaY = Math.abs(deltaY);
            
            // Determine gesture type
            if (absDeltaX > this.gestureThreshold || absDeltaY > this.gestureThreshold) {
                if (absDeltaX > absDeltaY) {
                    // Horizontal swipe
                    if (deltaX > 0) {
                        this.skipTime(10); // Swipe right - forward
                    } else {
                        this.skipTime(-10); // Swipe left - backward
                    }
                } else {
                    // Vertical swipe
                    if (deltaY < 0) {
                        // Swipe up - show controls or increase volume
                        if (this.touchStartX < window.innerWidth / 2) {
                            this.adjustBrightness(0.1);
                        } else {
                            this.adjustVolume(0.1);
                        }
                    } else {
                        // Swipe down - hide controls or decrease volume
                        if (this.touchStartX < window.innerWidth / 2) {
                            this.adjustBrightness(-0.1);
                        } else {
                            this.adjustVolume(-0.1);
                        }
                    }
                }
            } else {
                // Tap - toggle play/pause
                this.togglePlayPause();
            }
        });
    }
    
    setupKeyboardControls() {
        document.addEventListener('keydown', (e) => {
            // Prevent default for media keys
            const mediaKeys = [' ', 'ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown', 'f', 'F', 'm', 'M', 'c', 'C'];
            if (mediaKeys.includes(e.key)) {
                e.preventDefault();
            }
            
            switch(e.key) {
                case ' ':
                    this.togglePlayPause();
                    break;
                case 'ArrowLeft':
                    this.skipTime(-10);
                    break;
                case 'ArrowRight':
                    this.skipTime(10);
                    break;
                case 'ArrowUp':
                    this.adjustVolume(0.1);
                    break;
                case 'ArrowDown':
                    this.adjustVolume(-0.1);
                    break;
                case 'f':
                case 'F':
                    this.toggleFullscreen();
                    break;
                case 'm':
                case 'M':
                    this.toggleMute();
                    break;
                case 'c':
                case 'C':
                    this.toggleCinematicMode();
                    break;
                case 'Escape':
                    if (document.fullscreenElement) {
                        this.exitFullscreen();
                    }
                    break;
            }
            this.showControls();
        });
    }
    
    setupProgressTracking() {
        this.progressSaveInterval = setInterval(() => {
            this.saveProgress();
        }, 10000); // Save every 10 seconds
    }
    
    setupQualityControls() {
        const qualityOptions = document.querySelectorAll('.quality-option');
        qualityOptions.forEach(option => {
            option.addEventListener('click', (e) => {
                this.changeQuality(e.target.dataset.quality);
            });
        });
        
        // Close dropdown when clicking outside
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.quality-selector')) {
                this.closeQualityDropdown();
            }
        });
    }
    
    togglePlayPause() {
        if (this.video.paused) {
            this.video.play();
        } else {
            this.video.pause();
        }
    }
    
    handlePlay() {
        const playIcon = document.getElementById('playIcon');
        if (playIcon) {
            playIcon.className = 'fas fa-pause';
        }
        
        // Enable cinematic mode when playing
        if (!this.isCinematicMode) {
            this.enableCinematicMode();
        }
    }
    
    handlePause() {
        const playIcon = document.getElementById('playIcon');
        if (playIcon) {
            playIcon.className = 'fas fa-play';
        }
    }
    
    skipTime(seconds) {
        this.video.currentTime = Math.max(0, Math.min(this.video.duration, this.video.currentTime + seconds));
        this.showGestureIndicator(seconds > 0 ? 'right' : 'left');
    }
    
    showGestureIndicator(direction) {
        const indicator = document.querySelector(`.gesture-indicator.${direction}`);
        if (indicator) {
            indicator.classList.add('show');
            setTimeout(() => indicator.classList.remove('show'), 1000);
        }
    }
    
    adjustVolume(delta) {
        const newVolume = Math.max(0, Math.min(1, this.video.volume + delta));
        this.video.volume = newVolume;
        
        // Show volume feedback
        this.showVolumeIndicator(Math.round(newVolume * 100));
    }
    
    adjustBrightness(delta) {
        // Simulate brightness control with video filter
        const currentFilter = this.video.style.filter || '';
        const brightnessMatch = currentFilter.match(/brightness\(([^)]+)\)/);
        let currentBrightness = brightnessMatch ? parseFloat(brightnessMatch[1]) : 1;
        
        currentBrightness = Math.max(0.1, Math.min(2, currentBrightness + delta));
        
        this.video.style.filter = currentFilter.replace(/brightness\([^)]+\)/, '') + ` brightness(${currentBrightness})`;
        
        // Show brightness feedback
        this.showBrightnessIndicator(Math.round(currentBrightness * 100));
    }
    
    showVolumeIndicator(volume) {
        // Create or update volume indicator
        let indicator = document.getElementById('volumeIndicator');
        if (!indicator) {
            indicator = document.createElement('div');
            indicator.id = 'volumeIndicator';
            indicator.style.cssText = `
                position: absolute;
                top: 50%;
                right: 30px;
                transform: translateY(-50%);
                background: rgba(0,0,0,0.8);
                padding: 15px;
                border-radius: 10px;
                color: white;
                font-weight: 600;
                z-index: 25;
                transition: opacity 0.3s ease;
                backdrop-filter: blur(10px);
            `;
            document.querySelector('.player-container').appendChild(indicator);
        }
        
        indicator.innerHTML = `<i class="fas fa-volume-up"></i> ${volume}%`;
        indicator.style.opacity = '1';
        
        clearTimeout(indicator.hideTimeout);
        indicator.hideTimeout = setTimeout(() => {
            indicator.style.opacity = '0';
        }, 1500);
    }
    
    showBrightnessIndicator(brightness) {
        // Create or update brightness indicator
        let indicator = document.getElementById('brightnessIndicator');
        if (!indicator) {
            indicator = document.createElement('div');
            indicator.id = 'brightnessIndicator';
            indicator.style.cssText = `
                position: absolute;
                top: 50%;
                left: 30px;
                transform: translateY(-50%);
                background: rgba(0,0,0,0.8);
                padding: 15px;
                border-radius: 10px;
                color: white;
                font-weight: 600;
                z-index: 25;
                transition: opacity 0.3s ease;
                backdrop-filter: blur(10px);
            `;
            document.querySelector('.player-container').appendChild(indicator);
        }
        
        indicator.innerHTML = `<i class="fas fa-sun"></i> ${brightness}%`;
        indicator.style.opacity = '1';
        
        clearTimeout(indicator.hideTimeout);
        indicator.hideTimeout = setTimeout(() => {
            indicator.style.opacity = '0';
        }, 1500);
    }
    
    seekVideo(event) {
        const progressBar = event.currentTarget;
        const rect = progressBar.getBoundingClientRect();
        const clickX = event.clientX - rect.left;
        const width = rect.width;
        const duration = this.video.duration;
        
        this.video.currentTime = (clickX / width) * duration;
    }
    
    updateProgress() {
        const currentTime = this.video.currentTime;
        const duration = this.video.duration;
        
        if (duration > 0) {
            const percentage = (currentTime / duration) * 100;
            const progressFill = document.querySelector('.progress-fill');
            if (progressFill) {
                progressFill.style.width = percentage + '%';
            }
        }
        
        const currentTimeEl = document.getElementById('currentTime');
        if (currentTimeEl) {
            currentTimeEl.textContent = this.formatTime(currentTime);
        }
    }
    
    updateBuffer() {
        if (this.video.buffered.length > 0) {
            const bufferedEnd = this.video.buffered.end(this.video.buffered.length - 1);
            const duration = this.video.duration;
            
            if (duration > 0) {
                const bufferedPercentage = (bufferedEnd / duration) * 100;
                const progressBuffer = document.querySelector('.progress-buffer');
                if (progressBuffer) {
                    progressBuffer.style.width = bufferedPercentage + '%';
                }
            }
        }
    }
    
    updateTotalTime() {
        const totalTimeEl = document.getElementById('totalTime');
        if (totalTimeEl) {
            totalTimeEl.textContent = this.formatTime(this.video.duration);
        }
    }
    
    formatTime(seconds) {
        if (isNaN(seconds)) return '0:00';
        
        const hours = Math.floor(seconds / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        const secs = Math.floor(seconds % 60);
        
        if (hours > 0) {
            return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
        } else {
            return `${minutes}:${secs.toString().padStart(2, '0')}`;
        }
    }
    
    toggleMute() {
        if (this.video.muted) {
            this.video.muted = false;
            this.video.volume = this.volumeBeforeMute;
        } else {
            this.volumeBeforeMute = this.video.volume;
            this.video.muted = true;
        }
    }
    
    updateVolumeIcon() {
        const volumeIcon = document.getElementById('volumeIcon');
        if (volumeIcon) {
            if (this.video.muted || this.video.volume === 0) {
                volumeIcon.className = 'fas fa-volume-mute';
            } else if (this.video.volume < 0.5) {
                volumeIcon.className = 'fas fa-volume-down';
            } else {
                volumeIcon.className = 'fas fa-volume-up';
            }
        }
    }
    
    toggleFullscreen() {
        if (!document.fullscreenElement && !document.webkitFullscreenElement && 
            !document.mozFullScreenElement && !document.msFullscreenElement) {
            this.enterFullscreen();
        } else {
            this.exitFullscreen();
        }
    }
    
    enterFullscreen() {
        const element = document.documentElement;
        
        if (element.requestFullscreen) {
            element.requestFullscreen();
        } else if (element.webkitRequestFullscreen) {
            element.webkitRequestFullscreen();
        } else if (element.mozRequestFullScreen) {
            element.mozRequestFullScreen();
        } else if (element.msRequestFullscreen) {
            element.msRequestFullscreen();
        }
    }
    
    exitFullscreen() {
        if (document.exitFullscreen) {
            document.exitFullscreen();
        } else if (document.webkitExitFullscreen) {
            document.webkitExitFullscreen();
        } else if (document.mozCancelFullScreen) {
            document.mozCancelFullScreen();
        } else if (document.msExitFullscreen) {
            document.msExitFullscreen();
        }
    }
    
    updateFullscreenIcon() {
        const fullscreenIcon = document.getElementById('fullscreenIcon');
        if (fullscreenIcon) {
            const isFullscreen = document.fullscreenElement || document.webkitFullscreenElement || 
                               document.mozFullScreenElement || document.msFullscreenElement;
            fullscreenIcon.className = isFullscreen ? 'fas fa-compress' : 'fas fa-expand';
        }
    }
    
    toggleCinematicMode() {
        this.isCinematicMode = !this.isCinematicMode;
        const bars = document.querySelectorAll('.cinematic-bars');
        const vignette = document.querySelector('.theater-vignette');
        
        bars.forEach(bar => bar.classList.toggle('active', this.isCinematicMode));
        if (vignette) {
            vignette.classList.toggle('active', this.isCinematicMode);
        }
    }
    
    enableCinematicMode() {
        if (!this.isCinematicMode) {
            this.toggleCinematicMode();
        }
    }
    
    showControls() {
        this.isControlsVisible = true;
        const topControls = document.querySelector('.top-controls');
        const mobileControls = document.querySelector('.mobile-controls');
        
        if (topControls) topControls.classList.remove('hidden');
        if (mobileControls) mobileControls.classList.remove('hidden');
        
        // Auto-hide after 3 seconds
        clearTimeout(this.controlsTimeout);
        this.controlsTimeout = setTimeout(() => this.hideControls(), 3000);
    }
    
    hideControls() {
        if (!this.video.paused) {
            this.isControlsVisible = false;
            const topControls = document.querySelector('.top-controls');
            const mobileControls = document.querySelector('.mobile-controls');
            
            if (topControls) topControls.classList.add('hidden');
            if (mobileControls) mobileControls.classList.add('hidden');
        }
    }
    
    saveProgress() {
        if (!this.video.paused && this.video.currentTime > 0 && this.video.duration > 0) {
            const currentTime = Math.floor(this.video.currentTime);
            const duration = Math.floor(this.video.duration);
            const percentage = Math.floor((currentTime / duration) * 100);
            
            // Get filename from global variable or URL
            const filename = window.filename || window.location.pathname.split('/').pop();
            
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
            }).catch(error => {
                console.log('Progress save failed:', error);
            });
        }
    }
    
    handleMovieEnd() {
        // Save final progress
        this.saveProgress();
        
        // Show ending overlay
        setTimeout(() => {
            const endingOverlay = document.getElementById('endingOverlay');
            if (endingOverlay) {
                endingOverlay.classList.add('active');
            }
            this.showDolbyAnimation();
        }, 1000);
        
        // Auto-return to library after 8 seconds
        setTimeout(() => {
            this.goBack();
        }, 8000);
    }
    
    showDolbyAnimation() {
        const dolbyOverlay = document.getElementById('dolbyOverlay');
        if (dolbyOverlay) {
            dolbyOverlay.classList.add('active');
            
            setTimeout(() => {
                dolbyOverlay.classList.remove('active');
            }, 3000);
        }
    }
    
    changeQuality(quality) {
        const qualityBtn = document.querySelector('.quality-btn');
        if (qualityBtn) {
            qualityBtn.textContent = quality.toUpperCase();
        }
        
        // Update active state
        document.querySelectorAll('.quality-option').forEach(opt => opt.classList.remove('active'));
        document.querySelector(`[data-quality="${quality}"]`).classList.add('active');
        
        this.closeQualityDropdown();
        
        // Here you would implement actual quality switching
        console.log('Quality changed to:', quality);
    }
    
    closeQualityDropdown() {
        const dropdown = document.querySelector('.quality-dropdown');
        if (dropdown) {
            dropdown.classList.remove('active');
        }
    }
    
    handleOrientationChange() {
        // Handle orientation changes for mobile
        setTimeout(() => {
            this.showControls();
        }, 500);
    }
    
    goBack() {
        this.cleanup();
        window.location.href = '/';
    }
    
    cleanup() {
        if (this.progressSaveInterval) {
            clearInterval(this.progressSaveInterval);
        }
        if (this.controlsTimeout) {
            clearTimeout(this.controlsTimeout);
        }
    }
}

// Auto-initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    const video = document.getElementById('movieVideo');
    if (video) {
        window.cinemaControls = new CinemaControls(video);
    }
});
