import sys

import pygame, random
import pymunk
import math

vector = pygame.math.Vector2

# initialize game
pygame.init()

# Khởi tạo Pymunk Space
my_space = pymunk.Space()
my_space.gravity = (0, 900)

WINDOW_WIDTH = 1184  # 37
WINDOW_HEIGHT = 672  # 21
display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Zombie Knight")
volume = 0.1

game_icon = pygame.image.load('images/game_icon.jpg')
pygame.display.set_icon(game_icon)

# set fps and clock
FPS = 60
clock = pygame.time.Clock()

# define classes
class Game():
    def __init__(self, player, zombie_group, platform_group, portal_group, bullet_group, ruby_group, tile_group):
        # set constant variables
        self.STARTING_ROUND_TIME = 30
        self.STARTING_ZOMBIE_CREATION_TIME = 10
        # set game values
        self.score = 0
        self.round_number = 1
        self.frame_count = 0
        self.round_time = self.STARTING_ROUND_TIME
        self.zombie_creation_time = self.STARTING_ZOMBIE_CREATION_TIME

        # set fonts
        self.title_font = pygame.font.Font("fonts/Pixel.ttf", 35)
        self.HUD_font = pygame.font.Font("fonts/Pixel.ttf", 24)

        # set sounds
        self.lost_ruby_sound = pygame.mixer.Sound("sounds/lost_ruby.wav")
        self.lost_ruby_sound.set_volume(volume)
        self.ruby_pickup_sound = pygame.mixer.Sound("sounds/ruby_pickup.wav")
        self.ruby_pickup_sound.set_volume(volume)
        pygame.mixer.music.load("sounds/level_music.wav")
        pygame.mixer.music.set_volume(volume)

        # attach groups and sprites
        self.player = player
        self.zombie_group = zombie_group
        self.platform_group = platform_group
        self.portal_group = portal_group
        self.bullet_group = bullet_group
        self.ruby_group = ruby_group
        self.tile_group = tile_group

        self.asset_paths = {
            1: {"images": ["images/tiles/Tile_1.png", "images/tiles/SewerTile_2.png", "images/tiles/SewerTile_3.png",
                           "images/tiles/SewerTile_4.png", "images/tiles/SewerTile_5.png"],
                "backgrounds": ["images/background_4.jpg"]},
            2: {"images": ["images/tiles/Tile_1.png", "images/tiles/Tile_2.png", "images/tiles/Tile_3.png",
                           "images/tiles/Tile_4.png", "images/tiles/Tile_5.png"],
                "backgrounds": ["images/background_3.png"]},
            3: {"images": ["images/tiles/InfernoTile_1.png", "images/tiles/InfernoTile_2.png",
                           "images/tiles/InfernoTile_3.png", "images/tiles/InfernoTile_4.png",
                           "images/tiles/InfernoTile_5.png"],
                "backgrounds": ["images/background_6.png"]},
            4: {"images": ["images/tiles/StationTile_1.png", "images/tiles/StationTile_2.png",
                           "images/tiles/StationTile_3.png", "images/tiles/StationTile_4.png",
                           "images/tiles/StationTile_5.png"],
                "backgrounds": ["images/background_station.png"]},
            5: {"images": ["images/tiles/ForestTile_1.png", "images/tiles/ForestTile_2.png",
                           "images/tiles/ForestTile_3.png", "images/tiles/ForestTile_4.png",
                           "images/tiles/ForestTile_5.png"],
                "backgrounds": ["images/background_forest.png"]}
        }

    def update(self):
        # update the round time every sec
        self.frame_count += 1
        if self.frame_count % FPS == 0:
            self.round_time -= 1
            self.frame_count = 0

        # check gameplay collision
        self.check_collision()

        # add zombie if zombie creation time is met
        self.add_zombie()

        # check for round completion
        self.check_round_completion()

        self.check_game_over()

    def draw(self):
        # set colors
        WHITE = (255, 255, 255)
        GREEN = (25, 200, 25)

        # set texts
        score_text = self.HUD_font.render("Score: " + str(self.score), True, WHITE)
        score_rect = score_text.get_rect()
        score_rect.topleft = (10, WINDOW_HEIGHT - 50)

        health_text = self.HUD_font.render("Health: " + str(self.player.health), True, WHITE)
        health_rect = health_text.get_rect()
        health_rect.topleft = (10, WINDOW_HEIGHT - 25)

        title_text = self.title_font.render("Zombie Knight", True, GREEN)
        title_rect = title_text.get_rect()
        title_rect.center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT - 25)

        round_text = self.HUD_font.render("Night: " + str(self.round_number), True, WHITE)
        round_rect = round_text.get_rect()
        round_rect.topright = (WINDOW_WIDTH - 10, WINDOW_HEIGHT - 50)

        time_text = self.HUD_font.render("Sunrise In: " + str(self.round_time), True, WHITE)
        time_rect = time_text.get_rect()
        time_rect.topright = (WINDOW_WIDTH - 10, WINDOW_HEIGHT - 25)

        # draw the HUD
        display_surface.blit(score_text, score_rect)
        display_surface.blit(health_text, health_rect)
        display_surface.blit(title_text, title_rect)
        display_surface.blit(round_text, round_rect)
        display_surface.blit(time_text, time_rect)

    def add_zombie(self):
        # check to add a zombie every sec
        if self.frame_count % FPS == 0:
            # add a zombie if zombie creation time pass
            if self.round_time % self.zombie_creation_time == 0:
                zombie = Zombie(self.platform_group, self.portal_group, self.round_number, self.round_number + 1)
                self.zombie_group.add(zombie)

    def check_collision(self):
        # check if bullet hit zombie
        collision_dict = pygame.sprite.groupcollide(self.bullet_group, self.zombie_group, True, False)
        if collision_dict:
            for zombies in collision_dict.values():
                for zombie in zombies:
                    zombie.hit_sound.play()
                    zombie.is_dead = True
                    zombie.animate_death = True

        # check if player collides with zombies
        collision_list = pygame.sprite.spritecollide(self.player, self.zombie_group, False)
        if collision_list:
            for zombie in collision_list:
                # the zombie is dead
                if zombie.is_dead:
                    zombie.kick_sound.play()
                    zombie.kill()
                    self.score += 25

                    ruby = Ruby(self.platform_group, self.portal_group)
                    self.ruby_group.add(ruby)
                # the zombie isnt dead, player take damage
                else:
                    self.player.health -= 20
                    self.player.hit_sound.play()
                    # move the player to stop taking damage
                    self.player.position.x -= 256 * zombie.direction
                    self.player.rect.bottomleft = self.player.position

        # check if a player collide with a ruby
        if pygame.sprite.spritecollide(self.player, self.ruby_group, True):
            self.ruby_pickup_sound.play()
            self.score += 100
            self.player.health += 10
            if self.player.health > self.player.STARTING_HEALTH:
                self.player.health = self.player.STARTING_HEALTH

        # check if a living zombie collide with a ruby
        for zombie in self.zombie_group:
            if zombie.is_dead == False:
                if pygame.sprite.spritecollide(zombie, self.ruby_group, True):
                    self.lost_ruby_sound.play()
                    zombie = Zombie(self.platform_group, self.portal_group, self.round_number, self.round_number + 5)
                    self.zombie_group.add(zombie)

    def check_round_completion(self):
        # check if the player survive the night

        if self.round_time == 0:
            self.start_new_round()
            self.change_tile_asset()

    def change_tile_asset(self):
        global bg_img
        if self.round_number in self.asset_paths:
            paths = self.asset_paths[self.round_number]
            for tile in self.tile_group:
                if isinstance(tile, Tile) and tile.image_int in range(1, 6):
                    tile.image_path = paths["images"][tile.image_int - 1]
                    if tile.image_int != 1:
                        tile.sub_group.add(tile)
                    tile.main_group.add(tile)
                    tile.image = pygame.transform.scale(pygame.image.load(tile.image_path), (32, 32))
                    tile.mask = pygame.mask.from_surface(tile.image)

            bg_img_path = paths["backgrounds"][0]
            bg_img = pygame.transform.scale(pygame.image.load(bg_img_path), (WINDOW_WIDTH, WINDOW_HEIGHT))
            display_surface.blit(bg_img, bg_rect)

    def check_game_over(self):
        # check if player lost the game
        if self.player.health <= 0:
            pygame.mixer.music.stop()
            bg = pygame.image.load("images/stars_2.png")
            self.pause_game("FINAL SCORE: " + str(self.player.health), "PRESS ENTER TO PLAY AGAIN...", bg)
            self.reset_game()

    def start_new_round(self):
        self.round_number += 1

        # decrease zombie creation time to get more zombies
        if self.round_number < self.STARTING_ZOMBIE_CREATION_TIME:
            self.zombie_creation_time -= 1

        # reset round values
        self.round_time = self.STARTING_ROUND_TIME
        self.zombie_group.empty()
        self.ruby_group.empty()
        self.bullet_group.empty()
        self.player.reset()
        bg = pygame.image.load("images/stars.jpg")
        self.pause_game("YOU SURVIVED THE NIGHT!", "PRESS ENTER TO CONTINUE...", bg)

    def setting_screen(self, main_text, sub_text, background):
        global running
        global volume
        pygame.mixer.music.pause()
        # set colors
        WHITE = (255, 255, 255)
        BLACK = (0, 0, 0)
        GREEN = (134, 192, 108)

        # main text
        main_text = self.HUD_font.render(main_text, True, GREEN)
        main_rect = main_text.get_rect()
        main_rect.center = (WINDOW_WIDTH // 2, 250)
        # sub text
        sub_text = self.HUD_font.render(sub_text, True, GREEN)
        sub_rect = sub_text.get_rect()
        sub_rect.center = (WINDOW_WIDTH // 2, 350)
        # mute icon
        # mute
        mute_img = pygame.transform.scale(pygame.image.load("images/volume_muted.png"), (64, 64))
        mute_img_rect = mute_img.get_rect()
        mute_img_rect.center = (WINDOW_WIDTH // 2 + 70, 250)
        # unmute
        unmute_img = pygame.transform.scale(pygame.image.load("images/volume_normal.png"), (64, 64))
        unmute_img_rect = unmute_img.get_rect()
        unmute_img_rect.center = (WINDOW_WIDTH // 2 + 70, 250)
        # current
        mute_image = pygame.transform.scale(unmute_img, (64, 64))
        mute_rect = mute_image.get_rect()
        mute_rect.center = (WINDOW_WIDTH // 2 + 70, 250)

        # volume icon
        # up
        vol_up_img = pygame.transform.scale(pygame.image.load("images/plus.png"), (32, 32))
        vol_up_rect = vol_up_img.get_rect()
        vol_up_rect.center = (WINDOW_WIDTH // 2 + 70, 350)
        # down
        vol_down_img = pygame.transform.scale(pygame.image.load("images/minus.png"), (32, 32))
        vol_down_rect = vol_down_img.get_rect()
        vol_down_rect.center = (WINDOW_WIDTH // 2 + 110, 350)

        # display the pause text
        pause_img = pygame.transform.scale(background, (WINDOW_WIDTH, WINDOW_HEIGHT))
        pause_rect = pause_img.get_rect()
        pause_rect.topleft = (0, 0)
        display_surface.blit(pause_img, bg_rect)
        display_surface.blit(main_text, main_rect)
        if pygame.mixer.music.get_volume() == 0:
            display_surface.blit(mute_img, mute_img_rect)
        else:
            display_surface.blit(unmute_img, unmute_img_rect)
        display_surface.blit(sub_text, sub_rect)
        display_surface.blit(vol_up_img, vol_up_rect)
        display_surface.blit(vol_down_img, vol_down_rect)
        pygame.display.update()

        # pause the game until user hit enter
        is_pause = True
        is_mute = False
        while is_pause:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    # user wants to continue
                    if event.key == pygame.K_RETURN:
                        is_pause = False
                        pygame.mixer.music.unpause()
                # user wants to quit
                if event.type == pygame.QUIT:
                    is_pause = False
                    running = False
                    pygame.mixer.music.stop()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    if mute_rect.collidepoint(mouse_x, mouse_y):
                        if pygame.mixer.music.get_volume() == 0:
                            pygame.mixer.music.set_volume(0.5)
                            display_surface.blit(mute_img, mute_img_rect)
                        else:
                            pygame.mixer.music.set_volume(0)
                            display_surface.blit(unmute_img, unmute_img_rect)
                        pygame.display.update()
                    if vol_up_rect.collidepoint(mouse_x, mouse_y):
                        if volume < 0.5:
                            volume += 0.1
                        else:
                            volume = 0.5
                        pygame.mixer.music.set_volume(volume)
                        print("volume up", volume)
                    if vol_down_rect.collidepoint(mouse_x, mouse_y):
                        if volume <= 0:
                            volume = 0
                        else:
                            volume -= 0.1
                        pygame.mixer.music.set_volume(volume)
                        print("volume down", volume)

    def pause_game(self, main_text, sub_text, background, image="", is_menu=False):
        global running

        pygame.mixer.music.pause()

        # set colors
        WHITE = (255, 255, 255)
        BLACK = (0, 0, 0)
        GREEN = (134, 192, 108)
        PALEGREEN = (205, 221, 179)
        # load font
        menu_font = pygame.font.Font("fonts/LowresPixel-Regular.otf", 48)

        # display the pause text
        pause_img = pygame.transform.scale(background, (WINDOW_WIDTH, WINDOW_HEIGHT))
        pause_rect = pause_img.get_rect()
        pause_rect.topleft = (0, 0)
        display_surface.blit(pause_img, bg_rect)
        if is_menu:
            main_text = menu_font.render(main_text, True, PALEGREEN)
            main_rect = main_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 100))
            display_surface.blit(main_text, main_rect)

            menu_text = menu_font.render(sub_text, True, PALEGREEN)
            menu_rect = menu_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 180))
            display_surface.blit(menu_text, menu_rect)
        else:
            main_text = self.title_font.render(main_text, True, GREEN)
            main_rect = main_text.get_rect()
            main_rect.center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
            display_surface.blit(main_text, main_rect)

            sub_text = self.HUD_font.render(sub_text, True, WHITE)
            sub_rect = sub_text.get_rect()
            sub_rect.center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 64)
            display_surface.blit(sub_text, sub_rect)
        if image != "":
            image = pygame.transform.scale(image, (400, 400))
            image_rect = image.get_rect()
            image_rect.center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 100)
            display_surface.blit(image, image_rect)
        pygame.display.update()

        # pause the game until user hit enter
        is_pause = True
        while is_pause:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    # user wants to continue
                    if event.key == pygame.K_RETURN:
                        is_pause = False
                        pygame.mixer.music.unpause()
                # user wants to quit
                if event.type == pygame.QUIT:
                    is_pause = False
                    running = False
                    pygame.mixer.music.stop()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    if is_menu:
                        if menu_rect.collidepoint(mouse_x, mouse_y):
                            pygame.quit()
                            sys.exit()
                        if main_rect.collidepoint(mouse_x, mouse_y):
                            is_pause = False

    def reset_game(self):
        # reset game values
        self.score = 0
        self.round_number = 1
        self.round_time = self.STARTING_ROUND_TIME
        self.zombie_creation_time = self.STARTING_ZOMBIE_CREATION_TIME

        # reset the player
        self.player.health = self.player.STARTING_HEALTH
        self.player.reset()

        # reset tile map asset
        global bg_img
        for tile in self.tile_group:
            if isinstance(tile, Tile):
                if tile.image_int == 1:
                    tile.image_path = "images/tiles/Tile_1.png"
                elif tile.image_int == 2:
                    tile.image_path = "images/tiles/SewerTile_2.png"
                    tile.sub_group.add(tile)
                elif tile.image_int == 3:
                    tile.image_path = "images/tiles/SewerTile_3.png"
                    tile.sub_group.add(tile)
                elif tile.image_int == 4:
                    tile.image_path = "images/tiles/SewerTile_4.png"
                    tile.sub_group.add(tile)
                elif tile.image_int == 5:
                    tile.image_path = "images/tiles/SewerTile_5.png"
                    tile.sub_group.add(tile)
                tile.main_group.add(tile)
                tile.image = pygame.transform.scale(pygame.image.load(tile.image_path), (32, 32))
                tile.mask = pygame.mask.from_surface(tile.image)
            # loading assets
            bg_img = pygame.transform.scale(pygame.image.load("images/background_4.jpg"), (WINDOW_WIDTH, WINDOW_HEIGHT))
            # blit the bg
            display_surface.blit(bg_img, bg_rect)

        # empty spite groups
        self.zombie_group.empty()
        self.ruby_group.empty()
        self.bullet_group.empty()

        pygame.mixer.music.play(-1, 0.0)

class Tile(pygame.sprite.Sprite):
    # class to represent a 32x32 pixel area
    def __init__(self, x, y, image_int, space, main_group, sub_group=""):
        super().__init__()

        self.image_int = image_int
        self.sub_group = sub_group
        self.main_group = main_group

        # Load the image based on image_int
        if image_int == 1:
            image_path = "images/tiles/Tile_1.png"
        elif image_int == 2:
            image_path = "images/tiles/SewerTile_2.png"
            sub_group.add(self)
        elif image_int == 3:
            image_path = "images/tiles/SewerTile_3.png"
            sub_group.add(self)
        elif image_int == 4:
            image_path = "images/tiles/SewerTile_4.png"
            sub_group.add(self)
        elif image_int == 5:
            image_path = "images/tiles/SewerTile_5.png"
            sub_group.add(self)

        # Load and scale the image
        self.image = pygame.transform.scale(pygame.image.load(image_path), (32, 32))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

        # Create a Pymunk body and shape for collisions
        self.body = pymunk.Body(body_type=pymunk.Body.STATIC)
        self.body.position = pymunk.Vec2d(x, y)
        self.shape = pymunk.Poly.create_box(self.body, (32, 32))
        self.shape.elasticity = 0.5  # Set elasticity for collisions

        # Create a mask for better collisions
        self.mask = pygame.mask.from_surface(self.image)

        # Add the tile to the space
        space.add(self.body, self.shape)

        # Add the tile to the main group
        main_group.add(self)

class Player(pygame.sprite.Sprite):
    # class the use can control
    def __init__(self, x, y, platform_group, portal_group, bullet_group):
        super().__init__()

        # set constant variables
        self.HORIZONTAL_ACCELERATION = 2
        self.HORIZONTAL_FRICTION = 0.25
        self.VERTICAL_ACCELERATION = 0.8  # gravity
        self.VERTICAL_JUMP_SPEED = 18  # how high player jump
        self.STARTING_HEALTH = 100

        # animation frames
        self.move_right_sprites = []
        self.move_left_sprites = []
        self.idle_right_sprites = []
        self.idle_left_sprites = []
        self.jump_right_sprites = []
        self.jump_left_sprites = []
        self.attack_right_sprites = []
        self.attack_left_sprites = []

        # moving right
        self.move_right_sprites.append(
            pygame.transform.scale(pygame.image.load("images/player/run/Walk_1.png"), (64, 64)))
        self.move_right_sprites.append(
            pygame.transform.scale(pygame.image.load("images/player/run/Walk_2.png"), (64, 64)))
        self.move_right_sprites.append(
            pygame.transform.scale(pygame.image.load("images/player/run/Walk_3.png"), (64, 64)))
        self.move_right_sprites.append(
            pygame.transform.scale(pygame.image.load("images/player/run/Walk_4.png"), (64, 64)))
        # moving left
        for sprite in self.move_right_sprites:
            self.move_left_sprites.append(pygame.transform.flip(sprite, True, False))

        # idle
        self.idle_right_sprites.append(
            pygame.transform.scale(pygame.image.load("images/player/idle/Idle_1.png"), (64, 64)))
        self.idle_right_sprites.append(
            pygame.transform.scale(pygame.image.load("images/player/idle/Idle_2.png"), (64, 64)))
        for sprite in self.idle_right_sprites:
            self.idle_left_sprites.append(pygame.transform.flip(sprite, True, False))

        # jump
        self.jump_right_sprites.append(
            pygame.transform.scale(pygame.image.load("images/player/run/Walk_1.png"), (64, 64)))
        self.jump_right_sprites.append(
            pygame.transform.scale(pygame.image.load("images/player/run/Walk_2.png"), (64, 64)))
        self.jump_right_sprites.append(
            pygame.transform.scale(pygame.image.load("images/player/run/Walk_3.png"), (64, 64)))
        self.jump_right_sprites.append(
            pygame.transform.scale(pygame.image.load("images/player/run/Walk_4.png"), (64, 64)))
        for sprite in self.jump_right_sprites:
            self.jump_left_sprites.append(pygame.transform.flip(sprite, True, False))

        # attack
        self.attack_right_sprites.append(
            pygame.transform.scale(pygame.image.load("images/player/attack/Shoot_1.png"), (64, 64)))
        self.attack_right_sprites.append(
            pygame.transform.scale(pygame.image.load("images/player/attack/Shoot_2.png"), (64, 64)))
        self.attack_right_sprites.append(
            pygame.transform.scale(pygame.image.load("images/player/attack/Shoot_3.png"), (64, 64)))
        self.attack_right_sprites.append(
            pygame.transform.scale(pygame.image.load("images/player/attack/Shoot_4.png"), (64, 64)))
        for sprite in self.attack_right_sprites:
            self.attack_left_sprites.append(pygame.transform.flip(sprite, True, False))

        # load images and get rect
        self.current_sprite = 0
        self.image = self.idle_right_sprites[self.current_sprite]
        self.rect = self.image.get_rect()
        self.rect.bottomleft = (x, y)

        # attach sprite groups
        self.platform_group = platform_group
        self.portal_group = portal_group
        self.bullet_group = bullet_group

        # animation booleans
        self.animate_jump = False
        self.animate_fire = False

        # load sounds
        self.jump_sound = pygame.mixer.Sound("sounds/jump_sound.wav")
        self.jump_sound.set_volume(volume)
        self.slash_sound = pygame.mixer.Sound("sounds/slash_sound.wav")
        self.slash_sound.set_volume(volume)
        self.portal_sound = pygame.mixer.Sound("sounds/portal_sound.wav")
        self.portal_sound.set_volume(volume)
        self.hit_sound = pygame.mixer.Sound("sounds/player_hit.wav")
        self.hit_sound.set_volume(volume)

        # kinematics vectors
        self.position = vector(x, y)
        self.velocity = vector(0, 0)
        self.acceleration = vector(0, self.VERTICAL_ACCELERATION)

        # set initial player values
        self.health = self.STARTING_HEALTH
        self.starting_x = x
        self.starting_y = y

    def update(self):
        self.move()
        self.check_collision()
        self.check_animation()

        # update the players mask
        self.mask = pygame.mask.from_surface(self.image)

    def move(self):
        # set the acceleration vector
        self.acceleration = vector(0, self.VERTICAL_ACCELERATION)

        # check if user is pressing a key
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.acceleration.x = -1 * self.HORIZONTAL_ACCELERATION
            self.animate(self.move_left_sprites, .15)
        elif keys[pygame.K_RIGHT]:
            self.acceleration.x = self.HORIZONTAL_ACCELERATION
            self.animate(self.move_right_sprites, .15)
        else:
            if self.velocity.x > 0:
                self.animate(self.idle_right_sprites, .05)
            else:
                self.animate(self.idle_left_sprites, .05)

        # calculate physics
        self.acceleration.x -= self.velocity.x * self.HORIZONTAL_FRICTION
        self.velocity += self.acceleration  # v = u + at
        self.position += self.velocity + 0.5 * self.acceleration  # s = ut + 0.5at^2

        # update rect base on calculation vector and wrap around movement
        if self.position.x < 0:
            self.position.x = WINDOW_WIDTH
        elif self.position.x > WINDOW_WIDTH:
            self.position.x = 0

        self.rect.bottomleft = self.position

    def check_collision(self):
        # check collision with platform and portal when falling down
        if self.velocity.y > 0:
            collided_platforms = pygame.sprite.spritecollide(self, self.platform_group, False,
                                                             pygame.sprite.collide_mask)
            if collided_platforms:
                self.position.y = collided_platforms[0].rect.top + 5
                self.velocity.y = 0

        # collision if jump up
        if self.velocity.y < 0:
            collided_platforms = pygame.sprite.spritecollide(self, self.platform_group, False,
                                                             pygame.sprite.collide_mask)
            if collided_platforms:
                self.velocity.y = 0
                while pygame.sprite.spritecollide(self, self.platform_group, False):
                    self.position.y += 1
                    self.rect.bottomleft = self.position

        # check collision with portals
        if pygame.sprite.spritecollide(self, self.portal_group, False):
            self.portal_sound.play()
            # determine which portal user gonna transport to
            # left and right
            if self.position.x > WINDOW_WIDTH // 2:
                self.position.x = 86
            else:
                self.position.x = WINDOW_WIDTH - 150
            # top and bot
            if self.position.y > WINDOW_HEIGHT // 2:
                self.position.y = 64
            else:
                self.position.y = WINDOW_HEIGHT - 132

            self.rect.bottomleft = self.position

    def check_animation(self):
        # check to se if jump/fire animations should run
        if self.animate_jump:
            if self.velocity.x > 0:
                self.animate(self.jump_right_sprites, .1)
            else:
                self.animate(self.jump_left_sprites, .1)

        # animate the player attack
        if self.animate_fire:
            if self.velocity.x > 0:
                self.animate(self.attack_right_sprites, .05)
            else:
                self.animate(self.attack_left_sprites, .05)

    def jump(self):
        # only jump if on a platform
        if pygame.sprite.spritecollide(self, self.platform_group, False):
            self.jump_sound.play()
            self.velocity.y = -1 * self.VERTICAL_JUMP_SPEED
            self.animate_jump = True

    def fire(self):
        self.slash_sound.play()
        Bullet(self.rect.centerx, self.rect.centery, self.bullet_group, self, my_space)
        self.animate_fire = True

    def reset(self):
        # reset player position
        self.velocity = vector(0, 0)
        self.position = vector(self.starting_x, self.starting_y)
        self.rect.bottomleft = self.position

    def animate(self, sprite_list, speed):
        if self.current_sprite < len(sprite_list) - 1:
            self.current_sprite += speed
        else:
            self.current_sprite = 0
            # end the jump animation
            if self.animate_jump:
                self.animate_jump = False
            # end the attack animation
            if self.animate_fire:
                self.animate_fire = False

        self.image = sprite_list[int(self.current_sprite)]

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, bullet_group, player, space):
        super().__init__()

        # set constant variables
        self.VELOCITY = 5
        self.RANGE = 500

        # load image and get rect
        if player.velocity.x > 0:
            self.image = pygame.transform.scale(pygame.image.load("images/player/Bullet.png"), (64, 64))
        else:
            self.image = pygame.transform.scale(
                pygame.transform.flip(pygame.image.load("images/player/Bullet.png"), True, False), (64, 64))
            self.VELOCITY = -1 * self.VELOCITY

        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

        self.starting_x = x

        bullet_group.add(self)

        # Create a Pymunk body and shape for the bullet
        self.body = pymunk.Body(body_type=pymunk.Body.DYNAMIC)
        self.body.position = pymunk.Vec2d(x, y)
        self.shape = pymunk.Circle(self.body, 16)  # Assume radius 16 for the bullet
        self.shape.elasticity = 0.5  # Set elasticity for collisions

        # Add the bullet to the space
        space.add(self.body, self.shape)

    def update(self):
        self.rect.x += self.VELOCITY

        # if the bullet pass the range, kill it
        if abs(self.rect.x - self.starting_x) > self.RANGE:
            self.kill()

class Zombie(pygame.sprite.Sprite):
    # enemy class that moves across the screen
    def __init__(self, platform_group, portal_group, min_speed, max_speed):
        super().__init__()

        # set constant variables
        self.VERTICAL_ACCELERATION = 3  # gravity
        self.RISE_TIME = 2

        # animation frames
        self.walk_right_sprites = []
        self.walk_left_sprites = []
        self.die_right_sprites = []
        self.die_left_sprites = []
        self.rise_right_sprites = []
        self.rise_left_sprites = []

        type = random.randint(0, 1)
        if type == 0:
            # Walking
            self.walk_right_sprites.append \
                (pygame.transform.scale(pygame.image.load("images/zombie/boy/walk/Walk_1.png"), (64, 64)))
            self.walk_right_sprites.append(
                pygame.transform.scale(pygame.image.load("images/zombie/boy/walk/Walk_2.png"), (64, 64)))
            self.walk_right_sprites.append(
                pygame.transform.scale(pygame.image.load("images/zombie/boy/walk/Walk_3.png"), (64, 64)))
            self.walk_right_sprites.append(
                pygame.transform.scale(pygame.image.load("images/zombie/boy/walk/Walk_4.png"), (64, 64)))
            self.walk_right_sprites.append(
                pygame.transform.scale(pygame.image.load("images/zombie/boy/walk/Walk_5.png"), (64, 64)))
            self.walk_right_sprites.append(
                pygame.transform.scale(pygame.image.load("images/zombie/boy/walk/Walk_6.png"), (64, 64)))
            self.walk_right_sprites.append(
                pygame.transform.scale(pygame.image.load("images/zombie/boy/walk/Walk_7.png"), (64, 64)))
            self.walk_right_sprites.append(
                pygame.transform.scale(pygame.image.load("images/zombie/boy/walk/Walk_8.png"), (64, 64)))
            self.walk_right_sprites.append(
                pygame.transform.scale(pygame.image.load("images/zombie/boy/walk/Walk_9.png"), (64, 64)))
            self.walk_right_sprites.append(
                pygame.transform.scale(pygame.image.load("images/zombie/boy/walk/Walk_10.png"), (64, 64)))
            for sprite in self.walk_right_sprites:
                self.walk_left_sprites.append(pygame.transform.flip(sprite, True, False))

            # Dying
            self.die_right_sprites.append(
                pygame.transform.scale(pygame.image.load("images/zombie/boy/dead/Death_1.png"), (64, 64)))
            self.die_right_sprites.append(
                pygame.transform.scale(pygame.image.load("images/zombie/boy/dead/Death_2.png"), (64, 64)))
            self.die_right_sprites.append(
                pygame.transform.scale(pygame.image.load("images/zombie/boy/dead/Death_3.png"), (64, 64)))
            self.die_right_sprites.append(
                pygame.transform.scale(pygame.image.load("images/zombie/boy/dead/Death_4.png"), (64, 64)))
            self.die_right_sprites.append(
                pygame.transform.scale(pygame.image.load("images/zombie/boy/dead/Death_5.png"), (64, 64)))
            self.die_right_sprites.append(
                pygame.transform.scale(pygame.image.load("images/zombie/boy/dead/Death_6.png"), (64, 64)))
            self.die_right_sprites.append(
                pygame.transform.scale(pygame.image.load("images/zombie/boy/dead/Death_7.png"), (64, 64)))
            for sprite in self.die_right_sprites:
                self.die_left_sprites.append(pygame.transform.flip(sprite, True, False))

            # Rising
            self.rise_right_sprites.append(
                pygame.transform.scale(pygame.image.load("images/zombie/boy/dead/Death_7.png"), (64, 64)))
            self.rise_right_sprites.append(
                pygame.transform.scale(pygame.image.load("images/zombie/boy/dead/Death_6.png"), (64, 64)))
            self.rise_right_sprites.append(
                pygame.transform.scale(pygame.image.load("images/zombie/boy/dead/Death_5.png"), (64, 64)))
            self.rise_right_sprites.append(
                pygame.transform.scale(pygame.image.load("images/zombie/boy/dead/Death_4.png"), (64, 64)))
            self.rise_right_sprites.append(
                pygame.transform.scale(pygame.image.load("images/zombie/boy/dead/Death_3.png"), (64, 64)))
            self.rise_right_sprites.append(
                pygame.transform.scale(pygame.image.load("images/zombie/boy/dead/Death_2.png"), (64, 64)))
            self.rise_right_sprites.append(
                pygame.transform.scale(pygame.image.load("images/zombie/boy/dead/Death_1.png"), (64, 64)))
            for sprite in self.rise_right_sprites:
                self.rise_left_sprites.append(pygame.transform.flip(sprite, True, False))
        else:
            # Walking
            self.walk_left_sprites.append(
                pygame.transform.scale(pygame.image.load("images/zombie/skeleton/walk/SkeletonWalk_1.png"), (64, 64)))
            self.walk_left_sprites.append(
                pygame.transform.scale(pygame.image.load("images/zombie/skeleton/walk/SkeletonWalk_2.png"), (64, 64)))
            self.walk_left_sprites.append(
                pygame.transform.scale(pygame.image.load("images/zombie/skeleton/walk/SkeletonWalk_3.png"), (64, 64)))
            self.walk_left_sprites.append(
                pygame.transform.scale(pygame.image.load("images/zombie/skeleton/walk/SkeletonWalk_4.png"), (64, 64)))
            self.walk_left_sprites.append(
                pygame.transform.scale(pygame.image.load("images/zombie/skeleton/walk/SkeletonWalk_5.png"), (64, 64)))
            self.walk_left_sprites.append(
                pygame.transform.scale(pygame.image.load("images/zombie/skeleton/walk/SkeletonWalk_6.png"), (64, 64)))
            for sprite in self.walk_left_sprites:
                self.walk_right_sprites.append(pygame.transform.flip(sprite, True, False))

            # Dying
            self.die_right_sprites.append(
                pygame.transform.scale(pygame.image.load("images/zombie/skeleton/dead/SkeletonDead_1.png"), (64, 64)))
            self.die_right_sprites.append(
                pygame.transform.scale(pygame.image.load("images/zombie/skeleton/dead/SkeletonDead_2.png"), (64, 64)))
            self.die_right_sprites.append(
                pygame.transform.scale(pygame.image.load("images/zombie/skeleton/dead/SkeletonDead_3.png"), (64, 64)))
            self.die_right_sprites.append(
                pygame.transform.scale(pygame.image.load("images/zombie/skeleton/dead/SkeletonDead_4.png"), (64, 64)))
            self.die_right_sprites.append(
                pygame.transform.scale(pygame.image.load("images/zombie/skeleton/dead/SkeletonDead_5.png"), (64, 64)))
            self.die_right_sprites.append(
                pygame.transform.scale(pygame.image.load("images/zombie/skeleton/dead/SkeletonDead_6.png"), (64, 64)))
            for sprite in self.die_right_sprites:
                self.die_left_sprites.append(pygame.transform.flip(sprite, True, False))

            # Rising
            self.rise_right_sprites.append(
                pygame.transform.scale(pygame.image.load("images/zombie/skeleton/dead/SkeletonDead_6.png"), (64, 64)))
            self.rise_right_sprites.append(
                pygame.transform.scale(pygame.image.load("images/zombie/skeleton/dead/SkeletonDead_5.png"), (64, 64)))
            self.rise_right_sprites.append(
                pygame.transform.scale(pygame.image.load("images/zombie/skeleton/dead/SkeletonDead_4.png"), (64, 64)))
            self.rise_right_sprites.append(
                pygame.transform.scale(pygame.image.load("images/zombie/skeleton/dead/SkeletonDead_3.png"), (64, 64)))
            self.rise_right_sprites.append(
                pygame.transform.scale(pygame.image.load("images/zombie/skeleton/dead/SkeletonDead_2.png"), (64, 64)))
            self.rise_right_sprites.append(
                pygame.transform.scale(pygame.image.load("images/zombie/skeleton/dead/SkeletonDead_1.png"), (64, 64)))
            for sprite in self.rise_right_sprites:
                self.rise_left_sprites.append(pygame.transform.flip(sprite, True, False))

        # load an image and get rect
        self.direction = random.choice([-1, 1])

        self.current_sprite = 0
        if self.direction == -1:
            self.image = self.walk_left_sprites[self.current_sprite]
        else:
            self.image = self.walk_right_sprites[self.current_sprite]

        self.rect = self.image.get_rect()
        self.rect.bottomleft = (random.randint(100, WINDOW_WIDTH - 100), -100)

        # attach sprite groups
        self.platform_group = platform_group
        self.portal_group = portal_group

        # animation booleans
        self.animate_death = False
        self.animate_rise = False

        # load sounds
        self.hit_sound = pygame.mixer.Sound("sounds/zombie_hit.wav")
        self.hit_sound.set_volume(volume)
        self.kick_sound = pygame.mixer.Sound("sounds/zombie_kick.wav")
        self.kick_sound.set_volume(volume)
        self.portal_sound = pygame.mixer.Sound("sounds/portal_sound.wav")
        self.portal_sound.set_volume(volume)

        # kinematics vectors
        self.position = vector(self.rect.x, self.rect.y)
        self.velocity = vector(self.direction * random.randint(min_speed, max_speed), 0)
        self.acceleration = vector(0, self.VERTICAL_ACCELERATION)

        # initial zombie values
        self.is_dead = False
        self.round_time = 0
        self.frame_count = 0

    def update(self):
        self.move()
        self.check_collision()
        self.check_animation()

        # determine when zombie rises back form death
        if self.is_dead:
            self.frame_count += 1
            if self.frame_count % FPS == 0:
                self.round_time += 1
                if self.round_time == self.RISE_TIME:
                    self.animate_rise = True
                    # the image of the zombie keep at the last image when it dies
                    # when it rises back, start at index 0
                    self.current_sprite = 0

    def move(self):
        if not self.is_dead:
            if self.direction == -1:
                self.animate(self.walk_left_sprites, .5)
            else:
                self.animate(self.walk_right_sprites, .5)

            self.velocity += self.acceleration
            self.position += self.velocity + 0.5 * self.acceleration

            # update rect base on kinematic calculations
            if self.position.x < 0:
                self.position.x = WINDOW_WIDTH
            elif self.position.x > WINDOW_WIDTH:
                self.position.x = 0

            self.rect.bottomleft = self.position

    def check_collision(self):
        # check collision with platform and portal
        collided_platforms = pygame.sprite.spritecollide(self, self.platform_group, False)
        if collided_platforms:
            self.position.y = collided_platforms[0].rect.top + 1
            self.velocity.y = 0

        # check collision with portals
        if pygame.sprite.spritecollide(self, self.portal_group, False):
            self.portal_sound.play()
            # determine which portal user gonna transport to
            # left and right
            if self.position.x > WINDOW_WIDTH // 2:
                self.position.x = 86
            else:
                self.position.x = WINDOW_WIDTH - 150
            # top and bot
            if self.position.y > WINDOW_HEIGHT // 2:
                self.position.y = 64
            else:
                self.position.y = WINDOW_HEIGHT - 132

            self.rect.bottomleft = self.position

    def check_animation(self):
        # animate the zombie death
        if self.animate_death:
            if self.direction == 1:
                self.animate(self.die_right_sprites, .095)
            else:
                self.animate(self.die_left_sprites, .095)

        # animate the zombie rise
        if self.animate_rise:
            if self.direction == 1:
                self.animate(self.rise_right_sprites, .095)
            else:
                self.animate(self.rise_left_sprites, .095)

    def animate(self, sprite_list, speed):
        if self.current_sprite < len(sprite_list) - 1:
            self.current_sprite += speed
        else:
            self.current_sprite = 0
            # end the death ani
            if self.animate_death:
                self.current_sprite = len(sprite_list) - 1
                self.animate_death = False
            # end the rise ani
            if self.animate_rise:
                self.animate_rise = False
                self.is_dead = False
                self.frame_count = 0
                self.round_time = 0

        self.image = sprite_list[int(self.current_sprite)]

class RubyMaker(pygame.sprite.Sprite):
    def __init__(self, x, y, main_group, space):
        super().__init__()

        # animation frames
        self.ruby_sprites = []  # a list of pictures

        # rotating
        self.ruby_sprites.append(pygame.transform.scale(pygame.image.load("images/ruby/tile000.png"), (64, 64)))
        self.ruby_sprites.append(pygame.transform.scale(pygame.image.load("images/ruby/tile001.png"), (64, 64)))
        self.ruby_sprites.append(pygame.transform.scale(pygame.image.load("images/ruby/tile002.png"), (64, 64)))
        self.ruby_sprites.append(pygame.transform.scale(pygame.image.load("images/ruby/tile003.png"), (64, 64)))
        self.ruby_sprites.append(pygame.transform.scale(pygame.image.load("images/ruby/tile004.png"), (64, 64)))
        self.ruby_sprites.append(pygame.transform.scale(pygame.image.load("images/ruby/tile005.png"), (64, 64)))

        # load image and get rect
        self.current_sprite = 0
        self.image = self.ruby_sprites[self.current_sprite]
        self.rect = self.image.get_rect()
        self.rect.bottomleft = (x, y)

        # add to the main group to draw
        main_group.add(self)

        # Create a Pymunk body and shape for the ruby
        self.body = pymunk.Body(body_type=pymunk.Body.STATIC)  # Assume the ruby is static
        self.body.position = pymunk.Vec2d(x, y)
        self.shape = pymunk.Circle(self.body, 32)  # Assume radius 32 for the ruby
        self.shape.elasticity = 0.5  # Set elasticity for collisions

        # Add the ruby to the space
        space.add(self.body, self.shape)

    def update(self):
        self.animate(self.ruby_sprites, .25)

    def animate(self, sprite_list, speed):
        if self.current_sprite < len(sprite_list) - 1:
            self.current_sprite += speed
        else:
            self.current_sprite = 0

        self.image = sprite_list[int(self.current_sprite)]

class Ruby(pygame.sprite.Sprite):
    # class that user must collect too earn points
    def __init__(self, platform_group, portal_group):
        super().__init__()

        # set constant variables
        self.VERTICAL_ACCELERATION = 3  # gravity
        self.HORIZONTAL_VELOCITY = 5

        # animation frames
        self.ruby_sprites = []

        # rotating
        self.ruby_sprites.append(pygame.transform.scale(pygame.image.load("images/ruby/tile000.png"), (64, 64)))
        self.ruby_sprites.append(pygame.transform.scale(pygame.image.load("images/ruby/tile001.png"), (64, 64)))
        self.ruby_sprites.append(pygame.transform.scale(pygame.image.load("images/ruby/tile002.png"), (64, 64)))
        self.ruby_sprites.append(pygame.transform.scale(pygame.image.load("images/ruby/tile003.png"), (64, 64)))
        self.ruby_sprites.append(pygame.transform.scale(pygame.image.load("images/ruby/tile004.png"), (64, 64)))
        self.ruby_sprites.append(pygame.transform.scale(pygame.image.load("images/ruby/tile005.png"), (64, 64)))

        # load image and get rect
        self.current_sprite = 0
        self.image = self.ruby_sprites[self.current_sprite]
        self.rect = self.image.get_rect()
        self.rect.bottomleft = (WINDOW_WIDTH // 2, 100)

        # attach sprites group
        self.platform_group = platform_group
        self.portal_group = portal_group

        # load sound
        self.portal_sound = pygame.mixer.Sound("sounds/portal_sound.wav")
        self.portal_sound.set_volume(volume)

        # Kinematic vectors
        self.position = vector(self.rect.x, self.rect.y)
        self.velocity = vector(random.choice([-1 * self.HORIZONTAL_VELOCITY, self.HORIZONTAL_VELOCITY]), 0)
        self.acceleration = vector(0, self.VERTICAL_ACCELERATION)

    def update(self):
        self.animate(self.ruby_sprites, .25)
        self.move()
        self.check_collision()

    def move(self):
        self.velocity += self.acceleration
        self.position += self.velocity + 0.5 * self.acceleration

        # update rect base on kinematic calculations
        if self.position.x < 0:
            self.position.x = WINDOW_WIDTH
        elif self.position.x > WINDOW_WIDTH:
            self.position.x = 0

        self.rect.bottomleft = self.position

    def check_collision(self):
        collided_platforms = pygame.sprite.spritecollide(self, self.platform_group, False)
        if collided_platforms:
            self.position.y = collided_platforms[0].rect.top + 1
            self.velocity.y = 0

        # check collision with portals
        if pygame.sprite.spritecollide(self, self.portal_group, False):
            self.portal_sound.play()
            # determine which portal user gonna transport to
            # left and right
            if self.position.x > WINDOW_WIDTH // 2:
                self.position.x = 86
            else:
                self.position.x = WINDOW_WIDTH - 150
            # top and bot
            if self.position.y > WINDOW_HEIGHT // 2:
                self.position.y = 64
            else:
                self.position.y = WINDOW_HEIGHT - 132

            self.rect.bottomleft = self.position

    def animate(self, sprite_list, speed):
        if self.current_sprite < len(sprite_list) - 1:
            self.current_sprite += speed
        else:
            self.current_sprite = 0

        self.image = sprite_list[int(self.current_sprite)]

class Portal(pygame.sprite.Sprite):
    # a class that if collided with will transport user
    def __init__(self, x, y, color, portal_group, space):
        super().__init__()

        # animation frames
        self.portal_sprites = []

        # portal animation
        if color == "green":
            # green portal
            self.portal_sprites.append(
                pygame.transform.scale(pygame.image.load("images/portals/green/tile000.png"), (72, 72)))
            self.portal_sprites.append(
                pygame.transform.scale(pygame.image.load("images/portals/green/tile001.png"), (72, 72)))
            self.portal_sprites.append(
                pygame.transform.scale(pygame.image.load("images/portals/green/tile002.png"), (72, 72)))
            self.portal_sprites.append(
                pygame.transform.scale(pygame.image.load("images/portals/green/tile003.png"), (72, 72)))
            self.portal_sprites.append(
                pygame.transform.scale(pygame.image.load("images/portals/green/tile004.png"), (72, 72)))
            self.portal_sprites.append(
                pygame.transform.scale(pygame.image.load("images/portals/green/tile005.png"), (72, 72)))
            self.portal_sprites.append(
                pygame.transform.scale(pygame.image.load("images/portals/green/tile006.png"), (72, 72)))
            self.portal_sprites.append(
                pygame.transform.scale(pygame.image.load("images/portals/green/tile007.png"), (72, 72)))
            self.portal_sprites.append(
                pygame.transform.scale(pygame.image.load("images/portals/green/tile008.png"), (72, 72)))
            self.portal_sprites.append(
                pygame.transform.scale(pygame.image.load("images/portals/green/tile009.png"), (72, 72)))
            self.portal_sprites.append(
                pygame.transform.scale(pygame.image.load("images/portals/green/tile010.png"), (72, 72)))
            self.portal_sprites.append(
                pygame.transform.scale(pygame.image.load("images/portals/green/tile011.png"), (72, 72)))
            self.portal_sprites.append(
                pygame.transform.scale(pygame.image.load("images/portals/green/tile012.png"), (72, 72)))
            self.portal_sprites.append(
                pygame.transform.scale(pygame.image.load("images/portals/green/tile013.png"), (72, 72)))
            self.portal_sprites.append(
                pygame.transform.scale(pygame.image.load("images/portals/green/tile014.png"), (72, 72)))
            self.portal_sprites.append(
                pygame.transform.scale(pygame.image.load("images/portals/green/tile015.png"), (72, 72)))
            self.portal_sprites.append(
                pygame.transform.scale(pygame.image.load("images/portals/green/tile016.png"), (72, 72)))
            self.portal_sprites.append(
                pygame.transform.scale(pygame.image.load("images/portals/green/tile017.png"), (72, 72)))
            self.portal_sprites.append(
                pygame.transform.scale(pygame.image.load("images/portals/green/tile018.png"), (72, 72)))
            self.portal_sprites.append(
                pygame.transform.scale(pygame.image.load("images/portals/green/tile019.png"), (72, 72)))
            self.portal_sprites.append(
                pygame.transform.scale(pygame.image.load("images/portals/green/tile020.png"), (72, 72)))
            self.portal_sprites.append(
                pygame.transform.scale(pygame.image.load("images/portals/green/tile021.png"), (72, 72)))
        else:
            self.portal_sprites.append(
                pygame.transform.scale(pygame.image.load("images/portals/purple/tile000.png"), (72, 72)))
            self.portal_sprites.append(
                pygame.transform.scale(pygame.image.load("images/portals/purple/tile001.png"), (72, 72)))
            self.portal_sprites.append(
                pygame.transform.scale(pygame.image.load("images/portals/purple/tile002.png"), (72, 72)))
            self.portal_sprites.append(
                pygame.transform.scale(pygame.image.load("images/portals/purple/tile003.png"), (72, 72)))
            self.portal_sprites.append(
                pygame.transform.scale(pygame.image.load("images/portals/purple/tile004.png"), (72, 72)))
            self.portal_sprites.append(
                pygame.transform.scale(pygame.image.load("images/portals/purple/tile005.png"), (72, 72)))
            self.portal_sprites.append(
                pygame.transform.scale(pygame.image.load("images/portals/purple/tile006.png"), (72, 72)))
            self.portal_sprites.append(
                pygame.transform.scale(pygame.image.load("images/portals/purple/tile007.png"), (72, 72)))
            self.portal_sprites.append(
                pygame.transform.scale(pygame.image.load("images/portals/purple/tile008.png"), (72, 72)))
            self.portal_sprites.append(
                pygame.transform.scale(pygame.image.load("images/portals/purple/tile009.png"), (72, 72)))
            self.portal_sprites.append(
                pygame.transform.scale(pygame.image.load("images/portals/purple/tile010.png"), (72, 72)))
            self.portal_sprites.append(
                pygame.transform.scale(pygame.image.load("images/portals/purple/tile011.png"), (72, 72)))
            self.portal_sprites.append(
                pygame.transform.scale(pygame.image.load("images/portals/purple/tile012.png"), (72, 72)))
            self.portal_sprites.append(
                pygame.transform.scale(pygame.image.load("images/portals/purple/tile013.png"), (72, 72)))
            self.portal_sprites.append(
                pygame.transform.scale(pygame.image.load("images/portals/purple/tile014.png"), (72, 72)))
            self.portal_sprites.append(
                pygame.transform.scale(pygame.image.load("images/portals/purple/tile015.png"), (72, 72)))
            self.portal_sprites.append(
                pygame.transform.scale(pygame.image.load("images/portals/purple/tile016.png"), (72, 72)))
            self.portal_sprites.append(
                pygame.transform.scale(pygame.image.load("images/portals/purple/tile017.png"), (72, 72)))
            self.portal_sprites.append(
                pygame.transform.scale(pygame.image.load("images/portals/purple/tile018.png"), (72, 72)))
            self.portal_sprites.append(
                pygame.transform.scale(pygame.image.load("images/portals/purple/tile019.png"), (72, 72)))
            self.portal_sprites.append(
                pygame.transform.scale(pygame.image.load("images/portals/purple/tile020.png"), (72, 72)))
            self.portal_sprites.append(
                pygame.transform.scale(pygame.image.load("images/portals/purple/tile021.png"), (72, 72)))

        # load an image and get a rect
        self.current_sprite = random.randint(0, len(self.portal_sprites) - 1)
        self.image = self.portal_sprites[self.current_sprite]
        self.rect = self.image.get_rect()
        self.rect.bottomleft = (x, y)

        # add to the portal group
        portal_group.add(self)

        # Create Pymunk body and shape
        self.body = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
        self.body.position = pymunk.Vec2d(x, y)
        self.shape = pymunk.Poly.create_box(self.body, (self.rect.width, self.rect.height))
        self.shape.elasticity = 0.5

        # Add body and shape to the space
        space.add(self.body, self.shape)

    def update(self):
        self.animate(self.portal_sprites, 0.2)

    def animate(self, sprite_list, speed):
        if self.current_sprite < len(sprite_list) - 1:
            self.current_sprite += speed
        else:
            self.current_sprite = 0

        self.image = sprite_list[int(self.current_sprite)]


# create sprite groups
my_main_tile_group = pygame.sprite.Group()
my_platform_group = pygame.sprite.Group()

my_player_group = pygame.sprite.Group()
my_bullet_group = pygame.sprite.Group()

my_zombie_group = pygame.sprite.Group()

my_portal_group = pygame.sprite.Group()
my_ruby_group = pygame.sprite.Group()

# create the tile map
# 0: no tile, 1: dirt, 2-5: platforms, 6:ruby maker, 7-8: portals, 9: player
# 21 rows and 37 cols
tile_map = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8, 0],
    [4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 5, 0, 0, 0, 6, 0, 0, 0, 3, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 5],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [4, 4, 4, 4, 4, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 4, 4, 4, 4, 4],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7, 0],
    [4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 5, 0, 0, 0, 0, 0, 3, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 4, 4, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
]

# generate tile object from the tile map
for i in range(len(tile_map)):
    for j in range(len(tile_map[i])):
        # dirt tile
        if tile_map[i][j] == 1:
            Tile(j * 32, i * 32, 1, my_space, my_main_tile_group)
        # platform tiles
        elif tile_map[i][j] == 2:
            Tile(j * 32, i * 32, 2, my_space, my_main_tile_group, my_platform_group)
        elif tile_map[i][j] == 3:
            Tile(j * 32, i * 32, 3, my_space, my_main_tile_group, my_platform_group)
        elif tile_map[i][j] == 4:
            Tile(j * 32, i * 32, 4, my_space, my_main_tile_group, my_platform_group)
        elif tile_map[i][j] == 5:
            Tile(j * 32, i * 32, 5, my_space, my_main_tile_group, my_platform_group)
        # ruby maker
        elif tile_map[i][j] == 6:
            RubyMaker(j * 32, i * 32, my_main_tile_group, my_space)
        # portals
        elif tile_map[i][j] == 7:
            Portal(j * 32, i * 32, "green", my_portal_group, my_space)
        elif tile_map[i][j] == 8:
            Portal(j * 32, i * 32, "purple", my_portal_group, my_space)
        # player
        elif tile_map[i][j] == 9:
            my_player = Player(j * 32 - 32, i * 32 + 32, my_platform_group, my_portal_group, my_bullet_group)
            my_player_group.add(my_player)
# loading assets
bg_img = pygame.transform.scale(pygame.image.load("images/background_4.jpg"), (WINDOW_WIDTH, WINDOW_HEIGHT))
bg_rect = bg_img.get_rect()
bg_rect.topleft = (0, 0)

# create a game
main_bg = pygame.image.load("images/main_screen.png")
instruct_bg = pygame.image.load("images/instruction.png")
setting_bg = pygame.image.load("images/setting.png")
my_game = Game(my_player, my_zombie_group, my_platform_group, my_portal_group, my_bullet_group, my_ruby_group,
               my_main_tile_group)
my_game.pause_game("START", "QUIT", main_bg, is_menu=True)
my_game.pause_game("", "", instruct_bg)
pygame.mixer.music.play(-1, 0.0)

# main game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            if event.key == pygame.K_SPACE:
                my_player.jump()
            if event.key == pygame.K_UP:
                my_player.fire()
        keys = pygame.key.get_pressed()
        if keys[pygame.K_i]:
            my_game.pause_game("", "", instruct_bg)
        if keys[pygame.K_s]:
            my_game.setting_screen("Mute", "Volume", setting_bg)
        if keys[pygame.K_m]:
            my_game.pause_game("RESUME", "QUIT", main_bg, is_menu=True)

    # blit the bg
    display_surface.blit(bg_img, bg_rect)

    # draw tiles
    my_main_tile_group.update()
    my_main_tile_group.draw(display_surface)

    # update and draw sprite group
    my_portal_group.update()
    my_portal_group.draw(display_surface)

    my_player_group.update()
    my_player_group.draw(display_surface)

    my_bullet_group.update()
    my_bullet_group.draw(display_surface)

    my_zombie_group.update()
    my_zombie_group.draw(display_surface)

    my_ruby_group.update()
    my_ruby_group.draw(display_surface)

    # update and draw the game
    my_game.update()
    my_game.draw()

    # Cập nhật Pymunk Space
    my_space.step(1 / 60.0)

    # Update display
    pygame.display.update()
    clock.tick(FPS)

# End game
pygame.quit()
