# Lalin · Faz 01 üretim raporu

20 Kasım 2026

Tam 8–12 saniyelik ayna pilotu, mevcut varlıklarla doğrulanamadı. İki küçük teknik kanıt üretildi. İlki onaylı Lalin çiziminden yüz ve baş oyunculuğunu, ikincisi tek bir rujun kavranmasını ve elden ayrıldıktan sonra masaya oturmasını gösteriyor. İkisi de **540×960, 9:16, 30 fps**. Harici servis harcaması **0 USD**.

| Çıktı | Kanıt |
|---|---|
| [Mimik testi](../outputs/phase01/lalin_face_test.mp4) · 5 sn | Tek kaş, yana ve yukarı bakış, göz kırpma, şaşırma, iki vuruşlu sessiz kahkaha. Göz kapağı, iris, kaş, yanak, ağız ve baş ayrı kontrol ediliyor. Omuz kahkahaya eşlik ediyor. |
| [Ruj temas testi](../outputs/phase01/lalin_prop_test.mp4) · 3 sn | Şematik test eli ruju kavrıyor, kaldırıyor ve bırakıyor. Tek ruj, yalnızca kavrama sırasında ele bağlı. Serbest düşüş, temas, küçük sekme ve yerleşme ayrı görülüyor. İki geçici sentetik klik var. |
| [Kaynak ve render komutları](../src/phase01/README.md) · [Kare/olay çizelgesi](phase01_event_timing.csv) | Mimik için Python 3.9.6, Pillow 11.3.0, NumPy 2.0.2 ve SciPy 1.13.1. Nesne için Swift 6.4 ve Core Graphics. İki MP4 için FFmpeg 9.0.2. |

## Varlık denetimi

- Manifestteki yedi girdinin boyutu, piksel ölçüleri ve SHA-256 özeti eşleşti. Altı çizim 8 bit, tek katmanlı RGB PNG. Raina seçim ekranı RGBA PNG. Onaylı ilk üç karakter çizimi ve 1672×941 oda master'ı okundu. İki yardımcı model sheet'in yazıları ve oranları üretim verisine alınmadı.
- İlk çizimde bacaklar çapraz, kol ve el gövdeyle temas halinde, topuk ve zemin gölgesi çizime işlenmiş. Diğer iki onaylı paftanın ifadeleri farklı açı ve ışıkta çizilmiş. Mimikte **02 paftasının büyük portresi** sabit kimlik kaynağı olarak kullanıldı. Hareketli iris ve kapanan kirpik çizgisi bu portreye göre çizildi, ağız içi açılma sırasında ayrı işlendi. Başka ifadeye veya yüze geçiş yapılmadı.
- Oda master'ında dolap solda, pencere arkada, ayna ve makyaj masası sağda. Masa örtüşmeleri, ruj ve gölgeler tek görsele işlenmiş. Ortada halı var ve sert zemin hattı sandalyenin arkasında daralıyor. Oda entegrasyonu için bu yerleşimi koruyan ayrı dikey çekim kompozisyonu gerekir. Ruj klibindeki şematik masa bir test yüzeyi. Kanonik oda iki klibe de kompoze edilmedi.
- Üretim girdileri olarak gerçek `raina_test.wav` / `.mp3` veya pilot repliğinin kaydı, ayrı kahkaha/nefes, katmanlı vücut ve el rig'i, driving video, temiz dikey oda plakası, ayrı ruj ve kayıtlı topuk/ruj foley'si eksik. Arşivdeki eski render ve temiz plaka üretim girdisine alınmadı.

## Teknik karar

Yüz, el/nesne ve süreklilik değerlendirmeleri eldeki kaynakların sınırları ile araçların belgelenmiş yeteneklerine dayanıyor. Tablodaki adaylar için servis çağrısı veya kurulum yapılmadı. Fiyatlar 20 Kasım 2026 tarihli açık liste fiyatları.

| Yöntem | Mimik | El ve nesne | Süreklilik | İşçilik | Yaklaşık maliyet | Yerel uyum ve karar |
|---|---|---|---|---|---|---|
| Godot 4.7.2, 2D iskelet ve ağırlıklı mesh | Katmanlı çizimle yüksek kontrol | Poz, temas, gölge ve örtüşme kare bazında | Yüksek. Aynı rig ve oda katmanları yeniden kullanılır. | İlk rig ve temiz katman çizimi gerekir | 0 USD, MIT | Apple Silicon sürümü var. Rig hazır olduğunda ana sahne için tercih. [Sürüm](https://godotengine.org/download/archive/) · [2D iskelet](https://docs.godotengine.org/en/4.7/tutorials/animation/2d_skeletons.html) · [Lisans](https://godotengine.org/license/) |
| Moho 14 / Live2D Cubism 5.3 | Güçlü deformasyon ve yüz parametreleri | Moho iskelet ve el pozları için uygun. Live2D'de yürüyüş, el ve prop için ek sahne işçiliği var. | Tek rig ile yüksek | Temiz ve ayrık çizimler iki araçta da gerekli | Moho Pro 399,99 USD, Debut 59,99 USD tek sefer. Live2D Free sınırlı. Uygun Indie Pro 2.080 JPY/ay. | İki araç da Apple Silicon destekli. İlk faz için gerekli değiller. [Moho fiyatları ve uyum](https://moho.lostmarble.com/pages/buy) · [Live2D editör](https://www.live2d.com/en/cubism/download/editor/) · [Live2D fiyatları](https://store.live2d.com/en/) |
| Remotion / FFmpeg | Yüz hareketini oluşturmak için çizim ve hareket kontrolü gerekir | Kare ve ses düzenleme için yüksek kontrol | Render ve zamanlama tekrarlanabilir | FFmpeg ile az. Remotion için React kompozisyonu gerekir. | FFmpeg açık kaynak. Remotion bireyler ve en fazla üç kişilik şirketler için ücretsiz. | Kurulu FFmpeg kullanıldı. [FFmpeg lisansı](https://ffmpeg.org/legal.html) · [Remotion lisansı](https://www.remotion.dev/docs/license/pricing) |
| Higgsfield Genjutsu Motion Transfer v1.0 | Driving video ile yüz ve jest aktarımı denenebilir | El, ruj, ayna ve temas kareleri için sonuç doğrulanmalı | Onaylı Lalin ve oda sürekliliği bu varlıklarla doğrulanmadı | Pilot için özel 4–30 sn hareket kaydı, referans ve çıktı QA'sı | Açık API fiyatıyla 8–12 sn yaklaşık 2,76–4,14 USD (720p), 6,68–10,02 USD (1080p). Web kredi bedeli ayrı. | Bulutta çalışır. Özel driving video ve harcama onayı sonrası karşılaştırmalı test adayı. [Ürün rehberi](https://higgsfield.ai/blog/higgsfield-genjutsu) · [API fiyatı](https://open.higgsfield.ai/models/higgsfield/genjutsu/motion-transfer/v1.0/playground) |

**Seçim:** Bu fazda yerel, elle zamanlanmış iki dar test ve FFmpeg. Bir sonraki aşamada katmanlı 2D rig ve sahne için Godot, miks ve MP4 için FFmpeg. Tek portreye bağlı yüz deformasyonu, mimik ritmini kanıtlıyor. Çok açılı yüz, yürüme ve el anatomisi ayrı katman ve poz çizimleri gerektiriyor.

## Kare ve ses kontrolü

MP4'lerden çözülen **150 mimik karesi ve 90 nesne karesi** sırayla tarandı. Göz kırpma ve ağız açılma kareleri ile kavrama ve masa teması çevresi ayrıca büyütüldü. Aşağıda kareler sıfırdan başlıyor.

- Mimik f27'de kaş ve yan bakış, f49–56'da yukarı giden irisler, f68'de kırpma, f79'da şaşırma, f114 ve f127'de kahkaha zirveleri görülüyor. Büyük ağız açılışında iç ağız ve kapalı kapakta kirpik çizgisi stilize. El, tam vücut, sesli kahkaha, Türkçe ağız eşlemesi ve farklı açılarda yüz sürekliliği sınanmadı.
- Ruj f18'de başparmağa temas ediyor, f21'de tutuş tamamlanıyor, f26'da masadan ayrılıyor. f60'ta eldeki bağ kalkıyor, f63'te masa teması var, f65'te küçük sekme ve f67'de duruş görülüyor. Parmak örtüşmesi ve temas gölgesi şematik çizimle çözüldü. Parmak anatomisi ve ışık, Lalin'in onaylı odasında doğrulanmadı.
- 48 kHz'e çözülen MP4 sesinde, mutlak genliği 0,02'yi aşan ilk örnek ve yerel tepe f18 için **28.800**, f63 için **100.800**. Sapma iki temas için de **0 kare**. Klip tepesi **−8,67 dBFS**. Bunlar iki ruj teması için sentetik senkron işaretleri. Topuk foley'si, oda ambiyansı ve diyalog miksajı sınanmadı.

| QA | Sonuç | Kanıt ve sınır |
|---|---|---|
| VIS-01 | KISMİ | Mimik f0, f27, f79 ve f114 aynı portreden. Saç çizgisi, göz şekli, ben ve aksesuarlar okunuyor. Çok açılı kimlik sınanmadı. |
| VIS-02 | UYGULANMADI | Onaylı oda master'ı denetlendi. Pilot kadrajına entegrasyon yapılmadı. |
| ACT-01 | GEÇTİ | f27 alaycı bakış, f79 şaşırma, f114 kahkaha. Kaş, göz, ağız ve yanak hareketleri ayrı. |
| ACT-02 | GEÇTİ | f41–79 ve f90–136 geçişlerinde aynı kaynak üzerinde kademeli deformasyon. Ani poz değişimi gözlenmedi. |
| ACT-03 | KISMİ | f107–127'de baş ve omuz kahkaha jesti. Topuk adımları, vücut ağırlığı ve Lalin'in el jesti sınanmadı. |
| PROP-01 | KISMİ | Şematik provada f18–67 kavrama, kaldırma, serbest düşüş ve bırakış var. Aynı ruj tek yerde. Pilot eli ve makyaj masası bekliyor. |
| PROP-02 | KISMİ | f21 ve f43'te başparmak önde, diğer parmaklar arkada. Gölge yükseklikle değişiyor. Oda ışığı ve yansıma sınanmadı. |
| SND-01 | UYGULANMADI | Raina kaydı eksik. |
| SND-02 | KISMİ | Ruj provasında f18 ve f63'te duyulur geçici klikler. Topuk ve gerçek malzeme foley'si yok. |
| SND-03 | KISMİ | Ruj provasında 0 kare sapma. Topuk ve diyalog süreleri sınanmadı. |
| SND-04 | UYGULANMADI | Yalnız ruj kliki kanalı ölçüldü. Diyalog miksajı yok. |
| EDI-01 | KISMİ | İki klip 9:16. Onaylı odanın dikey kompozisyonu hazırlanmadı. |
| TECH-01 | GEÇTİ | Her iki kaynak ve render komutları teslim edildi. Aynı makinede ikinci renderlar bayt düzeyinde eşleşti. |
| COST-01 | GEÇTİ | Yerel araçlar kullanıldı. Harici servis harcaması 0 USD. |

## Pilota geçiş

İlk girdi, **“Ben senin fikrini değil, ışığını sordum.”** repliğinin orijinal Raina çıktısı `assets/voice/raina_pilot_line.wav`. Tercihen 48 kHz WAV. Yanına kısa kahkaha/nefes alınırsa son vuruş sesle eşlenebilir. Görsel tarafta öncelik, uzanma/kavrama pozları ve iki topuk adımı için ayrık bacak, ayakkabı ve el katmanları ile aynı makyaj masasının temiz plakası ve ayrık ruj. Böylece mevcut yerleşim korunarak önce 0–4 saniyedeki adım ve kavrama doğrulanır, sonra replik ve yüz oyunculuğu aynı çekime bağlanır. Driving video yalnız hareket aktarımı adayı için gerekli.

**EKSİK GİRDİ BEKLENİYOR**
