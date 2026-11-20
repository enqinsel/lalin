# Lalin / @lalinsahnede — Katmanlı Oda Prototipi v0.1

**Amaç:** Onaylanan genç-kadın odasını yeniden tasarlamadan, yeniden kullanılabilir bir sahne grafiği fikrini doğrulamak.

## Aç ve dene
- `preview.html` dosyasını tarayıcıda açın. Hiçbir paket kurulumu veya internet gerekmez.
- Telefon 2,00–2,80 saniyede titrer, kedi hafif nefes alır, çiçekler yavaş salınır.
- `Orijinal onaylı görsel` ve `Temiz plate` kontrolleriyle farkı görün.
- `scene.json`, sahne ölçülerini, katman konumlarını ve Foley olaylarını içerir.
- `build_assets.py`, mevcut maskeleri ve inpaint temiz plate'i kaynak PNG'den yeniden oluşturur (`pip install pillow numpy opencv-python`).

## Dosyalar
```
source_room.png          Onaylanan görsel; koruyun
assets/clean_plate.jpg   Prototip arka plan (inpaint)
assets/props/phone.png   Telefon katmanı, RGBA
assets/props/cat.png     Kedi katmanı, RGBA
assets/props/flowers.png Çiçek katmanı, RGBA
scene.json               Nesne konumları / zamanlama kuralları
preview.html            Tarayıcıda etkileşimli test
animation-test.mp4       Sessiz kısa önizleme (hazırlandıysa)
build_assets.py          Prototip maskelerinin yeniden üretimi
```

## Üretimde korunacak sabitler
- **Marka:** `@lalinsahnede`
- **Mekân:** Görselin renkleri, aksesuarlar, oda yerleşimi, manzara, ışık kaynağı
- **Karakter:** Lalin (30), ses: Higgsfield / Raina v1.0
- **Temel anlatı:** İstanbul Türkçesi, komedi, güçlü mimikler, gerçek Foley, ses-hareket senkronu

## Önemli sınırlama (kesinlikle okuyun)
Bu bir **animasyon rig'i veya profesyonel katmanlı sanat dosyası değildir**. Manuel çokgen maskelerle çıkarılmış 3 nesne ve OpenCV ile yaklaşık doldurulmuş arkaları içerir. İnce yapraklar/saç gibi kenarlar kusurlu olabilir. Telefon veya çiçek çok yer değiştirirse inpaint lekeleri ortaya çıkar. Kedinin yüzü henüz kemiklendirilmediği için yalnızca küçük ölçek hareketi var.

**Profesyonel üretim için:** Her animasyon nesnesini ayrı yüksek çözünürlüklü alfa katmanıyla yeniden çizin, kaldırıldığında görünen arka planı gerçek illüstrasyonla tamamlayın, eli/eşyayı karşılıklı bağlayın, Lalin'i rig edin, aynayı ayrı yansıma sahnesi haline getirin. Telefonun masada ve Lalin'in elinde aynı anda görünmesini engelleyen `attach/detach` mantığı kurun. Foley dosyalarını sağlayıp tam hareket temas karelerine bağlayın. Önemli nesneleri kodla kontrol edin; her kareyi AI ile yeniden çizerek kimlik/oda drift'i yaratmayın.

## Foley için önerilen zaman çizelgesi (demo)
- `0–6 sn`: room tone (henüz ses dosyası yok)
- `0–6 sn`: cat breathe/purr (henüz ses dosyası yok)
- `2.00 sn`: phone vibration başlar, `2.80 sn` biter (henüz ses dosyası yok)

Tam pilotta topuk vuruşları ayak-temas karelerine olay olarak işlenecek. Ses efektleri **bu demoda bulunmuyor**.
