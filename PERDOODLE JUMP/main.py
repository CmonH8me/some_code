import pygame
import random
import os

pygame.init()
clock = pygame.time.Clock()
FPS = 45
GRAVITY = 1
game_over = False
MAX_PLATFORMS = 10
SCROLL_LINE = 200
bg_scroll = 0
WIDTH = 400
HEIGHT = 600
score = 0
pygame.mixer.music.load('music/backmusic.mp3')
pygame.mixer.music.set_volume(0.4)
pygame.mixer.music.play(-1, 0.0)
lose_fx = pygame.mixer.Sound('music/lose.mp3')
jump_fx = pygame.mixer.Sound('music/jump.mp3')
jump_fx.set_volume(0.3)
death_fx = pygame.mixer.Sound('music/death2.mp3')
death_fx.set_volume(0.5)

if os.path.exists('score.txt'):
    with open('score.txt', 'r') as file:
        high_score = int(file.read())
else:
    high_score = 0
fade_counter = 0
font_small = pygame.font.SysFont('JOPA', 20)
font_big = pygame.font.SysFont('JOPA', 24)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("NARUTO JUMP")
icon_image = pygame.image.load("images/icon.png").convert_alpha()
bg_image = pygame.transform.scale(pygame.image.load('images/bg1.jpg').convert_alpha(), (400, 600))
player_image = pygame.image.load('images/player2.png').convert_alpha()
platform_image = pygame.image.load('images/platform.png').convert_alpha()
enemy_sheet_image = pygame.transform.scale(pygame.image.load('images/enemy.png').convert_alpha(), (200, 50))
pygame.transform.scale(platform_image, (75, 50))
pygame.display.set_icon(icon_image)


def draw_text(text, font, color, x, y):
    img = font.render(text, True, color)
    screen.blit(img, (x,y))


def draw_info():
    pygame.draw.rect(screen, (10, 130, 209), (0, 0, WIDTH, 15))
    pygame.draw.line(screen, (255, 255, 255), (0, 15), (WIDTH, 15), 2)
    draw_text(f'SCORE: {score}', font_small, (255, 255, 255), 0, 0)
    draw_text(f'HIGH SCORE: {high_score}', font_small, (255, 255, 255), 275, 0)


def draw_bg(bg_scroll):
    screen.blit(bg_image, (0, 0+bg_scroll))
    screen.blit(bg_image, (0, -600 + bg_scroll))


class SpriteSheet():
    def __init__(self, image):
        self.sheet = image

    def get_image(self, frame, width, height, scale, colour):
        image = pygame.Surface((width, height)).convert_alpha()
        image.blit(self.sheet,(-5,0), ((frame*width), 0, width, height))
        image = pygame.transform.scale(image, (int(width*scale), int(height*scale)))
        image.set_colorkey(colour)
        return image


class Enemy(pygame.sprite.Sprite):
    def __init__(self, width, y, sprite_sheet, scale):
        pygame.sprite.Sprite.__init__(self)
        self.animation_list = []
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()
        self.direction = random.choice([-1, 1])
        if self.direction == 1:
            self.flip = True
        else:
            self.flip = False
        animation_steps = 5
        for animation in range(animation_steps):
            image = sprite_sheet.get_image(animation, 40, 45, scale, (0, 0, 0))
            image = pygame.transform.flip(image, self.flip, False)
            image.set_colorkey((0, 0, 0))
            self.animation_list.append(image)
        self.image = self.animation_list[self.frame_index]
        self.rect = self.image.get_rect()
        if self.direction == 1:
            self.rect.x = 0
        else:
            self.rect.x = WIDTH
        self.rect.y = y


    def update(self, scroll,  WIDTH):
        ANIMATION_COOLDOWN = 75
        self.image = self.animation_list[self.frame_index]
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index +=1
        if self.frame_index > len(self.animation_list)-1:
            self.frame_index = 0
        self.rect.x += self.direction * 2
        self.rect.y += scroll
        if self.rect.right < 0 or self.rect.left > WIDTH:
            self.kill()


class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, moving):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(platform_image, (width, 20))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = random.randint(1, 2)
        self.direction = random.choice([-1, 1])
        self.move_counter = random.randint(0, 50)
        self.moving = moving

    def update(self, scroll):
        if self.moving:
            self.move_counter += 1
            self.rect.x += self.direction * self.speed
        if self.move_counter >= 100 or self.rect.left < 0 or self.rect.right > WIDTH:
            self.direction *= -1
            self.move_counter = 0
        self.rect.y += scroll
        if self.rect.top > HEIGHT:
            self.kill()


class Player:
    def __init__(self, x, y,):
        self.image = pygame.transform.scale(player_image, (50, 50))
        self.width = 30
        self.height = 40
        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.rect.center = (x,y)
        self.flip = False
        self.vel_y = 0

    def draw(self):
        screen.blit(pygame.transform.flip(self.image, self.flip, False), (self.rect.x - 10, self.rect.y - 5))
        #pygame.draw.rect(screen, (255, 255, 255), self.rect, 2)

    def move(self):
        scroll = 0
        dx = 0
        dy = 0
        key = pygame.key.get_pressed()
        if key[pygame.K_LEFT]:
            dx = -10
            self.flip = True
        if key[pygame.K_RIGHT]:
            dx = 10
            self.flip = False
        self.vel_y += GRAVITY
        dy += self.vel_y
        if self.rect.left + dx < 0:
            dx = 0 - self.rect.left
        if self.rect.right + dx > WIDTH:
            dx = WIDTH - self.rect.right
        for platform in platforms:
            if platform.rect.colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                if self.rect.bottom < platform.rect.centery:
                    if self.vel_y > 0:
                        self.rect.bottom = platform.rect.top
                        dy = 0
                        self.vel_y = - 20
                        jump_fx.play()
        if self.rect.top <= SCROLL_LINE:
            if self.vel_y < 0:
                scroll = -dy
        self.rect.x += dx
        self.rect.y += dy + scroll
        return scroll


enemy_sheet_image = SpriteSheet(enemy_sheet_image)
enemies = pygame.sprite.Group()
platforms = pygame.sprite.Group()
platform = Platform(WIDTH//2 - 50, HEIGHT-50, 100, False)
platforms.add(platform)
player = Player(WIDTH//2, HEIGHT-150)

running = True
while running:

    clock.tick(FPS)
    if game_over == False:
        scroll = player.move()
        bg_scroll += scroll
        if bg_scroll >= 600:
            bg_scroll = 0
        draw_bg(bg_scroll)
        if len(platforms) < MAX_PLATFORMS:
            p_w = random.randint(40, 60)
            p_x = random.randint(0, WIDTH-p_w)
            p_y = platform.rect.y - random.randint(80, 120)
            p_type = random.randint(1, 2)
            if p_type == 1 and score > 500:
                p_moving = True
            else:
                p_moving = False
            platform = Platform(p_x, p_y, p_w, p_moving)
            platforms.add(platform)

        enemies.update(scroll, WIDTH)
        if len(enemies) == 0 and score > 1500:
            enemy = Enemy(0, 100, enemy_sheet_image, 1)
            enemies.add(enemy)

        pygame.draw.line(screen, (255, 255, 255),
                         (0, score-high_score+SCROLL_LINE),
                         (WIDTH, score-high_score+SCROLL_LINE),
                         3)
        draw_text('HIGH SCORE', font_small, (0, 0, 0), WIDTH-130, score-high_score+SCROLL_LINE)
        if scroll > 0:
            score += scroll
        platforms.update(scroll)
        platforms.draw(screen)
        enemies.draw(screen)
        player.draw()
        draw_info()
        #for enemy in enemies:
            #pygame.draw.rect(screen, (0,0,0), enemy.rect, 2)

        if player.rect.top > HEIGHT:
            death_fx.play()
            game_over = True
        if pygame.sprite.spritecollide(player, enemies, False):
            death_fx.play()
            game_over = True
    else:
        pygame.mixer.music.pause()
        lose_fx.play(-1)
        if fade_counter < WIDTH:
            fade_counter += 5
            for y in range(0, 6, 2):
                pygame.draw.rect(screen, (0, 0, 0), (0, y*100, fade_counter, HEIGHT/6))
                pygame.draw.rect(screen, (0, 0, 0), (WIDTH - fade_counter, (y+1)*100, WIDTH, HEIGHT/6))
        else:
            draw_text('GAME OVER', font_big, (255, 0, 0), 130, 200)
            draw_text(f'SCORE: {score}', font_big, (255, 0, 0), 130, 250)
            draw_text('PRESS SPACE TO PLAY AGAIN', font_big, (255, 0, 0), 60, 300)
            if score > high_score:
                high_score = score
                with open('score.txt', 'w') as file:
                    file.write(str(high_score))
            key = pygame.key.get_pressed()
            if key[pygame.K_SPACE]:
                lose_fx.stop()
                pygame.mixer.music.unpause()
                game_over = False
                fade_counter = 0
                score = 0
                scroll = 0
                player.rect.center = (WIDTH//2, HEIGHT-150)
                platforms.empty()
                platform = Platform(WIDTH // 2 - 50, HEIGHT - 50, 100, False)
                platforms.add(platform)
                enemies.empty()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            if score > high_score:
                high_score = score
                with open('score.txt', 'w') as file:
                    file.write(str(high_score))
            running = False
            pygame.quit()
    pygame.display.update()