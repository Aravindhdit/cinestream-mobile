#!/usr/bin/env python3
"""
CineStream APK Builder
Script to build Android APK using Buildozer
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_requirements():
    """Check if required tools are installed"""
    print("🔍 Checking requirements...")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required")
        return False
    
    print("✅ Python version OK")
    
    # Check if running on Linux (required for Android builds)
    if os.name != 'posix':
        print("❌ Linux environment required for Android APK building")
        print("💡 Consider using WSL2 on Windows or a Linux VM")
        return False
    
    print("✅ Linux environment detected")
    
    return True

def install_buildozer():
    """Install Buildozer and dependencies"""
    print("📦 Installing Buildozer and dependencies...")
    
    try:
        # Install system dependencies
        subprocess.run([
            'sudo', 'apt-get', 'update'
        ], check=True)
        
        subprocess.run([
            'sudo', 'apt-get', 'install', '-y',
            'git', 'zip', 'unzip', 'openjdk-17-jdk', 'python3-pip',
            'autoconf', 'libtool', 'pkg-config', 'zlib1g-dev',
            'libncurses5-dev', 'libncursesw5-dev', 'libtinfo5',
            'cmake', 'libffi-dev', 'libssl-dev', 'build-essential',
            'libltdl-dev', 'ccache'
        ], check=True)
        
        print("✅ System dependencies installed")
        
        # Install Python dependencies
        subprocess.run([
            'pip3', 'install', '--user',
            'buildozer==1.5.0',
            'cython==0.29.33',
            'kivy==2.1.0'
        ], check=True)
        
        print("✅ Python dependencies installed")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        return False

def build_apk():
    """Build the Android APK"""
    print("🏗️  Building Android APK...")
    
    try:
        # Initialize buildozer (first time only)
        if not os.path.exists('.buildozer'):
            print("📋 Initializing Buildozer...")
            subprocess.run(['buildozer', 'init'], check=True)
        
        # Build APK in debug mode
        print("🔨 Building APK (this may take 30-60 minutes on first build)...")
        subprocess.run(['buildozer', 'android', 'debug'], check=True)
        
        # Find the built APK
        bin_dir = Path('./bin')
        apk_files = list(bin_dir.glob('*.apk'))
        
        if apk_files:
            apk_path = apk_files[0]
            print(f"✅ APK built successfully: {apk_path}")
            print(f"📱 File size: {apk_path.stat().st_size / (1024*1024):.1f} MB")
            
            # Copy to easy access location
            easy_path = Path('./CineStream-Mobile.apk')
            shutil.copy2(apk_path, easy_path)
            print(f"📋 APK copied to: {easy_path}")
            
            return True
        else:
            print("❌ APK file not found after build")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Error building APK: {e}")
        return False

def show_instructions():
    """Show installation and usage instructions"""
    print("\n" + "="*60)
    print("🎉 CineStream Mobile APK Build Complete!")
    print("="*60)
    print("\n📱 INSTALLATION INSTRUCTIONS:")
    print("1. Transfer CineStream-Mobile.apk to your Android device")
    print("2. Enable 'Install from Unknown Sources' in Android settings")
    print("3. Install the APK by tapping on it")
    print("4. Grant storage permissions when prompted")
    print("\n📁 MOVIE SETUP:")
    print("1. Create a 'Movies' folder in your Android storage")
    print("2. Copy your movie files (MP4, MKV, AVI, etc.) to this folder")
    print("3. Launch CineStream Mobile app")
    print("4. Enjoy your personal cinema!")
    print("\n🎬 FEATURES:")
    print("• Dolby Vision & Atmos support")
    print("• Mobile-optimized touch controls")
    print("• Progress tracking and resume")
    print("• High-quality streaming")
    print("• Download movies for offline viewing")
    print("\n💡 TROUBLESHOOTING:")
    print("• If movies don't appear, check folder permissions")
    print("• Supported formats: MP4, MKV, AVI, MOV, WMV, 3GP")
    print("• For best performance, use H.264/H.265 encoded videos")

def main():
    """Main build process"""
    print("🎬 CineStream Mobile APK Builder")
    print("=" * 40)
    
    if not check_requirements():
        print("\n❌ Requirements check failed. Please fix the issues above.")
        return 1
    
    print("\n📋 This script will:")
    print("1. Install Buildozer and Android build tools")
    print("2. Build your Flask movie server into an Android APK")
    print("3. Package all cinema features for mobile devices")
    print("\n⚠️  WARNING: First build may take 30-60 minutes and download 2-3GB")
    
    response = input("\n🤔 Continue with APK build? (y/N): ").strip().lower()
    if response != 'y':
        print("❌ Build cancelled by user")
        return 1
    
    if not install_buildozer():
        print("\n❌ Failed to install Buildozer")
        return 1
    
    if not build_apk():
        print("\n❌ Failed to build APK")
        return 1
    
    show_instructions()
    return 0

if __name__ == '__main__':
    sys.exit(main())