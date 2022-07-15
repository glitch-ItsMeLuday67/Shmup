from textwrap import fill
import pygame
import random
from os import path
import time
img_dir = path.join(path.dirname(__file__),"images")
snd_dir = path.join(path.dirname(__file__),"sounds")

width = 800
height = 800
fps = 60
powerup_time = 5000

#Define colours
white = (255,255,255)
black = (0,0,0)
red = (255,0,0)
green = (0,255,0)
blue = (0,0,255)
yellow = (255,255,0)
lavender = (100,0,255)

#Initialize Pygame and create window
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((width,height))
pygame.display.set_caption("Shmup")
clock = pygame.time.Clock()

font_name = pygame.font.match_font("arial")
def draw_text(surf, text, size, x, y):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, white)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)

#Create graphics
background = pygame.image.load(path.join(img_dir,"spotted_background_800x800.png")).convert()
background_rect = background.get_rect()
player_png = pygame.image.load(path.join(img_dir,"player.png")).convert()
player_mini_png = pygame.transform.scale(player_png,(30,25))
player_mini_png.set_colorkey(black)
bullet_png = pygame.image.load(path.join(img_dir,"bullet.png")).convert()
enemy_png = pygame.image.load(path.join(img_dir,"enemy.png")).convert()
meteor_images = []
meteor_list = ["meteorBrown_big1.png","meteorGrey_med1.png","meteorBrown_med3.png","meteorGrey_med2.png"
              ,"meteorGrey_tiny1.png","meteorGrey_big3.png","meteorGrey_small1.png","meteorBrown_small2.png","meteorBrown_big4.png"]
for img in meteor_list:
    meteor_images.append(pygame.image.load(path.join(img_dir,img)).convert())
powerup_images = {}
powerup_images["shield"] = pygame.image.load(path.join(img_dir,"shield.png")).convert()
powerup_images["gun"] = pygame.image.load(path.join(img_dir,"bolt.png")).convert()
powerups = pygame.sprite.Group()

#Add sounds & background music
shoot_snd = pygame.mixer.Sound(path.join(snd_dir,"boom1.wav"))
shoot_snd.set_volume(0.20)
explosion_snd = []
for snd in ["DeathFlash.flac","rock_breaking.flac"]:
    explosion_snd.append(pygame.mixer.Sound(path.join(snd_dir,snd)))
    pygame.mixer.music.set_volume(0.20)
pygame.mixer.music.load(path.join(snd_dir,"SeamlessLoop.ogg"))
pygame.mixer.music.set_volume(0.20)

#Path = C:\Users\emark\Desktop\PYGAME\images\images
#Create sprites
class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(player_png,(50,40))
        self.image.set_colorkey(black)
        self.rect = self.image.get_rect()
        self.radius = 10
        # pygame.draw.circle(self.image,red,self.rect.center,self.radius)
        self.rect.centerx = width/2
        self.rect.bottom = height-10
        self.speedx = 0
        self.shield = 200
        self.health = 100
        self.shoot_delay = 300
        self.last_shoot = pygame.time.get_ticks()
        self.lives = 1
        self.hidden = False
        self.hidden_timer = pygame.time.get_ticks()
        self.power = 1
        self.power_time = pygame.time.get_ticks()
    def hide(self):
        self.hidden = True
        self.hide_timer = pygame.time.get_ticks()
        self.rect.center = (width/2,height+200)
    def update(self):
        if self.power >= 2 and pygame.time.get_ticks() - self.power_time > powerup_time:
            self.power -= 1
            self.power_time = pygame.time.get_ticks()
        self.speedx = 0
        self.width = width
        self.height = height
        keystate = pygame.key.get_pressed()
        if keystate [pygame.K_UP] or keystate [pygame.K_RETURN] or keystate [pygame.K_SPACE]:
            self.shoot()
        if keystate [pygame.K_LEFT]:
            self.speedx = -4
        if keystate [pygame.K_RIGHT]:
            self.speedx = 4
        self.rect.x += self.speedx
        if self.rect.right > width:
            self.rect.left = 0
        if self.rect.left < 0:
            self.rect.right = width
        if keystate [pygame.K_F11]:
            screen = pygame.display.set_mode((1920,1080))
        #Unhide if hidden
        if self.hidden and pygame.time.get_ticks() - self.hide_timer >= 1000:
            self.hidden = False
            self.rect.centerx = (width/2)
            self.rect.bottom = height - 10
    def powerup(self):
        self.power += 1
        self.power_time = pygame.time.get_ticks()            
    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shoot > self.shoot_delay:
            self.last_shoot = now
            if self.power == 1:
                bullet = Bullet(self.rect.centerx,self.rect.top)
                all_sprites.add(bullet)
                bullets.add(bullet)
                shoot_snd.play()
                shoot_snd.set_volume(0.10)
            if self.power >= 2:
                bullet1 = Bullet(self.rect.left,self.rect.centery)
                bullet2 = Bullet(self.rect.right,self.rect.centery)
                all_sprites.add(bullet1)
                all_sprites.add(bullet2)
                bullets.add(bullet1)
                bullets.add(bullet2)
                shoot_snd.play()
                shoot_snd.set_volume(0.10)

class Mob(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image_original = random.choice(meteor_images)
        self.image_original.set_colorkey(black)
        self.image = self.image_original.copy()
        self.rect = self.image.get_rect()
        #100px = 100*0.85/2 = 85/2 = 42.5
        self.radius = self.rect.width*0.85/2
        # pygame.draw.circle(self.image,blue,self.rect.center,self.radius)
        self.image = enemy_png
        self.rect.x = random.randrange(width - self.rect.width)
        self.rect.y = random.randrange(-100,150)
        self.speedy = random.randrange(1,8)
        self.speedx = random.randrange(-3,3)
        self.rot = 0
        self.rot_speed = random.randrange(-8,8)
        self.last_update = pygame.time.get_ticks()
    def rotate(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > 50:
            self.last_update = now
            self.rot = (self.rot + self.rot_speed)%360
            new_image = pygame.transform.rotate(self.image_original,self.rot)
            old_center = self.rect.center
            self.image = new_image
            self.rect = self.image.get_rect()
            self.rect.center = old_center

    def update(self):
        self.rotate()
        self.rect.x += self.speedx
        self.rect.y += self.speedy
        if self.rect.top > height or self.rect.left < -20 or self.rect.right > width:
            self.rect.x = random.randrange(width - self.rect.width)
            self.rect.y = random.randrange(-100,-40)
            self.speedy = random.randrange(1,12)

class Bullet(pygame.sprite.Sprite):
    def __init__(self,x,y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(bullet_png,(7,30))
        self.image.set_colorkey(black)
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        self.speedy = -10
    def update(self):
        self.rect.y += self.speedy
        if self.rect.bottom < 0:
            self.kill()

class explosion(pygame.sprite.Sprite):
    def __init__(self,center,size):
        pygame.sprite.Sprite.__init__(self)
        self.size = size
        self.image = explosion_anim[self.size][0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 100
    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == len(explosion_anim[self.size]):
                self.kill()
            else:
                center = self.rect.center
                self.image = explosion_anim[self.size][self.frame]
                self.rect = self.image.get_rect()
                self.rect.center = center

class Pow(pygame.sprite.Sprite):
    def __init__(self,center):
        pygame.sprite.Sprite.__init__(self)
        self.type = random.choice(["shield","gun"])
        self.image = powerup_images[self.type]
        self.image.set_colorkey(black)
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.speedy = 2
    def update(self):
        self.rect.y += self.speedy
        if self.rect.top > height:
            self.kill()

all_sprites = pygame.sprite.Group()
player = Player()
all_sprites.add(player)
mobs = pygame.sprite.Group()
bullets = pygame.sprite.Group()
for i in range(10):
    m = Mob()
    all_sprites.add(m)
    mobs.add(m)
running = True
score = 0
#-1 to repeat music infinitely

#Explosions

explosion_anim = {}
explosion_anim["lg"] = []
explosion_anim["sm"] = []

explosion_anim["player"] = []
#Lg and sm is a key and their values are [] (empty list)
for i in range (0,9):
    file_name = "regularExplosion0"+str(i)+".png"
    img = pygame.image.load(path.join(img_dir,file_name)).convert()
    img.set_colorkey(black)
    img_lg = pygame.transform.scale(img,(75,75))
    explosion_anim["lg"].append(img_lg)
    img_sm = pygame.transform.scale(img,(32,32))
    explosion_anim["sm"].append(img_sm)
    file_name = "sonicExplosion0"+str(i)+".png"
    img = pygame.image.load(path.join(img_dir,file_name)).convert()
    img.set_colorkey(black)
    explosion_anim["player"].append(img)

def new_mob():
    m = Mob()
    all_sprites.add(m)
    mobs.add(m)

def draw_shield_bar(surf,x,y,pct,bar_colour,outline_colour):
    if pct <= 0:
        pct = 0
    bar_length = 100
    bar_height = 10
    outline_length = 100
    outline_height = 10
    fill = (bar_length * pct / 100) / 2
    outline = pygame.Rect(x,y,outline_length,outline_height)
    fill_rect = pygame.Rect(x,y,fill,bar_height)
    pygame.draw.rect(surf,bar_colour,fill_rect)
    pygame.draw.rect(surf,outline_colour,outline,2)

def draw_health_bar(surf,x,y,pct,bar_colour,outline_colour):
    if pct <= 0:
        pct = 0
    bar_length = 100
    bar_height = 10
    outline_length = 100
    outline_height = 10
    fill = bar_length * pct / 100
    outline = pygame.Rect(x,y,outline_length,outline_height)
    fill_rect = pygame.Rect(x,y,fill,bar_height)
    pygame.draw.rect(surf,bar_colour,fill_rect)
    pygame.draw.rect(surf,outline_colour,outline,2)

def draw_lives(surf,x,y,lives,img):
    for i in range(lives):
        img_rect = img.get_rect()
        img_rect.x = x + 40 * i
        img_rect.y = y
        surf.blit(img,img_rect)
    

pygame.mixer.music.play(loops = -1)
pygame.mixer.music.set_volume(0.20)

game_over = True

def display_end_screen():
    screen.blit(background, background_rect)
    draw_text(screen, "SHMUP!", 64, width / 2, height / 4)
    draw_text(screen, "Arrow keys move, Space to fire", 22,
              width / 2, height / 2)
    draw_text(screen, "Press a key to begin", 18, width / 2, height * 3 / 4)
    pygame.display.flip()
    waiting = True
    while waiting:
        clock.tick(fps)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYUP:
                waiting = False
        
while running:
    if game_over:
        display_end_screen()
        game_over = False
        all_sprites = pygame.sprite.Group()
        mobs = pygame.sprite.Group()
        bullets = pygame.sprite.Group()
        powerups = pygame.sprite.Group()
        player = Player()
        all_sprites.add(player)
        for i in range(8):
            new_mob()
        score = 0

    #Keep loop running at the right speed
    clock.tick(fps)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    all_sprites.update()
    #Check to see if the bullet hit a mob
    hits = pygame.sprite.groupcollide(mobs,bullets,True,True)

    for hit in hits:
        score += int(50 - hit.radius)
        exp_snd = random.choice(explosion_snd)
        exp_snd.play()
        exp_snd.set_volume(0.20)
        expl = explosion(hit.rect.center, "lg")
        all_sprites.add(expl)
        if random.random() > 0.9:
            pow = Pow(hit.rect.center)
            all_sprites.add(pow)
            powerups.add(pow)
        new_mob()

    #Check to see if the player hit a powerup
    hits = pygame.sprite.spritecollide(player,powerups,True)
    for hit in hits : 
        if hit.type == "shield":
            player.shield += random.randrange(10,70)
            if player.shield >= 200:
                player.shield = 200
        if hit.type == "gun":
            player.powerup()

    #Check to see if the mob hit a player
    hits = pygame.sprite.spritecollide(player,mobs,True,pygame.sprite.collide_circle)
    for hit in hits:
        player.shield -= hit.radius * 2
        expl = explosion(hit.rect.center, "sm")  
        all_sprites.add(expl)
        new_mob()
        if player.shield <= 0:
            player.health-= hit.radius * 2
            new_mob()
            if player.health <= 0:
                player.lives -= 1
                player.shield = 200
                player.health = 100
                player.hide()
        if player.lives == 0:
            game_over = True
            # running = False
    # screen.fill(lavender)
    screen.blit(background,background_rect)
    all_sprites.draw(screen)
    draw_text(screen, str("Score: " + str(score)), 25, width/2, 20)
    # draw_text(screen, str("Game Over"), 25, width/2, 60)
    draw_shield_bar(screen,5,5,player.shield,blue,white)
    draw_text(screen, str("Shield"), 18, 25, 15)
    draw_health_bar(screen,5,40,player.health,red,white)
    draw_text(screen, str("Health"), 18, 25, 50)
    draw_lives(screen,width - 125,5,player.lives,player_mini_png)
    pygame.display.flip()
pygame.quit()