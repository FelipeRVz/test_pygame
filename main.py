import random

import pygame
from sys import exit
from random import randint, choice


class Player(pygame.sprite.Sprite):
    def __init__(self, floor):
        super().__init__()
        # standing frames
        standing_1 = pygame.image.load("graphics/player/Pwak-1.png").convert_alpha()
        standing_2 = pygame.image.load("graphics/player/Pwak-2.png").convert_alpha()
        self.standing_frames = [standing_1, standing_1, standing_2, standing_2]
        self.standing_index = 0
        # walking frames
        walking_sheet = pygame.image.load("graphics/player/Pwak_walking.png")
        walking_1 = walking_sheet.subsurface((0, 0, 62, 64)).convert_alpha()
        walking_2 = walking_sheet.subsurface((62, 0, 62, 64)).convert_alpha()
        walking_3 = walking_sheet.subsurface((62, 64, 62, 64)).convert_alpha()
        self.walking_frames = [walking_1, walking_2, walking_1, walking_3]
        self.walking_index = 0
        # sitting frames
        sitting_sheet = pygame.image.load("graphics/player/Pwak_sit.png")
        sit_1 = sitting_sheet.subsurface((0, 0, 62, 64)).convert_alpha()
        sit_2 = sitting_sheet.subsurface((62, 0, 62, 64)).convert_alpha()
        sit_3 = sitting_sheet.subsurface((0, 64, 62, 64)).convert_alpha()
        self.sitting_frames = [sit_1, sit_2, sit_3, sit_3, sit_3]
        self.sitting_index = 0
        # jumping frames
        self.jump_frame = pygame.image.load("graphics/player/pwak.png").convert_alpha()

        # sound
        self.jump_sound = pygame.mixer.Sound("sound/audio_jump.mp3")
        # self.lay_egg_sound = pygame.mixer.music.load("sound/hen_egg.mp3")

        self.start_x = 0
        self.start_y = floor

        self.image = self.standing_frames[self.standing_index]
        self.rect = self.image.get_rect(bottomleft=(self.start_x, self.start_y))
        self.gravity = 0
        self.floor = floor
        self.right = True
        self.standing = True
        self.sitting = False

        self.cooldown = 0

    def player_input(self):
        # keyboard
        global eggs_count
        keys = pygame.key.get_pressed()

        if self.sitting:
            if self.sitting_animation():
                self.sitting = False
        else:
            if keys[pygame.K_w] and self.rect.bottom >= self.floor:
                self.gravity = -20
                self.jump_sound.play().set_volume(0.2)
                # self.standing = True
            if keys[pygame.K_d] and self.rect.right <= 800:
                self.rect.right += 5
                self.right = True
                self.walking_animation()
            if keys[pygame.K_a] and self.rect.left > 0:
                self.rect.left -= 5
                self.right = False
                self.walking_animation()
            if keys[pygame.K_s]:
                # if eggs_count < 4 and self.cooldown == 0 and self.sitting_animation():
                if eggs_count < 4 and self.cooldown == 0:
                    eggs_count += 1
                    self.cooldown = 120
                    self.sitting = True
                    # self.lay_egg_sound.play().set_volume(0.4)
                    pygame.mixer.music.load("sound/hen_egg.mp3")
                    pygame.mixer.music.play()

    def apply_gravity(self):
        self.gravity += 1
        self.rect.bottom += self.gravity
        if self.rect.bottom >= self.floor:
            self.rect.bottom = self.floor

    def animation(self, frames, index, animation_speed):
        if self.rect.bottom == self.floor:
            index = round(index + animation_speed, 1)
            if index > len(frames) - 1:
                index = 0
            self.image = frames[int(index)]
        else:
            self.image = self.jump_frame
        if not self.right:
            self.image = pygame.transform.flip(self.image, True, False)
        return index

    def standing_animation(self):
        self.standing_index = self.animation(self.standing_frames, self.standing_index, 0.1)

    def walking_animation(self):
        self.walking_index = self.animation(self.walking_frames, self.walking_index, 0.1)

    def sitting_animation(self):
        self.sitting_index = self.animation(self.sitting_frames, self.sitting_index, 0.1)
        if int(self.sitting_index) == len(self.sitting_frames) - 1:
            return True
        return False

    def update(self):
        self.apply_gravity()
        self.standing_animation()
        self.player_input()
        if self.cooldown > 0:
            self.cooldown -= 1


class Enemy(pygame.sprite.Sprite):
    def __init__(self, e_type):
        super().__init__()
        # load frames
        self.e_type = e_type
        if e_type == "fly":
            fly_frame1 = pygame.image.load("graphics/fly/Fly1.png").convert_alpha()
            fly_frame2 = pygame.image.load("graphics/fly/Fly2.png").convert_alpha()
            y_pos = 210
            self.frames = [fly_frame1, fly_frame2]
        else:
            snail_frame1 = pygame.image.load("graphics/snail/snail1.png").convert_alpha()
            snail_frame2 = pygame.image.load("graphics/snail/snail2.png").convert_alpha()
            y_pos = 300
            self.frames = [snail_frame1, snail_frame2]

        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect(bottomleft=(randint(800, 1000), y_pos))
        self.speed = randint(1, 9)

    def animation(self):
        self.rect.x -= self.speed
        self.frame_index += 0.1
        if self.frame_index > len(self.frames):
            self.frame_index = 0
        self.image = self.frames[int(self.frame_index)]

    def destroy(self):
        if self.rect.right <= -100:
            self.kill()

    def update(self):
        self.animation()
        self.destroy()


class Egg(pygame.sprite.Sprite):
    def __init__(self, player_rect, right, cursor):
        super().__init__()
        # egg frame
        self.image = pygame.image.load("graphics/player/egg.png").convert_alpha()
        self.rect = self.image.get_rect(midright=player_rect.midright)
        self.speed = 10
        self.right = right
        self.gravity = int(player_rect.x - cursor[0])/10
        self.cursor = cursor

    def update(self):
        if self.right:
            self.rect.x += self.speed
        else:
            self.rect.x -= self.speed

        self.gravity += 2
        self.rect.y += self.gravity

        if self.rect.left > 800 or self.rect.right < 0:
            self.kill()


def display_score(round_score=0, instructions=True):
    if round_score != 0:
        score_surf = font.render(f"Score: {int(round_score/100)}", False, (64, 64, 64))
        score_rect = score_surf.get_rect(center=(400, 50))
        screen.blit(score_surf, score_rect)
    else:
        title_surf = font.render("PWAK RUNNER", False, (64, 64, 64))
        title_rect = title_surf.get_rect(center=(400, 50))
        screen.blit(title_surf, title_rect)

    if instructions:
        instruction_surf = font.render("Press Spacebar to start", False, (64, 64, 64))
        instruction_rect = instruction_surf.get_rect(center=(400, 300))
        screen.blit(instruction_surf, instruction_rect)


pygame.init()
screen = pygame.display.set_mode((800, 400))
pygame.display.set_caption("PWAK RUNNER")
clock = pygame.time.Clock()
floor_level = 300
game_active = False
font = pygame.font.Font("font/Pixeltype.ttf", 50)
start_time = 0
current_time = 0
bg_music = pygame.mixer.Sound("sound/music.wav")
bg_music.play().set_volume(0.5)

surface_sky = pygame.image.load("graphics/Sky.png").convert()
surface_ground = pygame.image.load("graphics/ground_2.png").convert()
player_1 = pygame.image.load("graphics/player/pwak.png").convert_alpha()
egg_surf = pygame.image.load("graphics/player/egg.png").convert_alpha()
ground_width = surface_ground.get_width()
surface_x_pos = 800 - ground_width
surface2_x_pos = surface_x_pos - ground_width

hen = pygame.sprite.GroupSingle()
hen.add(Player(floor_level))

enemies = pygame.sprite.Group()
eggs = pygame.sprite.Group()
eggs_count = 0

main_player = pygame.transform.rotozoom(player_1, 0, 2)
main_rectangle = main_player.get_rect(midbottom=(400, 200))

speed = 0

obstacle_timer = pygame.USEREVENT + 1
pygame.time.set_timer(obstacle_timer, 1500)

while True:
    # events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        if game_active:
            # add enemies on timer
            if event.type == obstacle_timer and game_active:
                enemies.add(Enemy(choice(["fly", "snail", "snail", "snail"])))
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if eggs_count > 0:
                        eggs_count -= 1
                        # print(int(hen.sprite.rect.x - pygame.mouse.get_pos()[0])/10)
                        eggs.add(Egg(hen.sprite.rect, hen.sprite.right, pygame.mouse.get_pos()))

        else:
            # start game
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                game_active = True

    if game_active:
        # background
        screen.blit(surface_sky, (0, 0))
        screen.blit(surface_ground, (surface_x_pos, floor_level))
        screen.blit(surface_ground, (surface2_x_pos, floor_level))

        surface_x_pos = surface_x_pos + speed if surface_x_pos <= 800 else surface2_x_pos - ground_width
        surface2_x_pos = surface2_x_pos + speed if surface2_x_pos <= 800 else surface_x_pos - ground_width

        # characters
        hen.draw(screen)
        hen.update()

        enemies.draw(screen)
        enemies.update()

        eggs.draw(screen)
        eggs.update()

        # texts
        current_time = pygame.time.get_ticks() - start_time
        display_score(current_time, False)

        for i in range(0, eggs_count):
            screen.blit(egg_surf, (5+(i*20), 5))

        # collision
        game_active = not pygame.sprite.spritecollide(hen.sprite, enemies, False)
        for egg in eggs.sprites():
            if pygame.sprite.spritecollide(egg, enemies, True):
                egg.kill()
    else:
        screen.fill((94, 129, 162))
        display_score(current_time, True)
        start_time = pygame.time.get_ticks()
        screen.blit(main_player, main_rectangle)
        enemies.empty()
        hen.empty()
        hen.add(Player(floor_level))
        eggs.empty()
        eggs_count = 0

    pygame.display.update()
    clock.tick(60)
