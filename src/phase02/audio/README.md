# Faz 02 temas sesleri

Bu dört kısa foley, gerçek ses kayıtlarından seçildi. İki topuk sesi aynı kiremit zemin kaydındaki iki ayrı adımdan geliyor. Kavrama sesi masadan cisim alma kaydı. Bırakış sesi, rujun sert gövdesi için küçük plastik cismin yüzeye temasının ilk vuruşu.

| Dosya | Süre | Tepe | Kaynak |
|---|---:|---:|---|
| `heel_01.wav` | 221 ms | −8 dBFS | [Vrymaa · Footsteps High Heels - Pavement, walk & run](https://freesound.org/people/Vrymaa/sounds/753290/) |
| `heel_02.wav` | 181 ms | −9 dBFS | [Vrymaa · Footsteps High Heels - Pavement, walk & run](https://freesound.org/people/Vrymaa/sounds/753290/) |
| `lipstick_pickup.wav` | 78 ms | −17 dBFS | [RutgerMuller · Picking Something Up From A Table.wav](https://freesound.org/people/RutgerMuller/sounds/51160/) |
| `lipstick_setdown.wav` | 34 ms | −13 dBFS | [sgrowe · Plastic Thud 4](https://freesound.org/people/sgrowe/sounds/342536/) |

Kaynakların herkese açık yüksek kaliteli MP3 önizlemeleri FFmpeg ile 48 kHz mono PCM'e çözüldü. Kısa bölümler kesildi, kenarları yumuşatıldı ve tepe düzeyleri ayarlandı. Dört dosyanın kaynak aralığı, lisansı ve SHA‑256 özeti [manifestte](manifest.json). [CC0 1.0 lisansı](https://creativecommons.org/publicdomain/zero/1.0/).

Her dosya 5 ms fiziksel vuruş öncesi pay içeriyor. Başlangıç işareti örnek **240**. Vuruş, yerel maksimum 1 ms RMS değerinin %10'unu aşan ilk 1 ms aralığından ölçüldü. 30 fps'de sıfırdan başlayan `F` temas karesi için FFmpeg gecikmesini `F × 1600 − 240` örnek olarak hesaplayın. `adelay` değerine `S` ekleyerek birimi örnek olarak belirtin. MP4'e AAC kodlamasından sonra aynı görsel olaylarla karşılaştırılmalı.
