# 03 — Ana oda: canlı, etkileşimli giyinme/makyaj seti

## Kesin onaylı referans
`assets/environment/APPROVED_lalin_room_master.png` (1672×941, yatay). **Kaynak görsel tek parça**; bu otomatik olarak hareket edebilir katmanlar içerdiği anlamına gelmez.

İşaretleme/konum planı yalnız rehber: `assets/environment/room_zones_approx_NOT_MASTER.jpg`.

## Değişmeyecek atmosfer ve yerleşim
- Canlı pembe duvarlar ve koltuk, bordo perde/koltuk, altın aydınlatmalar/kenarlık, sıcak krem mobilyalar.
- Sol tarafta kıyafet dolabı ve çantalar/ayakkabılar.
- Arka tarafta büyük pencere ve Boğaz/İstanbul esinli şehir/su manzarası.
- Işıklı büyük makyaj aynası, sağ tarafta makyaj masası, parfümler, fırçalar ve kozmetikler.
- Canlı/kişisel dekor: `Lalin` neon tabela, çiçekler, yeşil bitkiler, küçük notlar/kitaplar.
- Telefon, bardak/kozmetik ürünleri, sandalye, yastıklar ve **uyuyan beyaz kedi**.
- Odada lüks, genç kadın enerjisi ve sıcaklık. Soluk, yalnız krem rengine dönmeyen canlı set.

## Sahne animasyon potansiyeli
| Bölge | Varlık | Bağımsız olabilecek hareket |
|---|---|---|
| Zemin | topuk temas noktaları | adım/zemin gölgesi/gerçek foley |
| Dolap | kapak, askı, kıyafet, çanta | açma, alma, sallanma, giyinme |
| Makyaj masası | ruj, kutu, fırça, telefon | tutma, açma, sürme, bırakma, titreşim |
| Ayna | ışık, refleksiyon | açma/kısma, karakterin hareketiyle uyumlu yansıma |
| Dekor | perde, yaprak, çiçek | küçük ikincil doğal hareketler |
| Oturma grubu | sandalye, koltuk, yastık | oturma ve fiziksel temas |
| Kedi | kafa, beden, kuyruk, göz | uyku nefesi, uyanma, esneme/tepki |

## Katman planı / kompozit
Önerilen derinlik: `background city` → `walls + rear furniture` → `mid props` → `Lalin` → `hand-held props` → `foreground` → `lighting/shadows`.
- Statik tek görselden **nesnenin altındaki gerçek zemini bilmek mümkün değildir**. Inpaint/paint-over ile temiz `clean plate` gerekebilir.
- Bir nesne masadan alındığında aynı nesne masadan kaybolmalı. Elin ön/arka örtüşmesi maskeyle doğru çalışmalı.
- Aynadaki yansıma karakter hareketleriyle uyumlu olmalı; ilk prototipte gerçek simülasyon çok maliyetli ise shot composition ile çözüm öner.
- 9:16'ya geçerken **yatay ana görseli ezip uzatma veya yalnız otomatik center crop'a güvenme**. Her shot için yeniden kompozisyon, gerekirse kontrollü genişletme. Odanın sol-sağ mekânsal mantığı değişmesin.
- Dışarıdan görüntüde gerçek İstanbul olduğu iddia edilmez; stilize Boğaz hissi yeterli.

## Kabul şartı
Objelerin ekranda hareket etmesi tek başına yetmez: gerçekten alınabilir, bırakılabilir, kapak açılabilir, temasa tepki verebilir ve ses olaylarına bağlı olmalıdır. Başarılı örnek tek bir nesneyle dahi başlayabilir; hepsini ilk pilotta animasyon yapmak zorunlu değil.
