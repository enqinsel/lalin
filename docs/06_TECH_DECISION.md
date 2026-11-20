# 06 — Teknik yol araştırma ve seçim şablonu

## Amaç
**Önce kalite kanıtı, sonra uzun vadeli pipeline.** Kullanıcının Mac mini M4 / 16GB RAM ortamı ve düşük maliyet ihtiyacı dikkate alınmalı.

## Adaylar (karar değil)
| Yol | Güçlü tarafı | Risk/eksik |
|---|---|---|
| Godot 2D skeleton/cutout | Kontrol edilebilir sahne/prop/trigger, ücretsiz; Kodlanabilir | Profesyonel katmanlı karakter rig'i/ressamlık gerekir |
| Live2D Cubism / Moho | Güçlü ifadeler ve deformasyon / elle oyunculuk | Lisans, öğrenme eğrisi, frame/rig emek ihtiyacı |
| Remotion / FFmpeg | Kurguda deterministik frame kontrolü, ses/miks otomasyonu | Tek başına yüz/beden 'oyunculuk motoru' değil |
| Higgsfield Genjutsu motion transfer | Referans oyunculuk videosundan jest/yüz aktarımı potansiyeli | **Referans karakter görseli + gerçek driving video** gerekir; maliyet ve tutarlılık değişken |
| Kling / diğer video modelleri | Hareketli sinematik testler | Frame bazlı prop/kimlik/çoklu bölüm kontrolü garanti değil |
| Blender Grease Pencil / OpenToonz | 2D/2.5D profesyonel hareket | Art/rig ve kurgu emeği, ağır olabilir |

## Karar vermek için Codex'in denetimi
1. Kaynaklar: 3 onaylı Lalin görüntüsü, onaylı oda **raster** mi, gerçek katman var mı? Raina `.wav` var mı? Driving video var mı?
2. 2–3 yöntem için **yüz, el, prop, set tutarlılığı, tekrar kullanma, yerel performans, servis maliyeti** puanlarını raporla.
3. Katmanlı hareket için kullanılabilir gerçek rig yoksa bunu açıkla, otomatik screenshot maskesini bitmiş varlık gibi gösterme.
4. Genjutsu için driving video yoksa kaynak üretim ihtiyacını bildir, motion transfer tamamlandı deme.
5. Ücretli servis maliyeti ve hangi hak/girdi gereklilikleri olduğunu **harcama öncesi** göster. Kullanıcı onayı olmadan çalıştırma.
6. Önce `docs/07_PILOT.md`'deki küçük prototipi geç; sonra büyük pipeline / SaaS / render farm kur.

## İstenen kısa rapor tablosu
`Yöntem | Mimık kalitesi | El/prop | Süreklilik | İşçilik | Yaklaşık maliyet | Yerel uyum | Karar`

## Yerel kaynak kuralı
FFmpeg/render, ses analizi ve ağır AI modellerini 16 GB makinede aynı anda çalıştırma. Makineyi kilitleyecek lokal video modelinden kaçın. Dış servis gerekiyorsa yalnız maliyet/izin sonrası çağır.

## Not
Fiyat ve model özellikleri hızla değişebilir; buradaki adlar **teknoloji adaylarıdır**, güncel sürüm/ücret/doğruluk Codex tarafından çalışma anında doğrulanmalıdır.
