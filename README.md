# LALİN — Codex Başlangıç Paketi v1.0

**Proje / Instagram:** `@lalinsahnede`  
**Tarih:** 20 Kasım 2026  
**Ana karakter:** Lalin, 30 yaşında; Türkçe/Türkiye odaklı animasyon komedi + stil/kozmetik.

## Bu paket ne için?
Codex'in sıfırdan varsayım yapmadan, onaylı karakter/oda görsellerine ve üretim kurallarına göre **kaliteli bir oyunculuk prototipi için doğru teknik yolu seçmesi** amacıyla hazırlanmıştır. Kalıcı render pipeline veya tam animasyon sistemi henüz kurulmuş değildir.

## Başlama sırası
1. `AGENTS.md` → çalışma kuralları ve yetki sınırları.
2. `docs/01_CANON.md` → asla yanlış anlaşılmaması gereken proje kararları.
3. `docs/02_CHARACTER_VISUAL.md`, `docs/03_ROOM.md`, `docs/04_VOICE_SOUND.md`, `docs/05_ACTING.md` → görsel/oyunculuk/ses standartları.
4. `docs/06_TECH_DECISION.md`, `docs/07_PILOT.md`, `docs/08_QA.md` → teknik karar/test/teslim.
5. `assets/manifest.json` → görsellerin kökeni, statüsü ve SHA256 bilgileri.
6. `prompts/CODEX_MASTER_PROMPT.md` → ilk görev için hazır komut.

## Kanonik görseller
- Lalin'in **ilk üç beğenilen görseli**: `assets/character/approved_initial_3/`.
- **Kesin onaylanan renkli oda:** `assets/environment/APPROVED_lalin_room_master.png`.
- Daha sonra üretilen iki model sheet: `assets/character/additional_concepts/` (**yalnız yardımcı fikir**, gerçek rig veya fiziksel ölçü değil).
- `assets/voice/voice_picker_raina_ui.png` sadece **Raina sesini seçtiğini gösteren ekran görüntüsüdür**; ses dosyası değildir.

## Eksik olanlar
- **Gerçek Raina deneme sesi (.wav/.mp3)**: kullanıcı Higgsfield'da test etti fakat bu pakette ses dosyası yok. `assets/voice/README.md`yi oku.
- Katmanlı, temiz, gerçek 2D rig ve ayrı hareket/poz varlıkları.
- Performans aktarımı yapılacaksa **driving video** (referans oyunculuk kaydı).
- Lisans kayıtlı Foley/SFX dosyaları ve sahneye özel mix.

## Kesin durum
Önceki oda katmanlama prototipi **başarısız / görsel hareket zayıf**, asla üretim başlangıcı olarak kabul edilmemeli. Yalnız incelemek istenirse `archive/failed_room_motion_v0_1/` içinde durur.

## Önemli
Bu paket karakter konseptleri ve yüksek çözünürlüklü oda görseli içerir ama **profesyonel rig ve ses varlıkları içermez**. Test hedeflerini kaynaksız var sayma. Harici ücretli model veya abonelik kullanımında önce kullanıcı onayı al.
