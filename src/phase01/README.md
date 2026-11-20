# Faz 01 kaynakları

İki komutu proje kökünden sırayla çalıştırın. İkisi de 540×960, 30 fps H.264 MP4 yazar. Ağ erişimi gerekmez.

```sh
/usr/bin/python3 src/phase01/face_test.py
swift -module-cache-path /tmp/lalin-swift-cache src/phase01/prop_test.swift
```

- `face_test.py`, ikinci onaylı çizimin portresine elle zamanlanmış iki kaş, iris, kapak, yanak, ağız, baş ve omuz hareketleri uygular. Göz sınırları ve dudak dikişi bu portreye göre belirlendi. Çıktı `outputs/phase01/lalin_face_test.mp4` ve ses kanalı yok.
- `prop_test.swift`, çizilmiş bir test elini ve bağımsız ruj nesnesini Core Graphics ile render eder. Temas karelerindeki iki geçici ses, 48 kHz PCM olarak kodda hesaplanır ve MP4'e AAC olarak yazılır. Çıktı `outputs/phase01/lalin_prop_test.mp4`.

Doğrulanan ortam Apple Silicon, Python 3.9.6, Pillow 11.3.0, NumPy 2.0.2, SciPy 1.13.1, Swift 6.4 ve `libx264`/AAC destekli FFmpeg 9.0.2. Bu makinede Python paketleri `/usr/bin/python3` altında kurulu. Başka bir Python ortamında Pillow, NumPy ve SciPy'nin kurulu olduğu yorumlayıcıyı kullanın.

Yüz testinden tek kare almak için `--still 79 --output /tmp/lalin_f079.png` ekleyin. Ruj testinde varsayılan çıktı yolunu değiştirmek için Swift komutunun sonuna MP4 yolunu ekleyin. [Kare ve ses çizelgesi](../../reports/phase01_event_timing.csv).
