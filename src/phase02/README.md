# Lalin · Ayna

Godot 4.7.2 Stable ile `project.godot` dosyasını içe aktarın ve F6 ile [LalinPilot.tscn](LalinPilot.tscn) sahnesini veya F5 ile projeyi çalıştırın. Sesli önizleme 10,2 saniyede başa döner. Raina orijinali proje ağacında `assets/voice/raina_pilot_line.mp3` yolundan okunur. MP4 için 30 fps görüntüyü ve 48 kHz sesi aşağıdaki şekilde birleştirin.

Proje kökünde çalıştırın. `GODOT_BIN` değerini kurulu Godot'un komut yolu olarak girin. Kare çıktısı için macOS grafik oturumu gerekiyor.

```sh
GODOT_BIN=/Applications/Godot.app/Contents/MacOS/Godot
LALIN_RENDER_DIR="$(mktemp -d)"
"$GODOT_BIN" --path src/phase02 --editor --headless --import
"$GODOT_BIN" --path src/phase02 --disable-vsync -- --frames "$LALIN_RENDER_DIR/frames"
ffmpeg -framerate 30 -start_number 0 -i "$LALIN_RENDER_DIR/frames/frame_%04d.png" \
  -frames:v 306 -c:v libx264 -threads 2 -crf 16 -preset medium -pix_fmt yuv420p \
  -movflags +faststart "$LALIN_RENDER_DIR/picture.mp4"
/usr/bin/python3 src/phase02/mix.py "$LALIN_RENDER_DIR/picture.mp4" \
  --output "$LALIN_RENDER_DIR/lalin_pilot.mp4"
```

- [Karakter rig'i](lalin_rig.gd), `Node2D` üzerinde ayrı yüz ve saç parçalarını, omuz ve el pozlarını, bacakları ve bağımsız topukları birleştirir. Kollar ve bacaklar iki eklemli ters kinematikle pozlanır. `pose_face` ve `pose_body` başka sahnelerde aynı görsel parçalarla kullanılabilir. Düzenlenebilir SVG beden parçaları [art/body](art/body), yüz parçaları [art/face](art/face) altında.
- [Sahne zamanlaması](pilot.gd), kadrajları, ayak rotalarını ve rujun hareketini içerir. [Olay çizelgesi](events.json) ses saldırı örneklerini karelere bağlar. [Konuşma zamanlaması](dialogue.json) kayda göre elle anahtarlanmış ağız şekillerini taşır.
- Yüz parçalarını `/usr/bin/python3 src/phase02/prepare_face.py`, oda plakalarını ve ruju `/usr/bin/python3 src/phase02/room_prepare.py` ile yeniden hazırlayabilirsiniz. Bu iki komut Pillow 11.3.0, NumPy 2.0.2 ve SciPy 1.13.1 ile doğrulandı. Ses kökenleri [foley manifestinde](audio/manifest.json), Raina kimliği ve üretim ayarları [ses manifestinde](../../assets/voice/phase02_manifest.json).

Render sırasında yalnız belirli kareleri almak için `--frames` klasörünün sonuna kare numaralarını ekleyin. Örnek kareler 18, 43, 110, 144, 225, 252 ve 282.
