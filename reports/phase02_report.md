# Lalin · Faz 02 kalite kontrolü

20 Kasım 2026 · [10,2 saniyelik pilot](../outputs/phase02/lalin_pilot.mp4) · [Godot sahnesi](../src/phase02/LalinPilot.tscn) · [Kaynak ve render komutları](../src/phase02/README.md)

Lalin pencere önünde iki topuk adımı atıyor. Kesmeden sonra makyaj masasından ruju alıyor, aynaya doğru kaş kaldırıp Raina sesiyle “Ben senin fikrini değil, ışığını sordum.” diyor. Aynı kaydın sonundaki kısa kıkırdama/nefes vurgusundan sonra ruju masaya bırakıyor. **540×960, 9:16, 30 fps, 306 kare**. H.264 görüntü ve mono 48 kHz AAC ses.

## Varlıklar ve yöntem

- Faz 01'in portre deformasyonu ve şematik temas görüntüsü bu sahnede kullanılmadı. İlk onaylı paftadaki bordo ceket, krem kombin ve topuk silueti temel alındı. İkinci paftanın özgün portresi saç, yüz, iki kaş, göz, kapak ve dudak katmanlarına ayrıldı. İkinci ve üçüncü paftanın genel gövde oranları ayrı çizilen SVG beden parçalarına rehber oldu. Ceket, kol hareketini gösterebilmek için kolları giyilmiş biçimde çizildi.
- Onaylı master, pencere önü ve makyaj masası için iki ayrı, oranı korunmuş kamera kadrajı olarak kullanıldı. Sandalyeler ayrı örtüşme katmanları. Hareketli bordo ruj ve masadaki sabit parlaması için yerel temizleme yapıldı. Master'dan türetilen temiz plakada 2.852 piksel değişti. Diğer ürünler yerinde.
- Godot **4.7.2 Stable**, GDScript, 2D parça rig'i ve eklem çözümüyle tüm 306 kareyi üretti. FFmpeg **9.0.2**, kayıtları karelere bağlayıp MP4'ü yazdı. Konuşma ağız pozları Whisper.cpp 1.8.4 tiny'nin yönlendirilmiş sözcük zamanları ve ses zarfı kullanılarak elle anahtarlandı. Bunlar yaklaşık hece pozları.
- Higgsfield MCP'de Raina hazır sesi doğrulandı. `voice_id` **`1c3a4775-9afb-52c1-a2bf-b6543231a9a1`**, model **`elevenlabs_v4`**. Onayla bir üretim tamamlandı. Kesin teklif ve onay **0,69 kredi**. MCP kesinleşen kesintiyi göstermedi. Başka ücretli üretim olmadı. [Raina orijinali](../assets/voice/raina_pilot_line.mp3) · [Üretim ayarları](../assets/voice/phase02_manifest.json)
- İki topuk, bir masa üstü alma sesi ve bir küçük plastik temas sesi gerçek kayıttan seçildi. Plastik ses, ruj kasasının masaya vuruşu için kullanıldı. CC0 kaynakları ve alındıkları aralıklar kayıtlı. [Foley kaynakları](../src/phase02/audio/manifest.json)

## Kare ve ses doğrulaması

Kodlanmış MP4'ün 306 karesi sıralı önizlemelerde, dört fiziksel temas da ardışık büyütülmüş karelerde incelendi. Ses sapması, 48 kHz'e çözülen AAC ile kaynak kayıtların dalga biçimi eşleştirilerek ölçüldü. Ruj başparmağı f109–110 aralığında gövdeye ulaşıyor. Çizelgede ilk belirgin örtüşme olan f110 kullanıldı.

| Kare | Süre | Görünen eylem | Ses |
|---:|---:|---|---|
| 18 | 0,600 sn | İlk topuk sert karoya oturuyor. | 28.800. örnek, çizelgeye göre 0 kare |
| 43 | 1,433 sn | İkinci topuk karoya oturuyor. | 68.800. örnek, 0 kare |
| 66 | 2,200 sn | Pencere önünden makyaj masasına kesme. | — |
| 110–116 | 3,667–3,867 sn | Başparmak ruja ulaşıyor, tutuş kapanıyor, taban masadan ayrılıyor. | f110, 176.000. örnek, 0 kare |
| 143–150 | 4,767–5,000 sn | Baş, göz ve tek kaşın hazırlık jesti. | — |
| 156 | 5,200 sn | Raina dosyası başlıyor. İlk sesli hece yaklaşık f160. | Asıl replik kaydı |
| 249–257 | 8,300–8,567 sn | Kısa kıkırdama/nefes vurgusu. Göz, yanak ve baş eşlik ediyor. | Aynı Raina dosyasının sonu |
| 282 | 9,400 sn | Ruj tabanı masaya oturuyor. | 451.200. örnek, 0 kare |
| 283–300 | 9,433–10,000 sn | Parmaklar ayrılıyor. Ruj masada, el başlangıç pozuna dönüyor. | — |

Çözülmüş miks tepesi **−6,38 dBFS**. MP4 baştan sona hatasız çözüldü.

| QA | Sonuç | Kanıt ve açık kalan nokta |
|---|---|---|
| VIS-01 | KISMİ | f18 ve f144 aynı yüz ve saç kaynaklarını kullanıyor. Tek 3/4 yüz varlığı kullanıldı. Ceket ve el çizgisi portreden daha düz. |
| VIS-02 | GEÇTİ | İki kadraj da onaylı master'ın aynı yerleşiminden. Sandalye, ayna ve masa konumları korunuyor. |
| ACT-01 | KISMİ | f144 tek kaş/yukarı bakış, f225 konuşma vurgusu, f252 göz kısma ve kısa gülüş. Kapak sıkışması ve bazı ağız şekilleri hâlâ keskin. |
| ACT-02 | KISMİ | Beden, baş ve ağız şekilleri arasında eğriler var. Kavramaya geçişte arka el çizimi değişimi f107–108'de fark edilebiliyor. |
| ACT-03 | KISMİ | f18/f43'te ayak basışı, ters kinematik ve kalça takibi var. Diz çizgileri ve ceket dirseği kesik parça hissi taşıyor. |
| PROP-01 | GEÇTİ | f110–116 kavrama ve alma, f282–300 bırakma. Hareketli ruj tek örnek ve geride sabit kopya kalmıyor. |
| PROP-02 | KISMİ | Başparmak önde, öbür parmaklar arkada. Masada hareketli temas gölgesi var. Yakında başparmak hacmi büyük kalıyor ve aynalarda hareketli karakter/ruj yansıması uygulanmadı. |
| SND-01 | GEÇTİ | Doğrulanmış Raina hazır sesi ve orijinal kayıt. |
| SND-02 | GEÇTİ | İki topuk ve iki masa/ruj teması kaydedilmiş foley ile işaretlendi. |
| SND-03 | GEÇTİ | Dört sesin çizelgeden sapması 0 kare. Görsel kavrama sınırı bir kare. |
| SND-04 | GEÇTİ | Raina ve foley tek MP4'te. Çözülmüş ses tepesinde klip yok. |
| EDI-01 | GEÇTİ | İki plan, 9:16. Geniş planda iki topuk görünür, yakın planda el ve ağız aynı kadrajda. |
| TECH-01 | GEÇTİ | Çalışan Godot sahnesi, düzenlenebilir parçalar, zamanlama ve miks komutu teslim edildi. |
| COST-01 | GEÇTİ | Tek Raina üretimi için 0,69 kredi onaylandı. Godot, foley ve kurgu ek ücret yaratmadı. |

Godot ve FFmpeg sahne ve ses zamanlaması için çalışıyor. Yayın kalitesine çıkmak için önce diz ve dirseği ağırlıklı mesh'e geçirmek, kavrama elini ara pozlarla düzeltmek ve Türkçe hece pozlarını elle inceltmek gerekiyor. Moho Smart Bones, bu üç düzeltmenin Godot'ta artan çizim yükünü azaltıp azaltmadığı karşılaştırılabilecek bir rig aracı. Lalin'in ticari Raina kullanım hakkı ayrıca doğrulanmayı bekliyor.

**DEVAM**
