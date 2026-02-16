# 🐍 Neon Snake: Evolution

Bu proje, Python ve Pygame kütüphanesi kullanılarak geliştirilmiş modern bir yılan oyunudur. Sadece klasik bir yılan oyunu değil; otonom zeka, dinamik zorluk seviyeleri ve neon estetiği ile harmanlanmış bir mühendislik çalışmasıdır.

## 🌟 Öne Çıkan Özellikler

- **Otonom Giriş Ekranı (AI Intro):** Oyun başlangıç ekranında yılan, basit bir yol bulma algoritması ile elmayı kendi kendine kovalar.
- **Dinamik Engel Sistemi:** Skor arttıkça engeller şekil değiştirir ve büyür, bu da oyunun zorluk seviyesini kademeli olarak artırır.
- **Turbo Mod:** Yön tuşlarına basılı tutulduğunda yılanın hızı iki katına çıkar, bu da oyuncuya risk-ödül dengesi sunar.
- **Parçacık Efektleri:** Elma yendiğinde veya bombaya çarpıldığında neon parçacık efektleri oluşur.
- **Yerel Skor Sistemi:** `high_score.txt` dosyası üzerinden en yüksek skoru kalıcı olarak saklar.
- **Retro Ses Yönetimi:** Elma yeme, patlama ve oyun bitişi için özel ses efektleri ve arka plan müziği entegre edilmiştir.

## 🛠️ Teknik Detaylar

- **Dil:** Python 3.x
- **Kütüphane:** Pygame
- **Mantık:** State machine tabanlı oyun döngüsü, koordinat tabanlı çarpışma algılama ve otonom hareket mantığı.

## 🎮 Kurulum ve Çalıştırma

1. Pygame kütüphanesini yükleyin:
   ```bash
   pip install pygame
   ```
