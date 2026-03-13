#!/bin/sh
# Nix store'daki tüm lib dizinlerini LD_LIBRARY_PATH'e ekle
# Böylece libsqlite3.so.0, libswe.so vb. hepsi bulunur
export LD_LIBRARY_PATH=$(find /nix/store -maxdepth 2 -type d -name lib 2>/dev/null | paste -sd: -):$LD_LIBRARY_PATH
echo "LD_LIBRARY_PATH set, starting server..."
exec python server.py
