# 05 — 2D yüz/beden oyunculuğu standardı

## Hedef
Lalin yalnızca konuşmamalı: **düşünmeli, tepki vermeli, gülmeli, objeyi gerçekten kavramalı ve ağırlığı olmalı**.

## Minimum oyunculuk repertuvarı
- Nötr/özgüvenli: kısa asimetrik yarım gülümseme, hafif yüksek çene.
- Alaycı: **tek kaş kalkar**, gözler yana kayar, dudak köşesi kıvrılır.
- Şaşırma: göz açılır, çene düşer, beden kısa süre donar.
- Öfke: kaşlar yaklaşır, üst beden gerilir, ağız sıkılır (bağırmak zorunda değil).
- Kahkaha: göz kapakları, yanak, ağız, kafa/omuz ritmi ve Raina kahkaha kaydı aynı performansı taşır.
- Göz devirmek: göz bebeklerinin yörüngesi + göz kapağı + kafa mikro tepkisi.
- Mahcubiyet/üzülme/düşünceli: yüz ve bedenin birlikte yumuşaması.

## Animasyon prensipleri
- İfadeler iki PNG arasında aniden değişmemeli; yüzün bir bölgesinden diğerine geçiş ritmi hissedilmeli.
- Kaş, göz, kapak, ağız, yanak, kafa pozisyonu kısmen bağımsız kontrol edilmeli.
- Göz hedefi (ayna, telefon, izleyici) fiziksel aksiyonla aynı yeri izlemeli; her kare kameraya bakmasın.
- Konuşma hecelerine yalnız çene değil yanak, nefes, el/baş, jest, küçük duraksamalar eşlik etmeli.
- Yürümede gövde ağırlık aktarımı, topuğun zemine basması, saç/çantanın gecikmeli hareketi.
- Prop tutma: uzanma → yaklaşma → temas → kavrama → el ile bir bütün gibi hareket → bırakma → yerleşme/sekme. Basit position tween yeterli değil.
- Çevre tepkisi: sandalye/ayna/telefon/ışık hareketleri karakteri takip etmeli.

## Üretim seçenekleri
A) Çizimi parçalayıp rig: uzun vadede yüz/nesne tutarlılığı yüksek; başlangıç varlık işçiliği çok.
B) Referans oyunculuk videosu → motion transfer AI: güçlü mimik potansiyeli; yüz, el ve prop kimlik kayması olabilir.
C) Hibrit: belirli mimik/eylem AI, düzenli konuşma/nesne/code scene Godot/2D rig, final sound/cut Remotion/FFmpeg.
**Karar önceden kilitlenmedi.** 5–12sn karşılaştırmalı kalite testi ile karar ver.

## Ret koşulları
- PNG'yi birkaç piksel salla; zoom yap; ağzı rastgele oynat = animasyon **DEĞİL**.
- Durağan foto + müzik veya sadece TTS lip sync = oyunculuk testinde **BAŞARISIZ**.
- Hand prop clip-through, kaybolan ruj, bozuk yansıma, değişen Lalin yüzü = videonun geçişi için kritik kusur.
