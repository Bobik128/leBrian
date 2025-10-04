#!/usr/bin/env bash
set -Eeuo pipefail

# --- adjust these two paths as needed ---
SRC="$(cd -- "$(dirname "$0")" && pwd)/src/"
DEST="/run/media/tomas/BRIAN/"   # any folder INSIDE the SD card mount

# Helper to run host tools from Flatpak VS Code
HOST() { flatpak-spawn --host "$@"; }

echo "Copying files to SD card..."
HOST /usr/bin/rsync -av --delete "$SRC" "$DEST"

echo "Syncing buffers..."
HOST /bin/sync

# Auto-detect the mounted block device for DEST
DEV="$(HOST /usr/bin/findmnt -T "$DEST" -no SOURCE || true)"
MNT="$(HOST /usr/bin/findmnt -T "$DEST" -no TARGET || true)"

if [[ -z "$DEV" || -z "$MNT" ]]; then
  echo "ERROR: Could not detect device/mount for: $DEST"
  HOST /usr/bin/findmnt -T "$DEST" || true
  HOST /usr/bin/lsblk -f || true
  exit 1
fi

echo "Detected mountpoint: $MNT"
echo "Detected device:     $DEV"

# Determine the parent disk (for power-off)
PARENT_KNAME="$(HOST /usr/bin/lsblk -no pkname "$DEV" 2>/dev/null || true)"
if [[ -n "$PARENT_KNAME" ]]; then
  PARENT_DEV="/dev/${PARENT_KNAME}"
else
  # Fallback: strip trailing partition number (handles sdb1 and mmcblk0p1)
  BASENAME="$(basename "$DEV")"
  PARENT_DEV="/dev/$(echo "$BASENAME" | sed -E 's/p?[0-9]+$//')"
fi
echo "Parent device:       $PARENT_DEV"

echo "Unmounting and ejecting SD card..."
if HOST /usr/bin/udisksctl unmount -b "$DEV"; then
  HOST /usr/bin/udisksctl power-off -b "$PARENT_DEV" || true
else
  echo "udisksctl unmount failed; trying umount fallback..."
  HOST /usr/bin/umount "$MNT" || true
fi

echo "SD card ejected safely!"
