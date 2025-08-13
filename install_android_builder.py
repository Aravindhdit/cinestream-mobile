#!/usr/bin/env python3
"""
Android Builder Setup Script
Sets up the environment for building Android APK from Flask app
"""

import os
import sys
import subprocess
import platform

def main():
    """Main setup function"""
    print("🎬 CineStream Android APK Builder Setup")
    print("=" * 50)
    
    print("This will convert your Flask movie server into an Android APK!")
    print("\n📱 What you'll get:")
    print("• Native Android app with embedded Flask server")
    print("• All cinema features preserved (Dolby, progress tracking, etc.)")
    print("• Mobile-optimized touch controls")
    print("• Offline movie streaming from device storage")
    print("• No internet required once installed")
    
    print("\n🏗️  Build Requirements:")
    print("• Linux environment (Ubuntu/Debian recommended)")
    print("• Python 3.8+")
    print("• 4GB+ RAM, 20GB+ disk space")
    print("• Stable internet for initial setup")
    
    print("\n🚀 Quick Build Options:")
    
    print("\n1️⃣  AUTOMATED BUILD (Recommended)")
    print("   Run: python3 build_apk.py")
    print("   • Installs all dependencies automatically")
    print("   • Builds APK with single command")
    print("   • Provides installation instructions")
    
    print("\n2️⃣  MANUAL BUILD (Advanced)")
    print("   See README_ANDROID.md for detailed steps")
    
    print("\n3️⃣  CLOUD BUILD (Alternative)")
    print("   • Use GitHub Actions for building")
    print("   • No local Linux requirement")
    print("   • Automated APK generation")
    
    print("\n4️⃣  ALTERNATIVE METHODS:")
    print("   • PWA (Progressive Web App)")
    print("   • Capacitor/Cordova wrapper")
    print("   • React Native bridge")
    
    # Check current environment
    print("\n🔍 Environment Check:")
    print(f"• OS: {platform.system()} {platform.release()}")
    print(f"• Python: {sys.version.split()[0]}")
    print(f"• Architecture: {platform.machine()}")
    
    if platform.system() == "Linux":
        print("✅ Linux environment detected - ready for APK building!")
    else:
        print("⚠️  Non-Linux environment detected")
        print("💡 Consider using:")
        print("   • WSL2 on Windows")
        print("   • Linux VM")
        print("   • Docker container")
        print("   • Cloud build service")
    
    print("\n📋 Files Created:")
    print("• android_app.py - Kivy/Android app wrapper")
    print("• buildozer.spec - Android build configuration")
    print("• mobile_main.py - Android app entry point")
    print("• build_apk.py - Automated build script")
    print("• README_ANDROID.md - Complete build guide")
    
    print("\n🎯 Next Steps:")
    print("1. Read README_ANDROID.md for detailed instructions")
    print("2. Run 'python3 build_apk.py' on Linux to build APK")
    print("3. Transfer APK to Android device and install")
    print("4. Add movies to device storage and enjoy!")
    
    print("\n💡 Alternative: Progressive Web App (PWA)")
    print("For a simpler mobile solution, you can also:")
    print("1. Open your Flask app in mobile browser")
    print("2. Add to Home Screen (creates app-like icon)")
    print("3. Works like native app with web technologies")
    
    response = input("\n❓ Would you like to see PWA setup instructions? (y/N): ").strip().lower()
    if response == 'y':
        show_pwa_instructions()
    
    print("\n🎉 Setup complete! Check README_ANDROID.md for next steps.")

def show_pwa_instructions():
    """Show PWA (Progressive Web App) setup instructions"""
    print("\n" + "="*50)
    print("📱 Progressive Web App (PWA) Setup")
    print("="*50)
    
    print("\nPWA is a simpler alternative that works on any mobile device:")
    
    print("\n🔧 Setup Steps:")
    print("1. Ensure your Flask app is accessible on your mobile device")
    print("2. Open web browser on mobile device")
    print("3. Navigate to your Flask app URL")
    print("4. Tap browser menu → 'Add to Home Screen'")
    print("5. App icon appears on home screen like native app")
    
    print("\n✅ PWA Advantages:")
    print("• No APK building required")
    print("• Works on iPhone and Android")
    print("• Automatic updates")
    print("• Full screen experience")
    print("• Offline caching possible")
    
    print("\n📝 To add PWA support to your Flask app:")
    print("1. Add manifest.json file")
    print("2. Add service worker for offline support")
    print("3. Add meta tags for mobile optimization")
    
    pwa_code = '''
# Add to your Flask app template:
<link rel="manifest" href="/static/manifest.json">
<meta name="theme-color" content="#000000">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black">

# Create /static/manifest.json:
{
  "name": "CineStream Mobile",
  "short_name": "CineStream",
  "description": "Premium Mobile Cinema Experience",
  "start_url": "/",
  "display": "fullscreen",
  "background_color": "#000000",
  "theme_color": "#ff6b6b",
  "icons": [
    {
      "src": "/static/icon-192.png",
      "sizes": "192x192",
      "type": "image/png"
    }
  ]
}
'''
    
    print(f"\n💻 Code Example:\n{pwa_code}")

if __name__ == '__main__':
    main()