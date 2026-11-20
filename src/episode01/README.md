# Bölüm 01 sahne kaynakları

[Storyboard](../../reports/episode01_storyboard.md) · [Teslim ve QA](../../reports/episode01_qa.md) · [Üretim manifesti](generation_manifest.json)

| Plan | Ham Wan görüntüsü | Raina kaydı |
|---|---|---|
| 1 | [7 sn](../../outputs/episode01/wan/plan01.mp4) | [Plan 1](../../assets/voice/episode01/plan01.mp3) |
| 2 | [5 sn](../../outputs/episode01/wan/plan02.mp4) | [Plan 2](../../assets/voice/episode01/plan02.mp3) |
| 3 | [6 sn](../../outputs/episode01/wan/plan03.mp4) | [Önceden onaylanan kayıt](../../assets/voice/raina_pilot_line.mp3) |
| 4 | [10 sn](../../outputs/episode01/wan/plan04.mp4) | [Plan 4](../../assets/voice/episode01/plan04.mp3) |

Kanonik sahne zamanları ve ses kesitleri [scene_plan.json](scene_plan.json) içinde. [Ses kimliği ve ayarları](../../assets/voice/episode01/manifest.json) · [Foley kaynakları](audio/manifest.json) · [Ayna ışığı katmanı](art/mirror_off_overlay.png)

Yerel yeniden üretim komutları proje kökünden çalışır. Swift 6.4, Python 3.9.6, Pillow 11.3.0, NumPy 2.0.2, SciPy 1.13.1 ve FFmpeg 9.0.2 kullanıldı. Ham kliplerin dosyada bulunması yeterli.

```sh
LALIN_BUILD="$(mktemp -d)"
swiftc -O -module-cache-path "$LALIN_BUILD/swift-cache" src/phase03a/start_frame.swift -o "$LALIN_BUILD/frame"
"$LALIN_BUILD/frame" --episode-cutout "$LALIN_BUILD/actor.png"
/usr/bin/python3 src/episode01/prepare_audio.py "$LALIN_BUILD/driver"

for n in 1 2 3; do
  /usr/bin/python3 src/episode01/composite.py --shot "$n" \
    --input "outputs/episode01/wan/plan0$n.mp4" --actor "$LALIN_BUILD/actor.png" \
    --output "$LALIN_BUILD/plan0$n.mp4"
done
/usr/bin/python3 src/episode01/composite.py --shot 4 --frames 249 \
  --input outputs/episode01/wan/plan04.mp4 --actor "$LALIN_BUILD/actor.png" \
  --output "$LALIN_BUILD/plan04.mp4"
/usr/bin/python3 src/episode01/mix.py "$LALIN_BUILD/driver" "$LALIN_BUILD/mix.wav" --cloth-frame 22 --frames 789

cat > "$LALIN_BUILD/concat.ffconcat" <<'EOF'
ffconcat version 1.0
file 'plan01.mp4'
file 'plan02.mp4'
file 'plan03.mp4'
file 'plan04.mp4'
EOF
ffmpeg -f concat -safe 0 -i "$LALIN_BUILD/concat.ffconcat" -i "$LALIN_BUILD/mix.wav" \
  -map 0:v:0 -map 1:a:0 -c:v copy -c:a aac -b:a 192k -movflags +faststart "$LALIN_BUILD/bolum01.mp4"
```
