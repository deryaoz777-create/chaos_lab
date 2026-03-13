#!/bin/sh
# LD_LIBRARY_PATH'i runtime'da doğru şekilde set et
# nixpacks.toml TOML içinde $(...) shell ikamesini değerlendiremiyor

# Tüm gerekli .so kütüphanelerini bul (swisseph, sqlite, vb.)
for pkg in swisseph sqlite; do
    PKG_DIR=$(ls /nix/store 2>/dev/null | grep "^[a-z0-9]*-${pkg}-" | head -n 1)
    if [ -n "$PKG_DIR" ] && [ -d "/nix/store/$PKG_DIR/lib" ]; then
        export LD_LIBRARY_PATH="/nix/store/$PKG_DIR/lib:$LD_LIBRARY_PATH"
    fi
done

# stdenv cc lib de ekle (libstdc++ vb. için)
for libdir in /nix/store/*/lib; do
    if [ -f "$libdir/libsqlite3.so.0" ] || [ -f "$libdir/libsqlite3.so" ]; then
        export LD_LIBRARY_PATH="$libdir:$LD_LIBRARY_PATH"
        break
    fi
done

exec python server.py
