# 09 — Kısa üretim akışı, onay kapıları ve ölçeklenme

## İş bölümü
- **ChatGPT:** Prodüktör/yaratıcı yönetmen; senaryo, kanon, araç kıyaslaması, geri bildirim, görevler.
- **Codex:** Kod/kurgu/rig pipeline, sahne oluşturma, animasyon prototipi, ses eşleme, QA raporu.
- **Kullanıcı:** Yaratıcı onay, Raina ses üretimi ve maliyet onayı, Instagram operasyonu.

## Kapılar
**G0 Varlık ve hak envanteri → G1 Yöntem kararı → G2 8–12sn oyunculuk prototipi → G3 Kalite incelemesi → G4 İlk gerçek pilot bölüm.**
Büyük seri üretim, yan karakterler, çoklu mekanlar, otomatik yayın G3 öncesi kapsam dışı.

## Beklenen çıktı klasörleri
- `assets/` kaynaklar + hazırlanmış ve **etiketlenmiş** katmanlar.
- `src/` çalışır, sürümlenebilir kod ve editlenebilir animasyon projeleri.
- `outputs/phase01/` test renderları.
- `reports/` teknik karar, skor tablosu, kalite, maliyet, olay zaman çizelgesi.
- `prompts/` kullanılan promptlar (değişiklikleri kaydet).

## Teknik kayıtlar
Her üretimde: `date`, `tools & versions`, `input hashes`, `seed if available`, `duration/fps/resolution`, `credits/cost`, `known defects`, `approval status`.

## Dikkat
- Projede ürün yerleştirme/işbirliği ileride yapılabilir; ilan/reklam işaretleme ve ticari ses/müzik/karakter lisansını yayından önce ayrıca gözden geçir.
- Açıkça izin alınmamış ünlü repliklerini, üçüncü taraf karakterleri, müziği birebir kopyalama.
- Raina sesinin uzun vadeli erişimi ayrı bir takip konusu; pilotu geciktirmesin ama lisansı varmış gibi iddia edilmesin.
- Türkçe özgün mizah en önemli ölçütlerden. Çocuk dizisi gibi fazla swoosh/pop efekti kullanma.
