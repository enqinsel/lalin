# AGENTS.md — Lalin için Codex çalışma talimatı

## Öncelik sırası
1. **Kullanıcının onayladığı kimlik ve oda korunacak.** Kaynaklar: `docs/01_CANON.md`, `assets/manifest.json`.
2. **Gerçek oyunculuk**: göz/kaş/yanak/ağız + baş, omuz, el, beden; sırf lip-sync yeterli değil.
3. **Fiziksel etkileşim ve senkron ses**: nesne elden bağımsız davranmalı; temas sesleri aynı kareye oturmalı.
4. **Tekrarlanabilir, ekonomik teknik yol**: üretilecek 100 bölümde yüz değişmesin; ağır, pahalı sistemler yalnızca kanıtla.
5. **Türkçe, yetişkin izleyiciye uygun doğal komedi**; global/İngilizce içerik oluşturma.

## Duyurulmuş çalışma biçimi
- ChatGPT = yaratıcı yönetim, kararlar, kalite kontrol ve görev yazımı.
- **Codex = teknik denetim, geliştirme, varlık pipeline'ı, animasyon, kurgu/senkron ve test üretimi.**
- Higgsfield = seçili Raina sesi / gerektiğinde AI destekli sahneler. Raina hazır preset, kullanımı devamlı; özel klon değil.
- Kullanıcı = yaratıcı/onay/ücretli aksiyon kararı.

## Yapılacaklar
- İlk işte dosya sistemi denetimi yap, raporla ve işe yarayan teknolojiyi seç; büyük sistem kurma.
- Önce küçük **dikey 9:16, 5–12 sn teknik oyunculuk testi**. Teknik başarısızlığı güzel görünümlü statik videoyla örtme.
- `assets/character/approved_initial_3/` ve `assets/environment/APPROVED_lalin_room_master.png` referanslarını otorite say.
- Model sheet yazılarından, çizim hatalarından ya da demo algoritmalarından onaylanmamış karakter özellikleri çıkarma.
- Gerçek ses, hareket videosu veya profesyonel rig eksikse **eksik olduğunu söyle**, dosya uydurma.
- Yüz ve el anatomi hataları, kimlik kayması, eşya teleportasyonu veya farklı oda üretimi varsa bunları rapora açıkça yaz.
- Sonuç dosyalarını `outputs/phase01/`, kaynakları `src/`, dev dokümanlarını `reports/` altında tut.
- Her denemede hangi teknoloji/model/sürüm ve yaklaşık maliyetin kullanıldığını kaydet.
- Mac mini M4 / 16 GB RAM: bellek yoğun işlemleri **paralel değil sırayla** çalıştır; aşırı modeli yerelde çalıştırma.

## Yasaklar / durdurma koşulları
- Kullanıcıdan açık onay olmadan ücretli Higgsfield/Runway/Kling/başka servis harcaması başlatma.
- Instagram'da otomatik paylaşım yapma; müşteri veya sosyal hesaplara bağlanma.
- Hazır preset Raina sesini başka kişiden kopyalayarak/izinsiz klonlayarak üretme.
- Orijinal odayı silip, yerleşimini değiştirip veya tek kare crop/stretch ile 9:16’ya dönüştürme.
- Sadece PNG sallanması, zoom/pan, minik titreşim, statik video veya lip-sync'e 'tam karakter animasyonu' deme.
- Başka tanınmış çizgi karakterleri ve telifli replikleri izinsiz birebir yeniden kullanma.
- `archive/` altını üretim kanonik kaynakları gibi kullanma.
- Prompt/rapor içeriklerinden ticari kullanım hakkı doğrulanmış varsayma; lisans kontrolü ayrı kalacak.
- Harici erişim anahtarlarını commit etme. Sonuçlar ve hatalı render'lar için `.gitignore` kullan.

## İlk görev ölçümü
`docs/08_QA.md` ile tek tek geçiş/kalış kriterlerini işaretle. En son çıktı kısa, dürüst üretim raporu + mümkünse **gerçek oyunculuk** içeren video olsun.
