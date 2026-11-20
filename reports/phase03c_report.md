# Lalin · Faz 03C hibrit ruj testi

20 Kasım 2026 · [6,6 sn MP4](../outputs/phase03c/lalin_hybrid_lipstick_test.mp4) · [Gerçek kareler](../outputs/phase03c/lalin_kare_ornekleri.jpg)

[Plan 1 başlangıç](../outputs/phase03c/start_plan01.png) · [Plan 2 başlangıç](../outputs/phase03c/start_plan02.png) · [Plan 3 başlangıç](../outputs/phase03c/start_plan03.png)

İlk iki plan Swift ve Core Graphics ile yerelde hazırlandı. Yakın planlar, onaylı masanın lake ve pembe mermer dokusunu kullanıyor. Üç planda da oda master'ındaki aynı bordo-altın rujun ayrıştırılmış görseli var. El teması, başparmak önde ve diğer parmaklar arkada olacak biçimde çizildi. Altın saat ve rujun sağa eğik açısı kesmenin iki tarafında eşlendi. Üçüncü plan 01 numaralı onaylı karakter çizimini, eldeki aynı ruju ve yalnızca asıl rujun masadan temizlendiği oda plakasını kullanıyor.

Planlar **0,000–0,800 sn** tek ruj, **0,800–3,600 sn** kavrama ve kaldırma, **3,600–6,600 sn** elde ruj ve yüz oyunculuğu. Onaylanan **7,5 kredilik tek Wan 2.7** işi `51201ae2-e579-479b-851b-38f6a852eafb` tamamlandı. Kesinleşen kredi kesintisi MCP yanıtında görünmedi. FFmpeg, Wan videosunun yüz bölgesini yumuşak kenarlı maskeyle üçüncü plana ekledi. Elde tutuş ve oda, başlangıç kompozitinden sabit kaldı. Çıktı **1080×1920, 30 fps, 198 kare**, H.264 ve 48 kHz AAC. Sahne diyalogsuz. [Yerel yakın plan kaynağı](../src/phase03c/pickup.swift) · [Üçüncü plan ve maske](../src/phase03a/start_frame.swift) · [Birleştirme komutu](../src/phase03c/assemble.sh)

## Görsel ve ses kontrolü

198 kare sıralı önizlemelerde tarandı. Temas, masadan ayrılma, plan kesmeleri ve yüz bölgesi büyütülerek ayrıca incelendi.

| Kontrol | Sonuç | Kanıt |
|---|---|---|
| Tek ruj ve dekor | GEÇTİ | f000'de masadaki kapalı ruj f055'te kavranıyor. f065'te masa yüzeyinden ayrılıyor. f107'de kaldırılmış tüp ile f108'de Lalin'in elindeki tüp aynı bordo kapak, altın şerit ve eğime sahip. Masada kopya görünmüyor. Üçüncü planda kitap ve tutuş bölgeleri f108 ve f193'te piksel düzeyinde eşleşti. [Masada f000](../outputs/phase03c/frames/f000.png) · [Kaldırma f084](../outputs/phase03c/frames/f084.png) · [Kesme f107](../outputs/phase03c/frames/f107.png) · [Kesme f108](../outputs/phase03c/frames/f108.png) |
| El ve temas | KISMİ | f055'te başparmak öne geçiyor. Diğer parmaklar arkada kapanıyor ve ruj kavramayla birlikte kalkıyor. Yerel elin ve saatin gölge geçişleri özgün Lalin çiziminden daha düz. Küçük kaynak ruj dokusu yakın planda yumuşak. [Temas f055](../outputs/phase03c/frames/f055.png) |
| Yüz ve oyunculuk | KISMİ | f118–132'de dudak köşesi yükseliyor, f188 civarında göz kapağı kapanıp açılıyor. Yüz kimliği ve çizgi korunuyor. f149–177'de gözler bir miktar fazla açılıyor ve bakış yukarı kayıyor. Baş ve saç hareketi sınırlı. [Küçük gülümseme f193](../outputs/phase03c/frames/f193.png) |
| Foley | GEÇTİ | Gerçek masa üstü alma kaydı başparmak temasına, f55 yani 1,833 sn'ye yerleştirildi. 48 kHz'e çözülen MP4'te referans dalga biçimi 88.000. örneğe düştü. Sapma **0 kare**, tepe **−17,05 dBFS**. [Foley kaynağı](../src/phase02/audio/manifest.json) · [Olay çizelgesi](../src/phase03c/events.json) |

**NESNE SÜREKLİLİĞİ GEÇTİ · OYUNCULUK KISMİ**
