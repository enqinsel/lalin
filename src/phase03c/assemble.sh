#!/bin/sh
set -eu

if [ "$#" -ne 3 ]; then
    echo "Kullanım: sh src/phase03c/assemble.sh ilk_iki_plan.mp4 wan.mp4 teslim.mp4" >&2
    exit 2
fi

pickup=$1
performance=$2
output=$3
scratch=$(mktemp -d)
trap 'rm -f "$scratch/frame" "$scratch/matte.png" "$scratch/picture.mp4"; rmdir "$scratch"' EXIT

swiftc -module-cache-path "$scratch/../lalin03c-swift-cache" src/phase03a/start_frame.swift -o "$scratch/frame"
"$scratch/frame" --holding-matte "$scratch/matte.png"

ffmpeg -hide_banner -v error -n -i "$pickup" -i "$performance" \
    -loop 1 -framerate 30 -i outputs/phase03c/start_plan03.png \
    -loop 1 -framerate 30 -i "$scratch/matte.png" \
    -filter_complex_threads 2 -filter_complex "
        [0:v]fps=30,trim=end_frame=108,setpts=PTS-STARTPTS,setsar=1,format=yuv420p[pickup];
        [1:v]fps=30,trim=end_frame=90,setpts=PTS-STARTPTS,format=gbrp[motion];
        [2:v]trim=end_frame=90,setpts=PTS-STARTPTS,format=gbrp[still];
        [3:v]trim=end_frame=90,setpts=PTS-STARTPTS,format=gbrp,gblur=sigma=8:steps=2[matte];
        [still][motion][matte]maskedmerge,setsar=1,format=yuv420p[expression];
        [pickup][expression]concat=n=2:v=1:a=0[out]" \
    -map '[out]' -an -frames:v 198 -c:v libx264 -threads 2 -preset medium \
    -crf 16 -pix_fmt yuv420p -movflags +faststart "$scratch/picture.mp4"

/usr/bin/python3 src/phase02/mix.py "$scratch/picture.mp4" \
    --events src/phase03c/events.json --output "$output"
