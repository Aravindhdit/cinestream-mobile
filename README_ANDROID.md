# CineStream Mobile - Android APK

Convert your Flask movie streaming server into a native Android application!

## 🎯 What This Creates

Your CineStream Flask app becomes a **native Android APK** with:

- ✅ **Native Android App**: Install directly on your phone
- ✅ **Embedded Web Server**: Flask server runs inside the app
- ✅ **All Features Preserved**: Dolby animations, progress tracking, streaming
- ✅ **Mobile Optimized**: Touch controls and responsive design
- ✅ **Offline Capable**: Movies stored locally on your device
- ✅ **No Internet Required**: Works completely offline

## 🚀 Quick Start (Linux Required)

### Method 1: Automated Build (Recommended)

```bash
# Run the automated builder
python3 build_apk.py
```

This script will:
1. Install all required dependencies
2. Set up Android build environment  
3. Build your APK automatically
4. Provide installation instructions

### Method 2: Manual Build

```bash
# Install system dependencies (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install -y git zip unzip openjdk-17-jdk python3-pip \
    autoconf libtool pkg-config zlib1g-dev libncurses5-dev \
    libncursesw5-dev libtinfo5 cmake libffi-dev libssl-dev \
    build-essential libltdl-dev ccache

# Install Python dependencies
pip3 install --user buildozer cython kivy

# Initialize and build
buildozer init
buildozer android debug
```

## 📱 Installation on Android

1. **Transfer APK**: Copy `CineStream-Mobile.apk` to your Android device
2. **Enable Unknown Sources**: Go to Settings > Security > Install from Unknown Sources
3. **Install**: Tap the APK file and follow installation prompts
4. **Grant Permissions**: Allow storage access when prompted

## 📁 Setting Up Movies

1. **Create Movies Folder**: 
   - Open file manager on Android
   - Create folder: `/storage/emulated/0/Movies/`
   - Or use: `Internal Storage/Movies/`

2. **Add Movies**: 
   - Copy your video files to the Movies folder
   - Supported formats: MP4, MKV, AVI, MOV, WMV, 3GP

3. **Launch App**: 
   - Open CineStream Mobile
   - Movies will appear automatically

## 🏗️ Build Requirements

### System Requirements
- **Linux OS** (Ubuntu 20.04+ recommended)
- **Python 3.8+**
- **4GB+ RAM** (8GB recommended)
- **20GB+ free disk space**
- **Stable internet** (for downloading Android SDK)

### Alternative Options
- **WSL2 on Windows**: Use Windows Subsystem for Linux
- **Docker**: Use Android build container
- **GitHub Actions**: Automated cloud building
- **Linux VM**: Virtual machine on Windows/Mac

## 🎮 App Features

### Core Functionality
- **Native Android App**: Runs as standard Android application
- **Embedded Flask Server**: Web server runs inside app
- **Local File Access**: Direct access to device storage
- **Background Processing**: Continues running when minimized

### Cinema Features (Preserved)
- **Dolby Vision & Atmos**: Premium visual/audio experience
- **Progress Tracking**: Resume where you left off
- **Touch Controls**: Mobile-optimized gestures
- **Quality Settings**: Adaptive streaming
- **Download Support**: Offline movie access

### Mobile Optimizations
- **Battery Efficient**: Optimized for mobile devices
- **Touch Friendly**: Large buttons and gesture support
- **Responsive Design**: Works on all screen sizes
- **Orientation Support**: Portrait and landscape modes

## 🔧 Advanced Configuration

### Custom Movies Folder
Edit `android_app.py` to change the default movies folder:

```python
def get_movies_folder(self):
    # Custom folder path
    return '/storage/emulated/0/MyMovies/'
```

### App Permissions
Modify `buildozer.spec` to add more permissions:

```ini
android.permissions = INTERNET,ACCESS_NETWORK_STATE,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,WAKE_LOCK,CAMERA
```

### App Icon and Branding
- Add `icon.png` (512x512) for app icon
- Add `presplash.png` for splash screen
- Modify app name in `buildozer.spec`

## 🐛 Troubleshooting

### Build Issues

**"Command not found: buildozer"**
```bash
# Add to PATH
echo 'export PATH=$PATH:~/.local/bin' >> ~/.bashrc
source ~/.bashrc
```

**"Java SDK not found"**
```bash
# Set JAVA_HOME
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
```

**"Android SDK download fails"**
```bash
# Manual SDK setup
buildozer android clean
buildozer android debug
```

### App Runtime Issues

**"No movies found"**
- Check Movies folder exists: `/storage/emulated/0/Movies/`
- Verify file permissions (grant storage access)
- Supported formats: MP4, MKV, AVI, MOV, WMV, 3GP

**"App crashes on startup"**
- Check Android version (requires Android 5.0+)
- Clear app data and restart
- Check logcat: `adb logcat | grep python`

**"Videos won't play"**
- Use H.264/H.265 encoded videos
- Keep file sizes reasonable (<4GB)
- Ensure videos aren't corrupted

## 📊 Build Process Details

### First Build (60+ minutes)
1. **Download Android SDK**: ~2GB
2. **Download NDK**: ~1GB  
3. **Compile Python**: ~20 minutes
4. **Compile Kivy**: ~15 minutes
5. **Package APK**: ~5 minutes

### Subsequent Builds (5-10 minutes)
- Only recompiles changed code
- Uses cached dependencies
- Much faster iteration

### APK Size
- **Base APK**: ~40-60MB
- **With Dependencies**: ~50-80MB
- **Final Size**: Optimized for mobile

## 🌟 Why This Approach?

### Advantages
- ✅ **True Native App**: Installs like any Android app
- ✅ **No Server Required**: Everything runs locally
- ✅ **Offline Capable**: Works without internet
- ✅ **Full Feature Set**: All Flask functionality preserved
- ✅ **Easy Distribution**: Share APK with friends/family

### Use Cases
- **Personal Media Server**: Stream your own movies
- **Family Sharing**: Install on multiple devices
- **Travel Entertainment**: Offline movie collection
- **Home Cinema**: Big screen casting
- **Demo/Portfolio**: Show your streaming app

## 🎯 Next Steps

1. **Build Your APK**: Run `python3 build_apk.py`
2. **Test on Device**: Install and verify functionality
3. **Add Your Movies**: Transfer your video collection
4. **Customize**: Modify branding and features
5. **Share**: Distribute to friends and family

## 📞 Support

If you encounter issues:
1. Check this README for common solutions
2. Review build logs for specific errors
3. Ensure system requirements are met
4. Try clean build: `buildozer android clean`

---

**🎬 Enjoy your personal cinema on Android! 📱**