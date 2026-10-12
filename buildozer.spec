[app]
title = Gui Dinh Vi SMS
package.name = guidinhvisms
package.domain = org.antoan

source.dir = .
source.include_exts = py,png,jpg,kv,atlas

version = 0.1

requirements = python3,kivy,plyer,pyjnius,android
orientation = portrait
fullscreen = 0

android.permissions = INTERNET, ACCESS_FINE_LOCATION, ACCESS_COARSE_LOCATION, SEND_SMS

# Cấu hình API và NDK chuẩn tương thích tuyệt đối
android.api = 33
android.minapi = 24
android.ndk_api = 24
android.ndk = 25b
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True
android.sdk = 33

[buildozer]
log_level = 2
warn_on_root = 1
