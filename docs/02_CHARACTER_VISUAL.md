# 02 — Lalin görsel tasarım ve karakter varlıkları

## Kullanılacak görseller (önem sırası)
1. `assets/character/approved_initial_3/01_lalin_full_body_primary.png`
2. `assets/character/approved_initial_3/02_lalin_expressions_fashion.png`
3. `assets/character/approved_initial_3/03_lalin_expressions_turnaround.png`
4. `assets/character/additional_concepts/*.png` → **yalnız destekleyici konsept**, hiçbir yazısı/ölçüsü güvenilir rig verisi değil.

## Tasarım kilidi
- Profilde de önden de aynı yüz: göz şekli/badem göz, kaş yüksekliği ve kalınlığı, burun, elmacık, dudak formu, ben, saç çizgisi.
- Yüz çizimlerinde karakteri koruyarak **ifade aralığını artır**. Her ifadede yepyeni bir kadın çizme.
- Güzel ve şık ama karakteristik; göz devirme, alaycı kaş, yan gülüş, abartılı kahkaha imza.
- Yetişkin görsel dil, çok çocuk/çibi tasarımı değil; ileri seviye çizgi oyunculuk.
- Vücut oranı her sahnede aynı, rig yeniden kullanılabilir, kıyafet ayrı değiştirilebilir.
- Saçın doğal temel dokusu **uzun düz koyu kahve**; bölüm içinde topuz, dalga, boyama olabilir ancak saç hacmi, yüz kenarı ve doğal fizik tutarlı.
- Aksesuarlar o bölümde fiziksel olarak giyilmişse görünür ve doğru hareket eden ayrı katmanlar olabilir.

## Teknik gereklilik (profesyonel rig için)
- Front, 3/4 ve profil görünüm için onay alınacak bir **turnaround**.
- Göz (L/R), üst/alt göz kapağı, göz bebekleri, kaşlar, yanak, çene, dudak/ağız, baş-boyun, omuz, el ve saç kütleleri ayrı deformasyon kontrolleri.
- Ağız/viseme seti Türkçe için sesle uyarlanmalı (TTS fonetik doğruluğu test edilecek).
- El/kol rig'inde tutma/açma/uzanma ve arada poz geçişleri.
- Katmanlardaki maskeler yalnız görsel yama değil, göz/saç/çene konturlarına uygun olmalı.
- Karakterin odaya entegrasyonunda kat planı, gölge, zemin teması, perspektif ve nesne örtülmesi.

## Testte kaçınılacak kusurlar
- Görselde var ama katmanlanamayan ellerin kopması, yüzün yapısının aniden değişmesi, gözler kayarken iris sabit kalması, saçın kopyalanmış gibi görünmesi.
- Yapay animasyon: yalnız yakınlaştırma/kaydırma, kısıtlı bir iki kare ağzın açılması, tek parçalı yüz deforme etme.

## Üretim tamamlanma ölçütü
Temel nötr poz ve güçlü alaycı/şaşkın/kahkaha ifadelerinde **aynı Lalin**. Bunları gösteren düşük maliyetli bir pose sheet/rig testi yapılabilir; kullanıcı onayı olmadan kalıcı tasarım değişikliği yapılmasın.
