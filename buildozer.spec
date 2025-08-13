[app]

# (str) Title of your application
title = CineStream Mobile

# (str) Package name
package.name = cinestream

# (str) Package domain (needed for android/ios packaging)
package.domain = org.cinestream.app

# (str) Source code where the main.py live
source.dir = .

# (str) Main script for Android app
source.main_py = mobile_main.py

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas,json,txt,md

# (str) Application versioning (method 1)
version = 1.0.0

# (list) Application requirements
# comma separated e.g. requirements = sqlite3,kivy
requirements = python3,kivy==2.1.0,flask==2.3.3,werkzeug==2.3.7,jinja2==3.1.2,markupsafe==2.1.3,click==8.1.7,itsdangerous==2.1.2,plyer,android

# (str) Presplash of the application
# presplash.filename = %(source.dir)s/presplash.png

# (str) Icon of the application
# icon.filename = %(source.dir)s/icon.png

# (str) Supported orientation (one of landscape, sensorLandscape, portrait or all)
orientation = all

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (list) Permissions
android.permissions = INTERNET,ACCESS_NETWORK_STATE,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,WAKE_LOCK,ACCESS_WIFI_STATE

# (str) Android entry point, default is ok for Kivy-based app
# android.entrypoint = org.kivy.android.PythonActivity

# (str) Full name including package path of the Java class that implements Android Activity
# use that parameter together with android.entrypoint to set custom Java class instead of PythonActivity
# android.activity_class_name = org.kivy.android.PythonActivity

# (str) Full name including package path of the Java class that implements Python Service
# use that parameter to set custom Java class for service
# android.service_class_name = org.kivy.android.PythonService

# (str) Android app theme, default is ok for Kivy-based app
# android.apptheme = "@android:style/Theme.NoTitleBar"

# (list) Pattern to whitelist for the whole project
# android.whitelist =

# (str) Path to a custom whitelist file
# android.whitelist_src =

# (str) Path to a custom blacklist file
# android.blacklist_src =

# (str) Android logcat filters to use
# android.logcat_filters = *:S python:D

# (bool) Enable AndroidX support. Enable when 'android.gradle_dependencies'
# contains an 'androidx' package, or any package from Kotlin source.
# android.enable_androidx requires android.api >= 28
android.enable_androidx = True

# (str) Android API to use
android.api = 33

# (str) Minimum API your APK / AAB will support.
android.minapi = 21

# (str) Android NDK version to use
android.ndk = 25b

# (bool) Use --private data storage (True) or --dir public storage (False)
android.private_storage = True

# (str) Android NDK directory (if empty, it will be automatically downloaded.)
android.ndk_path =

# (str) Android SDK directory (if empty, it will be automatically downloaded.)
android.sdk_path =

# (str) ANT directory (if empty, it will be automatically downloaded.)
android.ant_path =

# (bool) If True, then skip trying to update the Android sdk
# This can be useful to avoid excess Internet downloads or save time
# when an update is due and you just want to test/build your package
android.skip_update = False

# (bool) If True, then automatically accept SDK license
# agreements. This is intended for automation only. If set to False,
# the default, you will be shown the license when first running
# buildozer.
android.accept_sdk_license = True

# (str) Android arch to build for, choices: armeabi-v7a, arm64-v8a, x86, x86_64
# In past, was `android.arch` as we weren't supporting builds for multiple archs at the same time.
android.archs = arm64-v8a, armeabi-v7a

# (int) overrides automatic versionCode computation (used in build.gradle)
# this is not the same as app version and should only be edited if you know what you're doing
# android.numeric_version = 1

# (bool) enables Android auto backup feature (Android API >=23)
android.allow_backup = True

# (str) XML file for custom backup rules (see official auto backup documentation)
# android.backup_rules =

# (str) If you need to insert variables into your AndroidManifest.xml file,
# you can do so with the manifestPlaceholders property.
# This property takes a map of key-value pairs. (via a string)
# Usage example : android.manifest_placeholders = key:value, key2:value2
# android.manifest_placeholders =

# (bool) Skip byte compile for .py files
# android.no-byte-compile-python = False

# (str) LauncherActivity to set as launch activity
# android.launcher_activity = org.kivy.android.PythonActivity

# (str) The Android manifest base template to use. Only works for bootstrap 'sdl2'.
# android.manifest_template = my_android_manifest_template.xml

# (str) Bootstrap to use for android builds
# android.bootstrap = sdl2

# (int) port number to specify an explicit --port= p4a apk argument (eg: --port=1024, shuts down background service)
# p4a.port =

# Control passing the --use-setup-py vs --ignore-setup-py to p4a
# "in the future" --use-setup-py is going to be the default behaviour in p4a, right now it is not
# Setting this to false will pass --ignore-setup-py, true will pass --use-setup-py
# NOTE: this is general setuptools integration, having pyproject.toml is enough, no need to generate
# setup.py if you're using Poetry, but you need to add "toml" to source.include_exts.
#p4a.setup_py = false

# (str) extra command line arguments to pass when invoking pythonforandroid.toolchain
#p4a.extra_args =

# (str) Name of the certificate to use for signing the debug version
# Get a list of available identities: buildozer android debug_keystore
#android.debug_keystore = ~/.android/debug.keystore

# (str) SHA1 key used to generate the debug keystore
# android.debug_keystore_sha1 = XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1

# (str) Path to build artifact storage, absolute or relative to spec file
# build_dir = ./.buildozer

# (str) Path to build output (i.e. .apk, .aab, .ipa) storage
# bin_dir = ./bin

#    -----------------------------------------------------------------------------
#    Notes about using this file:
#
#    1. If you are in China, add the following line before any requirements
#       android.gradle_repositories = google(), jcenter(), mavenCentral()
#
#    2. You can use the field `android.build_dir` to specify where the
#       build files are put.
#
#    3. The option `android.wakelock` prevents the device from
#       going to sleep while the app is running.
#       To disable it, add this line:
#       `android.wakelock = 0`
#
#    4. You can build multiple architectures by separating them with
#       comma in `android.archs`.
#       Example: `android.archs = armeabi-v7a, arm64-v8a, x86`
#
#    5. You can set custom Java source files directory and custom Java
#       compile classpath using
#       `android.java_src_dirs` and `android.java_compile_classpath`.
#
#    -----------------------------------------------------------------------------
