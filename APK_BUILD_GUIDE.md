# 🎬 CineStream Android APK - Complete Build Guide

Transform your Flask movie streaming server into a native Android APK that works completely offline!

## 🎯 What You Get

Your CineStream app becomes a **real Android application** with:
- ✅ **Native Android Installation**: Install via APK file
- ✅ **Embedded Flask Server**: Runs your movie server inside the app
- ✅ **All Features Preserved**: Dolby animations, progress tracking, streaming
- ✅ **Mobile Optimized**: Touch controls and responsive design
- ✅ **Completely Offline**: No internet required after installation
- ✅ **Local Movie Storage**: Movies stored directly on your Android device

## 🚀 Three Build Methods

### Method 1: 🎯 One-Click Automated Build (Recommended)

If you have a Linux environment:

```bash
# Run the automated builder - handles everything!
python3 build_apk.py
```

**What it does:**
- Installs all Android build dependencies
- Sets up Android SDK and build tools
- Compiles your Flask app into Android APK
- Provides installation instructions
- Takes 30-60 minutes on first build

### Method 2: 🔧 Manual Build (Advanced Users)

```bash
# Install system dependencies (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install -y git zip unzip openjdk-17-jdk python3-pip autoconf libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo5 cmake libffi-dev libssl-dev build-essential libltdl-dev ccache

# Install Python build tools
pip3 install --user buildozer cython kivy

# Build the APK
buildozer init
buildozer android debug

# Your APK will be in: bin/cinestream-*.apk
```

### Method 3: ☁️ Cloud Build (No Linux Required)

If you don't have Linux, use GitHub Actions:

1. Push your code to GitHub repository
2. Create `.github/workflows/build-android.yml`:

```yaml
name: Build Android APK
on: [push]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    - name: Build APK
      run: |
        sudo apt-get update
        sudo apt-get install -y git zip unzip openjdk-17-jdk
        pip3 install buildozer cython
        buildozer android debug
    - name: Upload APK
      uses: actions/upload-artifact@v3
      with:
        name: CineStream-APK
        path: bin/*.apk
```

3. Download APK from GitHub Actions artifacts

## 📱 Installing on Android Device

### Step 1: Transfer APK
- Download `CineStream-Mobile.apk` from build output
- Transfer to your Android device via:
  - USB cable
  - Google Drive / Dropbox
  - Email attachment
  - File sharing app

### Step 2: Enable Unknown Sources
- Go to **Settings** → **Security** → **Install unknown apps**
- Enable for your file manager or browser
- Or: **Settings** → **Apps** → **Special access** → **Install unknown apps**

### Step 3: Install APK
- Locate the APK file on your device
- Tap to install
- Grant requested permissions (storage access)
- App will appear in your app drawer

## 📁 Setting Up Movies on Android

### Movie Storage Locations
The app will automatically scan these folders:
- `Internal Storage/Movies/`
- `Internal Storage/Download/Movies/`
- `SD Card/Movies/` (if available)

### Adding Movies
1. **Connect Device**: USB to computer or use file transfer app
2. **Create Movies Folder**: 
   - Navigate to Internal Storage
   - Create folder named "Movies" 
3. **Copy Movies**: Transfer your video files to this folder
4. **Supported Formats**: MP4, MKV, AVI, MOV, WMV, 3GP, M4V

### Recommended Video Settings
For best mobile performance:
- **Codec**: H.264 or H.265
- **Resolution**: 720p or 1080p
- **Bitrate**: 2-8 Mbps
- **File Size**: Under 4GB per file

## 🛠️ Build Environment Setup

### Linux Requirements (Recommended)
- **Ubuntu 20.04+** or **Debian 11+**
- **4GB RAM minimum** (8GB recommended)
- **20GB free disk space**
- **Python 3.8+**
- **Stable internet connection**

### Alternative Environments

#### Windows with WSL2
```bash
# Install WSL2 Ubuntu
wsl --install -d Ubuntu

# Enter WSL2 environment
wsl

# Follow Linux build instructions
python3 build_apk.py
```

#### Docker Container
```bash
# Use Android build container
docker run -it --rm -v $(pwd):/workspace kivy/buildozer bash
cd /workspace
buildozer android debug
```

#### Virtual Machine
- Install Ubuntu in VirtualBox/VMware
- Allocate 8GB RAM, 30GB disk
- Follow standard Linux build process

## 🔧 Customization Options

### App Branding
Edit `buildozer.spec`:
```ini
title = Your Movie App Name
package.name = yourmovieapp
package.domain = com.yourname.movieapp

# Add custom icon (512x512 PNG)
icon.filename = icon.png

# Add splash screen
presplash.filename = splash.png
```

### Movie Folder Customization
Edit `android_app.py`:
```python
def get_movies_folder(self):
    # Change default movies folder
    return '/storage/emulated/0/MyMovies/'
```

### App Permissions
Modify `buildozer.spec`:
```ini
android.permissions = INTERNET,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,WAKE_LOCK
```

## 🐛 Troubleshooting

### Build Issues

**"buildozer: command not found"**
```bash
# Add to PATH
echo 'export PATH=$PATH:~/.local/bin' >> ~/.bashrc
source ~/.bashrc
```

**"Java not found"**
```bash
# Install OpenJDK
sudo apt-get install openjdk-17-jdk
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
```

**"Android SDK download fails"**
```bash
# Clean and retry
buildozer android clean
buildozer android debug
```

**"Build takes too long"**
- First build: 30-60 minutes (downloads 2-3GB)
- Subsequent builds: 5-10 minutes
- Use `buildozer android debug` for faster debug builds

### App Runtime Issues

**"No movies found"**
- Check Movies folder exists: `/storage/emulated/0/Movies/`
- Verify app has storage permission
- Supported formats: MP4, MKV, AVI, MOV, WMV, 3GP

**"App crashes on startup"**
- Minimum Android 5.0 (API 21) required
- Clear app data: Settings → Apps → CineStream → Storage → Clear Data
- Check device logs: `adb logcat | grep python`

**"Videos won't play"**
- Use H.264/H.265 codecs
- Keep files under 4GB
- Test with small MP4 file first

### Performance Issues

**"Slow video loading"**
- Use H.264 codec for faster decoding
- Reduce video bitrate if necessary
- Store on internal storage (faster than SD card)

**"Battery drain"**
- Enable battery optimization exception
- Close app when not in use
- Use airplane mode for offline viewing

## 📊 Technical Details

### APK Structure
```
CineStream-Mobile.apk
├── Python runtime (embedded)
├── Flask web server
├── Kivy UI framework
├── Video player components
├── File system access
└── Android integration layer
```

### How It Works
1. **App Launch**: Kivy app starts with native Android interface
2. **Flask Server**: Embedded web server starts on localhost:5000
3. **Movie Scanning**: App scans device storage for video files
4. **Web Interface**: Native WebView loads Flask movie interface
5. **Video Streaming**: Direct file access with range request support

### Security & Privacy
- ✅ **No Internet Required**: Completely offline operation
- ✅ **Local Storage Only**: Movies never leave your device
- ✅ **No Data Collection**: No analytics or tracking
- ✅ **Open Source**: Full source code available

## 🎯 Why This Approach?

### Advantages over Web App
- ✅ **True Native App**: Install from APK like any Android app
- ✅ **No Browser Dependency**: Works without web browser
- ✅ **Better Performance**: Direct hardware access
- ✅ **Offline Guaranteed**: No accidental internet usage
- ✅ **Professional Feel**: Native Android experience

### Use Cases
- **Personal Entertainment**: Your movie collection anywhere
- **Family Sharing**: Install on multiple family devices
- **Travel Companion**: Offline entertainment for flights/trips
- **Home Media Server**: Stream to living room devices
- **App Portfolio**: Showcase your development skills

## 🌟 Alternative: Progressive Web App (PWA)

If APK building seems complex, consider a PWA:

### Quick PWA Setup
1. Add manifest.json to your Flask app
2. Add service worker for offline support
3. Open app in mobile browser
4. Tap "Add to Home Screen"
5. Works like native app!

### PWA vs APK Comparison
| Feature | PWA | APK |
|---------|-----|-----|
| Setup Complexity | ⭐ Easy | ⭐⭐⭐ Complex |
| Installation | Browser menu | APK file |
| Performance | ⭐⭐ Good | ⭐⭐⭐ Excellent |
| Offline Support | ⭐⭐ Limited | ⭐⭐⭐ Complete |
| File Access | ⭐ Restricted | ⭐⭐⭐ Full access |
| Updates | ⭐⭐⭐ Automatic | ⭐ Manual |

## 📞 Next Steps

1. **Choose Build Method**: Automated script, manual, or cloud
2. **Prepare Environment**: Linux system or alternative
3. **Build APK**: Follow chosen method instructions
4. **Test Installation**: Install on Android device
5. **Add Movies**: Transfer your video collection
6. **Enjoy**: Your personal cinema app is ready!

## 💡 Tips for Success

- **Start Small**: Test with a few movies first
- **Check Formats**: Ensure videos are mobile-compatible
- **Monitor Storage**: Android apps have storage limits
- **Test Thoroughly**: Try on different Android versions
- **Backup APK**: Save your built APK for redistribution

---

**🎬 Transform your Flask movie server into a powerful Android cinema app! 📱**

Need help? Check the README_ANDROID.md for more detailed instructions.