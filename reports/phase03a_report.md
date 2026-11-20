# Lalin · Faz 03A oyunculuk testi

20 Kasım 2026 · [5 saniyelik test](../outputs/phase03a/lalin_acting_test.mp4) · [Başlangıç karesi](../outputs/phase03a/lalin_start_frame.png) · [Kare hazırlama kaynağı](../src/phase03a/start_frame.swift)

Faz 02'nin f110 ve f144 karelerinde omuz şişiyor, kol silindirik kalıyor ve dirsek birleşimi okunuyor. Görünüm ilk onaylı çizimin siluetinden ayrılıyor. Bu denemede karakter ve ceket doğrudan ilk onaylı çizimden alındı. İkinci ve üçüncü paftalar yüz ve ifade kontrolünde kullanıldı. Onaylı oda master'ından alınan makyaj masası kadrajı aynı oran, renk ve dekor yerleşimini koruyor. Başlangıç karesi Swift 6.4 ve Core Graphics ile yerelde hazırlandı.

## Yöntem seçimi

| Yöntem | Girdi ve kontrol | 5 sn, 9:16 |
|---|---|---|
| Higgsfield Wan 2.7 image-to-video | Doğrudan başlangıç karesi ve Raina ses referansı alıyor. Ek oyuncu kaydına gerek yok. Yüz ve dekor sürekliliği çıktıda ölçülür. | **1080p, 12,5 kredi.** Tek üretim seçildi ve girdilerle MCP üzerinden yeniden fiyatlandı. [Wan giriş belgeleri](https://docs.modelstudio.console.alibabacloud.com/en/model-studio/image-to-video-general-api-reference) |
| Seedance 2.5 image-to-video | Başlangıç karesi, ek görsel referanslar ve ses kabul ediyor. Orijinal sesin aynen döndüğü doğrulanmalı. | MCP ön fiyatı 720p 35, 1080p 80 kredi. [Higgsfield ses referansı](https://higgsfield.ai/enterprise-help-center/platform/ugc-consistent-voice) |
| Genjutsu Motion Transfer | Karakter referansı ve 4–30 saniyelik sürücü video ister. Bu replik için Raina kaydına eşlenmiş, sabit kameralı bel üstü oyuncu kaydı gerekli. Doğal performans aktarımı avantajlı. Sahneyi de yeniden üretebildiği için dekor ayrıca denetlenir. | Sürücü video eksik. MCP girdiler olmadan kesin fiyat döndürmedi. [Genjutsu rehberi](https://higgsfield.ai/creator-hub/help-center/tools/how-do-i-use-genjutsu) |

Tek kadrajda yürüyüş ve ruj aksiyonu kapsam dışı. Çeneye yakın el, ilk çizimdeki dinlenme pozunda. Mevcut Raina kaydının başına 0,70 saniye sessizlik eklendi. [Sürücü ses](../outputs/phase03a/raina_5s.wav) 48 kHz PCM, 5,000 saniye. İlk sesli hece yaklaşık 0,824 sn, kısa kıkırdama/nefes bölümü 3,795–4,075 sn. Bunlar bakış, tek kaş ve kahkaha için kontrol noktaları.

## Sonuç ve kalite

Tek Wan 2.7 işi `ccb6ccdf-a83e-48df-a5ea-1013b173e37a` tamamlandı. Onaylanan ve girdilerle doğrulanan fiyat **12,5 kredi**. MCP'nin tamamlanma kaydı kesinleşen kredi kesintisini göstermedi. Çıktı **1080×1920, 30 fps, 150 kare, 5,000 sn**. FFmpeg 9.0.2, Wan görüntüsünü yeniden kodlamadan orijinal Raina kaydından hazırlanan 48 kHz sesle birleştirdi. H.264 akış özeti eşleşti ve teslim MP4'ü baştan sona hatasız çözüldü.

| Kontrol | Sonuç | Kanıt |
|---|---|---|
| Yüz kimliği, anatomi ve kıyafet | GEÇTİ | Başlangıç, f30, f72, f115 ve f149'da yüz, saç çizgisi, ceket ve takılar aynı karakteri taşıyor. Çenedeki el ve dirsek pozunda kopma veya kauçuk gibi esneme gözlenmedi. |
| Oda ve kadraj | GEÇTİ | Neon, altın ayna, sarmaşık, telefon ve kozmetik dizilimi 150 kare boyunca aynı yerde. Küçük ton ve doku farkları var. |
| Bakış ve tek kaş | KISMİ | f18'de göz kırpma, f20–30'da yan bakış ve asimetrik kaş belirgin. Gözün açılması ve kaşların içe yaklaşması bazı karelerde alaydan çok şaşkınlık veriyor. |
| Konuşma senkronu | KISMİ | Ana replik 0,824–3,533 sn içinde. f23'te dudak hazırlığı, konuşma boyunca farklı açıklıklar görülüyor. 2,33–2,48 sn duraklamasında ağız açık kalıyor. Türkçe hece pozları tam doğrulanmadı. Wan'ın ses izi sürücüyle 0 örnek gecikme ve 0,999596 korelasyon verdi. Teslim sesinde gecikme yine 0 örnek. |
| Gülüş, yanak, baş, omuz ve saç | KISMİ | 3,795–4,075 sn kıkırdama/nefes vurgusuna kapanan göz ve yükselen yanak eşlik ediyor. Dudak, omuz ve saç tepkisi sınırlı. Görsel, belirgin kahkahadan çok uzun bir gülümseme okuyor. |

Bu deneme, Faz 02'deki gövde ve eklem hatalarını tekrarlamadan aynı Lalin'i ve odayı koruyor. Başlangıç karesi görsel referans olarak kullanılabilir. Oyunculuk onayı için yumuşak tek kaş vurgusu, Türkçe duraklamalara daha iyi ağız eşliği ve kahkahanın omuz ve saça yansıması açık kaldı. Performans aktarımı karşılaştırması için bu üç vurguyu taşıyan sabit kameralı bel üstü oyuncu kaydı gerekir.

**KISMİ**
