import pygame
import random
import sys
import time
import os

# Pygame ve ses sistemini ayağa kaldırıyoruz
pygame.init()
pygame.mixer.init()

# Ekran ayarları (800x600 standart genişlik)
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Neon Snake: Evolution")
clock = pygame.time.Clock()

# Renk paletimiz - Neon temasına uygun seçim
BLACK = (10, 10, 10)
WHITE = (220, 220, 220)
APPLE_GREEN = (57, 255, 20)
BOMB_PURPLE = (150, 0, 255)
OBS_GRAY = (80, 80, 80)
GOLD = (255, 215, 0)
NEON_RED = (255, 30, 30)
SNAKE_COLORS = [(180, 0, 255), (0, 200, 255), (255, 200, 0)]

# Yazı tiplerini tanımlıyoruz
font_xs = pygame.font.SysFont("bahnschrift", 16)
font_small = pygame.font.SysFont("bahnschrift", 22)
font_title = pygame.font.SysFont("bahnschrift", 55)

# Ses dosyalarının yüklendiği kısım - Dosya yoksa oyun çökmesin diye try-except kullandım
try:
    eat_sound = pygame.mixer.Sound("eat.wav")
    bomb_sound = pygame.mixer.Sound("bomb.wav")
    death_sound = pygame.mixer.Sound("death.wav")
    
    pygame.mixer.music.load("background_music.wav") 
    pygame.mixer.music.play(-1) # Müziği döngüye alıyoruz
    pygame.mixer.music.set_volume(0.2) # Arka plan müziği kafamızı şişirmesin :)
except Exception as e:
    eat_sound = bomb_sound = death_sound = None
    print(f"Ses yükleme hatası: {e}")

# Rekor sistemini yöneten fonksiyonlar (high_score.txt dosyasından okur)
def get_high_score():
    if not os.path.exists("high_score.txt"): return 0
    with open("high_score.txt", "r") as f:
        try: return int(f.read())
        except: return 0

def save_high_score(score):
    if score > get_high_score():
        with open("high_score.txt", "w") as f: f.write(str(score))

# Elma yendiğinde veya bombaya çarpınca çıkan patlama efekti
particles = []
def create_particles(pos, color):
    for _ in range(15):
        particles.append([list(pos), [random.randint(-5, 5), random.randint(-5, 5)], random.randint(4, 8), color])

# Başlangıç ekranındaki bilgilendirme paneli kısımı
def draw_legend():
    start_y = HEIGHT - 145
    items = [
        (APPLE_GREEN, "APPLE: +10 Score & Grow"),
        (BOMB_PURPLE, "BOMB: -15 Score & Shrink"),
        (OBS_GRAY, "OBSTACLE: Game Over!"),
        (WHITE, "P KEY: Pause / Resume")
    ]
    for i, (color, text) in enumerate(items):
        pygame.draw.rect(screen, color, [40, start_y + (i*25), 15, 15])
        screen.blit(font_xs.render(text, True, WHITE), [65, start_y + (i*25)])

# Skora göre büyüyen ve şekil değiştiren engelleri üreten fonksiyon kısımı
def get_dynamic_obstacle(apple_pos, score):
    while True:
        center_x = round(random.randrange(100, WIDTH - 100) / 20.0) * 20.0
        center_y = round(random.randrange(100, HEIGHT - 100) / 20.0) * 20.0
        dist = ((center_x - apple_pos[0])**2 + (center_y - apple_pos[1])**2)**0.5
        if dist > 100: break # Engelin elmanın çok dibinde çıkmasını engelliyoruz

    offset = (score // 100) * 20 
    # L, T ve Kare şekilleri arasından rastgele seçiyoruz
    shapes = [[[0,0], [0,-20], [0,20], [20,20+offset]], [[-20-offset,0], [0,0], [20+offset,0], [0,20]], [[0,0], [20,0], [0,20+offset], [20,20+offset]]]
    return [[center_x + s[0], center_y + s[1]] for s in random.choice(shapes)]

def game_loop(mode="intro"):
    game_over = False
    game_close = False
    paused = False
    
    # Müzik çalmıyorsa başlatıyoruz
    if not pygame.mixer.music.get_busy():
        pygame.mixer.music.play(-1)

    # Başlangıç koordinatları ve değişkenleri
    x1, y1 = WIDTH / 2, HEIGHT / 2
    x1_change, y1_change = 20, 0
    snake_list = []
    snake_len = 8 if mode == "intro" else 3
    score = 0
    high_score = get_high_score()
    start_time = time.time()
    final_time = ""
    
    apple_pos = [round(random.randrange(100, WIDTH-100)/20.0)*20, round(random.randrange(100, HEIGHT-100)/20.0)*20]
    bomb_pos = [-100, -100]
    current_obs = []
    fading_obs = [] # Yeni engel gelince eskisinin silik kalma efekti
    fade_timer = 0

    while not game_over:
        if not paused:
            curr_dur = int(time.time() - start_time)
            time_label = f"{curr_dur // 60:02d}:{curr_dur % 60:02d}"

            # Başlangıç ekranındaki otonom yılan zekası
            if mode == "intro":
                if x1 < apple_pos[0]: x1_change, y1_change = 20, 0
                elif x1 > apple_pos[0]: x1_change, y1_change = -20, 0
                elif y1 < apple_pos[1]: x1_change, y1_change = 0, 20
                elif y1 > apple_pos[1]: x1_change, y1_change = 0, -20

        # Oyun bitti ekranı döngüsü
        while game_close:
            screen.fill(BLACK)
            save_high_score(score)
            title = font_title.render("GAME OVER", True, NEON_RED)
            screen.blit(title, title.get_rect(center=(WIDTH/2, HEIGHT/2 - 80)))
            stats = f"Score: {score} | Best: {get_high_score()} | Time: {final_time}"
            screen.blit(font_small.render(stats, True, WHITE), (WIDTH/2 - 200, HEIGHT/2))
            screen.blit(font_small.render("Restart: ENTER | Quit: Q", True, GOLD), (WIDTH/2 - 130, HEIGHT/2 + 60))
            pygame.display.update()
            
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q: pygame.quit(); sys.exit()
                    if event.key == pygame.K_RETURN: return

        # Burada klavye kontrollerini yakalıyoruz
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if mode == "play" and event.key == pygame.K_p: paused = not paused
                if mode == "play" and not paused:
                    if event.key == pygame.K_LEFT and x1_change <= 0: x1_change, y1_change = -20, 0
                    elif event.key == pygame.K_RIGHT and x1_change >= 0: x1_change, y1_change = 20, 0
                    elif event.key == pygame.K_UP and y1_change <= 0: x1_change, y1_change = 0, -20
                    elif event.key == pygame.K_DOWN and y1_change >= 0: x1_change, y1_change = 0, 20
                elif mode == "intro" and event.key == pygame.K_RETURN: return

        if not paused:
            x1 += x1_change; y1 += y1_change
            
            # Duvarlara çarpma kontrolü
            if (x1 >= WIDTH or x1 < 0 or y1 >= HEIGHT or y1 < 0) and mode == "play": 
                pygame.mixer.music.stop()
                if death_sound: death_sound.play()
                final_time = time_label; game_close = True

            screen.fill(BLACK)
            alpha = 70 if mode == "intro" else 255
            
            # Elma, bomba ve engelleri ekrana çiziyoruz
            pygame.draw.rect(screen, (*APPLE_GREEN, alpha), [apple_pos[0], apple_pos[1], 20, 20])
            if score >= 50: pygame.draw.rect(screen, (*BOMB_PURPLE, alpha), [bomb_pos[0], bomb_pos[1], 20, 20])
            for o in current_obs: pygame.draw.rect(screen, (*OBS_GRAY, alpha), [o[0], o[1], 20, 20])
            
            # Parçacık patlamalarını güncelle ve çiz
            for p in particles[:]:
                p[0][0] += p[1][0]; p[0][1] += p[1][1]; p[2] -= 0.2
                if p[2] <= 0: particles.remove(p)
                else: pygame.draw.rect(screen, (*p[3], 150), [p[0][0], p[0][1], p[2], p[2]])

            # Engel geçiş animasyonu (hayalet engeller)
            if fade_timer > 0:
                for o in fading_obs: pygame.draw.rect(screen, (40, 40, 40, 50), [o[0], o[1], 20, 20])
                fade_timer -= 1
            else: fading_obs = []

            # Yılanın gövdesini oluşturma ve çarpışma mantığı
            snake_head = [x1, y1]
            snake_list.append(snake_head)
            if len(snake_list) > snake_len: del snake_list[0]

            if mode == "play":
                for segment in snake_list[:-1]:
                    if segment == snake_head: 
                        pygame.mixer.music.stop()
                        if death_sound: death_sound.play()
                        final_time = time_label; game_close = True
                for o in current_obs:
                    if snake_head == o: 
                        pygame.mixer.music.stop()
                        if death_sound: death_sound.play()
                        final_time = time_label; game_close = True

            # Yılanın her boğumunun harklı renkte görünecek şekilde çizildiği kısım 
            for i, segment in enumerate(snake_list):
                color = SNAKE_COLORS[i % len(SNAKE_COLORS)]
                pygame.draw.rect(screen, (*color, alpha), [segment[0], segment[1], 20, 20])
                pygame.draw.rect(screen, (0,0,0, alpha), [segment[0], segment[1], 20, 20], 1)

            if mode == "intro":
                banner = font_title.render("NEON SNAKE", True, GOLD)
                screen.blit(banner, banner.get_rect(center=(WIDTH/2, HEIGHT/2 - 60)))
                screen.blit(font_small.render("PRESS ENTER TO START", True, WHITE), (WIDTH/2 - 120, HEIGHT/2 + 20))
                draw_legend()
            else:
                stats_label = f"Score: {score} | Best: {high_score} | Time: {time_label}"
                screen.blit(font_small.render(stats_label, True, WHITE), [10, 10])

            # Elma yeme mantığı ve zorluk artışı
            if x1 == apple_pos[0] and y1 == apple_pos[1]:
                if eat_sound: eat_sound.play()
                create_particles(apple_pos, APPLE_GREEN)
                apple_pos = [round(random.randrange(100, WIDTH-100)/20.0)*20, round(random.randrange(100, HEIGHT-100)/20.0)*20]
                if mode == "play":
                    score += 10; snake_len += 1; fading_obs = list(current_obs); fade_timer = 10
                    if score >= 30: current_obs = get_dynamic_obstacle(apple_pos, score)
                    if score >= 50: 
                        bomb_pos = [apple_pos[0]+20, apple_pos[1]] if random.random() > 0.5 else [apple_pos[0], apple_pos[1]+20]

            # Bombaya çarpma mantığı
            if x1 == bomb_pos[0] and y1 == bomb_pos[1]:
                if bomb_sound: bomb_sound.play()
                create_particles(bomb_pos, BOMB_PURPLE)
                score = max(0, score - 15); snake_len = max(2, snake_len - 1); bomb_pos = [-100, -100]

        else: # Duraklatma ekranı görseli
            pause_msg = font_title.render("GAME PAUSED", True, GOLD)
            screen.blit(pause_msg, pause_msg.get_rect(center=(WIDTH/2, HEIGHT/2 - 20)))
            screen.blit(font_small.render("Press P to Resume", True, WHITE), (WIDTH/2 - 80, HEIGHT/2 + 40))

        pygame.display.update()
        
        # Turbo modu ve oyun hızı (skora göre hızlanır)
        keys = pygame.key.get_pressed()
        turbo = mode == "play" and not paused and ((keys[pygame.K_LEFT] and x1_change < 0) or (keys[pygame.K_RIGHT] and x1_change > 0) or (keys[pygame.K_UP] and y1_change < 0) or (keys[pygame.K_DOWN] and y1_change > 0))
        tick_rate = 8 + (score // 100) * 2
        clock.tick(tick_rate * 2 if turbo else tick_rate)

if __name__ == "__main__":
    while True: # Oyun bittiğinde ana ekrana dönebilmek için sonsuz döngü sağlıyoruz
        game_loop("intro")
        game_loop("play")