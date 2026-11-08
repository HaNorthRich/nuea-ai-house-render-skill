#!/usr/bin/env bash
# Overlay Blender edges (red) on the AI image to check whether geometry drifted.
# usage: bash overlay.sh <blender.png> <ai.png> <out.png>
set -e
[[ $# -eq 3 ]] || { echo "usage: $0 blender.png ai.png out.png" >&2; exit 1; }
ffmpeg -v error -y -i "$2" -i "$1" -f lavfi -i "color=c=red:s=1080x1920" -filter_complex \
 "[0:v]scale=1080:1920,format=rgba[ai];[1:v]scale=1080:1920,edgedetect=low=0.05:high=0.15,format=gray,dilation[m];[2:v][m]alphamerge[e];[ai][e]overlay=format=auto" \
 -frames:v 1 "$3"
