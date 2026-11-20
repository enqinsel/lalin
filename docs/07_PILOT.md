# 07 — Pilot 01: Lalin Canlanıyor (oyunculuk kanıtı)

**Amaç:** İlk defa Lalin'i gerçek yüz/beden/prop oyunculuğu ve kadrajla birlikte görmek. Bu bir final Instagram bölümü değil, teknik kalitenin dürüst kanıtı.

**Format:** Dikey 9:16; 30 fps; ilk gösterim mümkünse 1080×1920 (hızlı araştırma preview'su daha düşük olabilir). Hedef **8–12 sn**, gereği varsa en fazla 15 sn.

## Ana test senaryosu (oynanabilir kısım)
- **0–2 s:** Lalin odada sert zeminde **iki belirgin topuk adımı** ile aynaya doğru ilerler. Ayak tabanı/gölge/foley senkron.
- **2–4 s:** Makyaj masasındaki ruja uzanır, doğru kavrar ve eline alır. Ruj masadan kaybolur; el/ruj/ayna ve gölge tutarlı.
- **4–6 s:** Aynaya bakarken hafif kendinden emin gülümseme → tek kaş yükselir → göz devrilir. Sabit ifadenin değişimi seyirci tarafından anlaşılır.
- **6–10 s:** Lalin, **Raina** sesiyle `Ben senin fikrini değil, ışığını sordum.` der. Lafı söylerken kaş/göz/yanak/çene ve baş-el jestleri oynar.
- **10–12 s:** Yarım gülüş, kısa nefes/isteğe bağlı kahkaha; rujun kontrolsüz biçimde kaybolmaması ve set tutarlılığı.

Bu sahne eskiden konuşulan **'ayna ile tartışma'** fikrinden alınmıştır. Henüz aynanın ikinci sesi seçilmediği için ilk **oyunculuk prototipinde aynaya ayrı diyalog zorunlu değil**. Sonraki yayın bölümünde `Bu kombini dün de giymiştin.` ayna repliği eklenebilir; ayrı ses ve yeni onay gerekir.

## Ses girdisi
- `assets/voice/raina_test.wav` veya `assets/voice/raina_test.mp3` beklenir.
- Kullanıcının mevcut Raina testi farklı uzun metinse pilot repliğini kullanıcı Higgsfield'da tekrar üretebilir. **Düzleştirilmiş taklit sesi kullanma**.
- Ses dosyası yoksa sessiz performance block ve ses zamanlama taslağı çıkartılabilir; **lip-sync tamamlandı** diye raporlama.

## Başarılı testte aradığımız
1. Önce/sonra gerçekten ayırt edilebilen yüz oyunculuğu.
2. İki adımda ayak-zemin temasları + eş zamanlı iki topuk sesi.
3. Tek prop etkileşimi: el kavrar, obje ortamdan kalkar, doğal şekilde elde kalır.
4. Lalin yüzü, saç, oda kimliği kareler boyunca sabit.
5. Tüm bunların planlanmış kamera/kurgu ile yetişkin çizgi komedi tonunda görünmesi.

## Yan yol / dürüst fallback
Bazı girdi/teknoloji eksikleri nedeniyle yukarıdakilerin hepsi yapılıyorsa abartılmış, kalitesiz sahte video üretme. Bunun yerine **konuşma/mimik 5 sn**, **prop 3 sn** gibi iki küçük gerçek test hazırlayıp eksikleri yaz. Bir sonraki net girdiyi iste.

## Teslim dosyaları
- `outputs/phase01/lalin_acting_test.mp4` (yapıldıysa, kesin dosya yolu)
- `reports/phase01_report.md`: teknoloji/sürüm, gerçekten yapılanlar, yapılamayanlar, hata notları, maliyet ve QA.
- `reports/phase01_event_timing.csv`: kare numarası / eylem / SFX girişi / gözlem.
- Çalışabilir kaynak projesi `src/` altında, dış bağımlılık/kurulum README'siyle.
