#!/usr/bin/env bash
set -Eeuo pipefail

SRC="$(cd -- "$(dirname "$0")" && pwd)/src"

BRIAN_IP="192.168.4.1"
API="http://${BRIAN_IP}/api/sd"


urlencode_path() {
    python3 -c '
import sys
from urllib.parse import quote
print("/".join(quote(x, safe="") for x in sys.argv[1].split("/")))
' "$1"
}


upload_file() {
    local local_file="$1"
    local remote_path="$2"
    local encoded
    local content_type
    local url

    encoded="$(urlencode_path "$remote_path")"

    case "${local_file,,}" in
        *.py)
            content_type="text/x-python"
            ;;
        *.txt|*.log)
            content_type="text/plain"
            ;;
        *.png)
            content_type="image/png"
            ;;
        *.jpg|*.jpeg)
            content_type="image/jpeg"
            ;;
        *.wav)
            content_type="audio/wav"
            ;;
        *.mp3)
            content_type="audio/mpeg"
            ;;
        *)
            content_type="application/octet-stream"
            ;;
    esac

    url="${API}/${encoded}"

    echo "Uploading: $remote_path"

    curl \
        --fail-with-body \
        --silent \
        --show-error \
        -X PUT \
        -H "Content-Type: $content_type" \
        --data-binary "@$local_file" \
        "$url"

    echo " OK"
}


echo "Checking Brian connection..."

if ! curl \
    --fail \
    --silent \
    --connect-timeout 2 \
    "$API" >/dev/null
then
    echo "ERROR: Cannot connect to Brian at $BRIAN_IP"
    echo "Make sure the computer is connected to Brian's Wi-Fi."
    exit 1
fi

echo "Uploading program..."
echo


while IFS= read -r -d '' file; do
    rel="${file#$SRC/}"
    upload_file "$file" "$rel"
done < <(find "$SRC" -type f -print0)


echo
echo "Upload complete!"