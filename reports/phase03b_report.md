# Lalin · Faz 03B ruj oyunculuk testi

20 Kasım 2026 · [Başlangıç karesi](../outputs/phase03b/lalin_start_frame.png) · [6 saniyelik test MP4](../outputs/phase03b/lalin_lipstick_test.mp4) · [Gerçek kare örnekleri](../outputs/phase03b/lalin_kare_ornekleri.jpg)

Faz 03A'daki karakter çizimi aynı kaynak piksellerle sola alındı. Altın küçük ayna ve hemen sağındaki kapalı bordo-altın ruj görünür. Arkadaki açık pembe ruj, telefon ve diğer dekor onaylı oda master'ındaki yerinde. Karakter katmanı doğrudan 01 numaralı onaylı çizimden. Başlangıç karesi `swift src/phase03a/start_frame.swift --vanity-reach` ile üretilebilir.

Higgsfield Wan 2.7 (`wan2_7`) tek işi tamamlandı. İş kimliği `b62a6929-8e8c-4d60-afb0-8ad142474d6a`. Başlangıç karesiyle kesin fiyat **15 kredi**, kullanıcı onayı alındı. Kesinleşen kesinti MCP yanıtında görünmedi. Diyalogsuz teslim **6,000 sn, 1080×1920, 30 fps, 180 kare**, H.264 ve 48 kHz AAC. FFmpeg 9.0.2 ile gerçek foley eklendi. Kaynak ve teslim H.264 akış özeti eşleşti. [Foley kayıtları ve CC0 kaynakları](../src/phase03b/audio/manifest.json)

## Görsel QA

| Kontrol | Sonuç | Gerçek kare kanıtı |
|---|---|---|
| Lalin'in görsel kimliği | GEÇTİ | Yüz, uzun saç, bordo ceket, krem üst ve takılar çekim boyunca tanınır. [f000](../outputs/phase03b/frames/f000.png) · [f179](../outputs/phase03b/frames/f179.png) |
| Uzanma ve el anatomisi | KISMİ | El çeneden akıcı ayrılıyor ve iki el kapağı tutabiliyor. Uzanmada bazı parmak uçları bulanıklaşıyor. Kitap temasında el ve nesne sınırı birleşiyor. [f040](../outputs/phase03b/frames/f040.png) |
| Rujun alınması ve tek nesne sürekliliği | KALDI | 1,23–1,43 sn arasında kitap yığını eldeki büyük bordo tüpe dönüşüyor. Makyaj masasındaki seçili ince kapalı ruj yerinde kalıyor. [Dönüşüm f040](../outputs/phase03b/frames/f040.png) · [İki nesne f043](../outputs/phase03b/frames/f043.png) |
| Kapak hareketi | KISMİ | Elde oluşan tüpte kapak f126'da, 4,200 sn'de görünür biçimde ayrılıyor. Gövde diğer elde kalıyor. [f126](../outputs/phase03b/frames/f126.png) |
| Ayna bakışı ve ikincil oyunculuk | KISMİ | Uzanmada omuz, ceket ve saç tepki veriyor. Son bakışta gözler belirgin açılıyor ve yukarı kayıyor. Son karede ruj ucu dudağa geliyor. Kendinden emin ayna bakışı okunmuyor. [f179](../outputs/phase03b/frames/f179.png) |
| Oda sürekliliği | KALDI | Ayna, telefon ve neon sabit, kadraj kesintisiz. Sağ öndeki dört kitap f43'e gelindiğinde masadan siliniyor. [f000](../outputs/phase03b/frames/f000.png) · [f043](../outputs/phase03b/frames/f043.png) |

## Ses kontrolü

| Foley | Kare | Başlangıç örneği, 48 kHz |
|---|---:|---:|
| Uzanmada ceket yakası | 17 · 0,567 sn | 27.200 |
| Destek eli kalkarken bileklik | 47 · 1,567 sn | 75.200 |
| Elde oluşan tüpte kapak ayrılması | 126 · 4,200 sn | 201.600 |

Üç kaydın çözülmüş AAC dalga biçimleriyle eşleşen konumları, hedefe göre **0 örnek sapma** gösterdi. Miks tepesi **−11,44 dBFS**. 180 kare tarandı ve kritik hareketler ardışık tam çözünürlükte kontrol edildi. [Olay ve miks girdileri](../src/phase03b/events.json)

Asıl rujun alınması ve dekor sürekliliği kabul şartını karşılamadığı için bu çıktı başarısız deneme kaydıdır.

**KALDI**
