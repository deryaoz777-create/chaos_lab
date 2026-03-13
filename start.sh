#!/bin/sh
# LD_LIBRARY_PATH'i runtime'da doğru şekilde set et
# nixpacks.toml TOML içinde $(...) shell ikamesini değerlendiremiyor

SWISSEPH_DIR=$(ls /nix/store 2>/dev/null | grep '^[a-z0-9]*-swisseph-' | head -n 1)
if [ -n "$SWISSEPH_DIR" ]; then
    export LD_LIBRARY_PATH="/nix/store/$SWISSEPH_DIR/lib:$LD_LIBRARY_PATH"
fi

exec python server.py
