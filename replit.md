# Overview

This is a Flask-based movie streaming server that serves video files from a local directory structure. The application provides a web interface for browsing and watching movies with features like progress tracking, mobile-optimized controls, and cinematic viewing modes. It's designed to create a personal Netflix-like experience for locally stored movie collections.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Backend Architecture
- **Framework**: Flask web application with minimal dependencies
- **File Serving**: Direct file streaming with range request support for video playback
- **Data Storage**: JSON file-based persistence for watch progress tracking
- **Configuration**: Environment variable-based configuration with sensible defaults
- **Network**: Configurable host binding with local IP detection for network access

## Frontend Architecture
- **Responsive Design**: Mobile-first CSS with touch-optimized controls
- **Video Player**: Custom HTML5 video player with enhanced controls
- **Progressive Enhancement**: JavaScript-based cinema controls layer for advanced features
- **Touch Gestures**: Custom touch gesture implementation for mobile devices

## Data Management
- **File Discovery**: Recursive directory scanning for supported video formats
- **Progress Tracking**: Client-side progress reporting with server-side JSON persistence
- **Media Support**: Multiple video format support (.mp4, .avi, .mkv, .mov, .wmv, .flv, .webm, .m4v)

## Key Design Decisions
- **Stateless Architecture**: No database dependency, using filesystem and JSON for simplicity
- **Direct File Streaming**: Bypasses complex media processing for better performance
- **Mobile-First**: Touch-optimized interface with gesture controls
- **Auto-Discovery**: Automatic movie detection from configured directory
- **Cross-Platform**: Network-accessible server for multiple device support

# External Dependencies

## Core Dependencies
- **Flask**: Web framework for HTTP server and routing
- **Python Standard Library**: Built-in modules for file handling, JSON, networking, and MIME types

## Client-Side Technologies
- **HTML5 Video API**: Native video playback and controls
- **CSS3**: Responsive design and mobile optimization
- **Vanilla JavaScript**: Custom video controls and touch gesture handling

## System Requirements
- **File System**: Local directory structure for movie storage
- **Network**: Optional LAN access for multi-device streaming
- **Browser**: Modern web browser with HTML5 video support

## Configuration
- **Environment Variables**: `MOVIES_FOLDER` for video directory path, `SESSION_SECRET` for security
- **File Permissions**: Read access to video files and write access for progress tracking