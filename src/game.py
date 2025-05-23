import sys

import pygame as pg
from pytmx.util_pygame import load_pygame

from entities.base_entity import Entity
from settings import *


class Game:
    """
    Класс, представляющий собой объект игры.

    В атрибутах содержит все сущности на карте (игрок, враги),
    объект экрана, группу sprites и различные вспомогательные переменные
    """

    def __init__(self) -> None:
        """
        Инициализация игры.
        Спавн игрока и противников
        """

        pg.init()
        pg.display.set_caption('Tower Game')
        pg.mixer.init()
        self.music_path = '../sounds/music/веселая, можно в локации перед боссом.mp3'

        self.jump_sound = pg.mixer.Sound(PLAYER_JUMP_SOUND)
        self.jump_sound.set_volume(0.8)

        self.attack_sound = pg.mixer.Sound(PLAYER_ATTACK_SOUND)
        self.attack_sound.set_volume(0.8)

        self.player_damaged = pg.mixer.Sound(PLAYER_DAMAGED_SOUND)
        self.attack_sound.set_volume(0.1)

        self.death_sound = pg.mixer.Sound(SLIME_DEATH_SOUND)
        self.death_sound.set_volume(0.1)

        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        self.clock = pg.time.Clock()
        self.sprites = pg.sprite.Group()

        self.tmx_data = load_pygame(LEVEL1_PATH)
        self.background_image_fd = pg.image.load(BACKGROUND_IMAGE_0).convert()
        self.background_image_fwd = pg.image.load(BACKGROUND_IMAGE_1).convert()

        self.player = Entity(
            'player',
            self.sprites,
            PLAYER_START_POS[0] * self.tmx_data.tilewidth,
            PLAYER_START_POS[1] * self.tmx_data.tileheight,
            PLAYER_IMAGE,
            PLAYER_HEALTH,
            PLAYER_DAMAGE,
            PLAYER_FRAMES,
            PLAYER_ATTACK_FRAMES,
        )

        self.enemy_slime_1 = Entity(
            'slime_1',
            self.sprites,
            SLIME_1_START_POS[0] * self.tmx_data.tilewidth,
            SLIME_1_START_POS[1] * self.tmx_data.tileheight,
            SLIME_IMAGE,
            SLIME_HEALTH,
            SLIME_DAMAGE,
            SLIME_FRAMES,
            SLIME_ATTACK_FRAMES,
        )

        self.enemy_slime_2 = Entity(
            'slime_2',
            self.sprites,
            SLIME_2_START_POS[0] * self.tmx_data.tilewidth,
            SLIME_2_START_POS[1] * self.tmx_data.tileheight,
            SLIME_IMAGE,
            SLIME_HEALTH,
            SLIME_DAMAGE,
            SLIME_FRAMES,
            SLIME_ATTACK_FRAMES,
        )

        self.enemy_slime_3 = Entity(
            'slime_3',
            self.sprites,
            SLIME_3_START_POS[0] * self.tmx_data.tilewidth,
            SLIME_3_START_POS[1] * self.tmx_data.tileheight,
            SLIME_IMAGE,
            SLIME_HEALTH,
            SLIME_DAMAGE,
            SLIME_FRAMES,
            SLIME_ATTACK_FRAMES,
        )

        self.map_width = self.tmx_data.width * self.tmx_data.tilewidth
        self.map_height = self.tmx_data.height * self.tmx_data.tileheight

        self.player.health = PLAYER_HEALTH
        self.player_max_health = PLAYER_HEALTH
        self.player_invincible = False
        self.player_invincible_timer = 0
        self.game_over = False
        self.fade_alpha = 0

        self.has_double_jump = False
        self.ability_notification = ""
        self.notification_timer = 0
        self.item_sound = pg.mixer.Sound('../sounds/подобран прикол.mp3')
        self.item_sound.set_volume(0.6)
        self.chest_sound = pg.mixer.Sound('../sounds/открывание железного замка.mp3')
        self.chest_sound.set_volume(0.6)

        # Объекты для ромба и сундука
        self.diamond = Entity(
            'diamond',
            self.sprites,
            diamond_pos[0] * self.tmx_data.tilewidth,
            diamond_pos[1] * self.tmx_data.tileheight,
            diamond_image,
            0,
            0,
            [diamond_image],  # список кадров, из одного элемента
            []
        )

        self.has_sword = False
        self.chest_opened = False

        self.chest = Entity(
            'chest',
            self.sprites,
            chest_pos[0] * self.tmx_data.tilewidth,
            chest_pos[1] * self.tmx_data.tileheight,
            chest_image,  # статичное изображение
            0, 0,
            [chest_image],  # walk_frames (минимум 1 кадр)
            []  # attack_frames
        )

        # Координаты шипов
        self.danger_zones = [
            (880, 112, 64, 16),
            (544, 160, 32, 16),
            (352, 272, 192, 16),
            (256, 448, 16, 32),
            (752, 272, 32, 16),
            (320, 480, 48, 16)
            ]

        self.danger_rects = [pg.Rect(x, y, w, h) for x, y, w, h in self.danger_zones]

        self.victory = False
        self.victory_image = pg.image.load('../img/ui/end_screen.png').convert()
        self.next_image = pg.image.load('../img/ui/хихи.png').convert()
        self.victory_music = pg.mixer.Sound('../sounds/menu.mp3')
        self.victory_music.set_volume(0.6)

        self.camera = QuarterCamera(self, self.map_width, self.map_height)

        self.bg_surf = pg.Surface((self.map_width, self.map_height))
        self.bg_surf.blit(pg.transform.scale(self.background_image_fd, (self.map_width, self.map_height // 2)),
                          (0, self.map_height // 2))
        self.bg_surf.blit(pg.transform.scale(self.background_image_fwd, (self.map_width, self.map_height // 2)), (0, 0))

        self.current_message = ""
        self.message_timer = 0
        self.message_font = pg.font.Font(None, 36)
        self.showed_messages = {
            "start": False,
            "double_jump": False,
            "sword": False
        }


    def show_message(self, message, duration):
        # Показывает сообщение
        self.current_message = message
        self.message_timer = pg.time.get_ticks() + duration


    def draw_message(self):
        # Отрисовка текущее сообщение (если оно активно)
        if pg.time.get_ticks() < self.message_timer and self.current_message:

            text_surface = self.message_font.render(self.current_message, True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT - 600))

            bg_rect = pg.Rect(
                text_rect.x - 10,
                text_rect.y - 5,
                text_rect.width + 20,
                text_rect.height + 10
            )
            pg.draw.rect(self.screen, (0, 0, 0, 150), bg_rect, border_radius=5)

            self.screen.blit(text_surface, text_rect)


    def handle_attack(self):
        # Атака мечом
        if not self.has_sword:
            self.player.do_attack = False
            return

        if not self.player.do_attack:
            return

        self.attack_sound.play()

        attack_rect = pg.Rect(
            self.player.rect.right if self.player.facing_right else self.player.rect.left - 10,
            self.player.rect.y,
            10,
            self.player.rect.height
        )

        for enemy in [e for e in [self.enemy_slime_1, self.enemy_slime_2, self.enemy_slime_3] if e.alive()]:
            if attack_rect.colliderect(enemy.rect):
                enemy.health -= self.player.damage
                if enemy.health <= 0:
                    enemy.kill()
                    self.death_sound.play()


    def update_invincibility(self):
        # Обновление статуса неуязвимости
        current_time = pg.time.get_ticks()

        if self.player_invincible:
            if current_time > self.player_invincible_timer:
                self.player_invincible = False
                self.player_visible = True
        else:
            self.player_visible = True


    def check_enemy_collisions(self):
        # Проверка столкновений игрока с врагами
        for enemy in [self.enemy_slime_1, self.enemy_slime_2, self.enemy_slime_3]:
            if enemy.health > 0 and self.player.rect.colliderect(enemy.rect) and not self.player_invincible:
                # Наносим урон игроку
                self.player_damaged.play()
                self.player.health -= enemy.damage
                self.player_invincible = True
                self.player_invincible_timer = pg.time.get_ticks() + 1000

                # Отталкивание игрока при получении урона
                if self.player.rect.centerx < enemy.rect.centerx:
                    self.player.velocity_x = -5
                else:
                    self.player.velocity_x = 5
                self.player.velocity_y = -3

    def check_item_collisions(self):
        # Проверка столкновения с ромбом
        if not self.has_double_jump and self.player.rect.colliderect(self.diamond.rect):
            self.has_double_jump = True
            self.ability_notification = "Вы получили двойной прыжок!"
            self.notification_timer = pg.time.get_ticks() + 3000
            self.diamond.kill()  # Удаляем ромб
            self.item_sound.play()  # Проигрываем звук
            if not self.showed_messages["double_jump"]:
                self.show_message("Попробуйте прыгнуть дважды", 2000)
                self.showed_messages["double_jump"] = True

    def check_chest_collision(self):
        # Проверка столкновения с сундуком
        if (
                not self.chest_opened
                and self.player.rect.colliderect(self.chest.rect)
        ):
            self.chest_opened = True
            self.has_sword = True
            self.chest.image = pg.image.load('../img/sunduk/chest3.png').convert_alpha()
            self.ability_notification = "Вы получили меч!"
            self.chest.static_image = self.chest.image
            self.notification_timer = pg.time.get_ticks() + 3000
            self.chest_sound.play()
            if not self.showed_messages["sword"]:
                self.show_message("Нажмите 'E' для атаки", 2000)
                self.showed_messages["sword"] = True

    def check_danger_zones(self):
        """Проверяет попадание игрока на шипы"""
        if self.player_invincible:
            return

        player_rect = pg.Rect(
            self.player.rect.x + 4,
            self.player.rect.y + 4,
            self.player.rect.width - 8,
            self.player.rect.height - 8
        )

        for danger_rect in self.danger_rects:
            if player_rect.colliderect(danger_rect):
                self._take_damage_from_zone()
                break

    def _take_damage_from_zone(self):
        """Получение урона от опасной зоны"""
        self.player.health -= 100
        self.player_invincible = True
        self.player_invincible_timer = pg.time.get_ticks() + 1000
        self.player_damaged.play()

        self.player.velocity_y = -10
        self.player.velocity_x = 0


    def handle_game_over(self):
        """Анимация смерти и рестарт уровня"""
        self.fade_alpha += 5
        fade_surface = pg.Surface((WIDTH, HEIGHT))
        fade_surface.fill((0, 0, 0))
        fade_surface.set_alpha(min(self.fade_alpha, 255))
        self.screen.blit(fade_surface, (0, 0))

        if self.fade_alpha > 100:
            font = pg.font.Font(None, 72)
            death_text = font.render("ВЫ ПОГИБЛИ", True, (255, 255, 255))
            text_rect = death_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            self.screen.blit(death_text, text_rect)

        if self.fade_alpha >= 255:
            pg.time.delay(1000)
            self.restart_level()


    def restart_level(self):
        """Перезапускает текущий уровень"""
        self.game_over = False
        self.fade_alpha = 0

        self.has_sword = False
        self.has_double_jump = False
        self.chest_opened = False

        self.player.health = self.player_max_health
        self.player_invincible = False
        self.player_visible = True

        self.player.x = PLAYER_START_POS[0] * self.tmx_data.tilewidth
        self.player.y = PLAYER_START_POS[1] * self.tmx_data.tileheight
        self.player.rect.x = self.player.x
        self.player.rect.y = self.player.y

        self.player.velocity_x = 0
        self.player.velocity_y = 0
        self.player.jump_count = 0

        for enemy in [self.enemy_slime_1, self.enemy_slime_2, self.enemy_slime_3]:
            if not enemy.alive():
                enemy.health = SLIME_HEALTH
                enemy.kill()
                self.sprites.add(enemy)

        if not self.diamond.alive():
            self.diamond.health = 1
            self.sprites.add(self.diamond)

        if self.chest_opened:
            self.chest_opened = False
            self.chest.image = pg.image.load('../img/sunduk/chest1.png').convert_alpha()
            self.chest.static_image = self.chest.image


    def get_collision_tiles(self) -> list[pg.Rect]:
        """
        Вспомогательная функция. Возвращает все тайлы,
        с которыми спрайты должны сталкиваться
        """

        collision_tiles = []
        for layer in self.tmx_data.visible_layers:
            if hasattr(layer, 'data'):
                for x, y, gid in layer:
                    tile = self.tmx_data.get_tile_image(x, y, 0)
                    if tile and layer.properties.get('walls', True):
                        if gid != 2:
                            rect = pg.Rect(
                                x * self.tmx_data.tilewidth,
                                y * self.tmx_data.tileheight,
                                self.tmx_data.tilewidth,
                                self.tmx_data.tileheight,
                            )
                            collision_tiles.append(rect)

        return collision_tiles


    def render_start_screen(self) -> None:
        """
        Отрисовка стартового экрана
        """

        run_start_screen = True
        start_screen = pg.image.load(START_SCREEN_PATH).convert()
        start = False
        menu_music = pg.mixer.Sound(START_SCREEN_MUSIC_PATH)
        menu_music.set_volume(0.6)
        menu_music.play()
        while run_start_screen:
            self.screen.blit(pg.transform.scale(start_screen, (960, 640)), (0, 0))
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()

                if event.type == pg.KEYDOWN:
                    if pg.key.get_pressed()[pg.K_RETURN]:
                        menu_music.stop()
                        start = True

            if start:
                self.show_message("Чтобы двигаться и прыгать, используйте стрелочки", 2000)
                self.showed_messages["start"] = True
                break

            pg.display.flip()


    def render_victory_screen(self):
        # Показывает финальный экран
        self.screen.blit(pg.transform.scale(self.victory_image, (960, 640)), (0, 0))
        pg.display.flip()

        start_time = pg.time.get_ticks()
        show_next = False

        waiting = True
        while waiting:
            current_time = pg.time.get_ticks()

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    waiting = False
                    pg.quit()
                    sys.exit()
                if event.type == pg.KEYDOWN or event.type == pg.MOUSEBUTTONDOWN:
                    waiting = False
                    pg.quit()
                    sys.exit()

            # Пасхалка
            if not show_next and current_time - start_time > 5000:
                show_next = True
                self.screen.blit(pg.transform.scale(self.next_image, (960, 640)), (0, 0))
                pg.display.flip()

            pg.time.delay(30)


    def mainloop(self):
        """
        Основной цикл игры. Обрабатывает все события.
        :return:
        """
        collision_tiles: list[pg.Rect] = self.get_collision_tiles()
        running = True
        font = pg.font.Font(None, 36)

        # Для инициализации музыки
        pg.mixer.music.load(self.music_path)
        pg.mixer.music.play(-1)

        while running:
            # Если достигли конца уровня
            if self.victory:
                self.render_victory_screen()
                break
                # Обработка событий
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False

                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_UP:
                        if self.player.on_ground:
                            self.player.velocity_y = -PLAYER_JUMP_SPEED
                            self.player.on_ground = False
                            self.player.jump_count = 1  # Счетчик прыжков
                            self.jump_sound.play()
                        elif self.has_double_jump and self.player.jump_count < 2:
                            self.player.velocity_y = -PLAYER_JUMP_SPEED
                            self.player.jump_count += 1
                            self.jump_sound.play()

                    if event.key == pg.K_e:
                        self.player.do_attack = True

            # Проверка столкновений
            self.check_item_collisions()
            self.check_danger_zones()
            self.check_enemy_collisions()
            self.update_invincibility()
            self.check_chest_collision()
            self.handle_attack()

            # Обновление игрока
            if not self.game_over:
                keys = pg.key.get_pressed()
                if keys[pg.K_LEFT]:
                    self.player.velocity_x = -PLAYER_WALK_SPEED
                elif keys[pg.K_RIGHT]:
                    self.player.velocity_x = PLAYER_WALK_SPEED
                else:
                    self.player.velocity_x = 0

                self.player.x += self.player.velocity_x
                self.player.rect.x = self.player.x

            # Обновление врагов
            for enemy in [self.enemy_slime_1]:
                # Простое ИИ: прыгает случайным образом
                if enemy.on_ground and pg.time.get_ticks() % 50 == 0:
                    enemy.velocity_y = -SLIME_JUMP_FORCE
                    enemy.on_ground = False

            for sprite in self.sprites:
                sprite.update()
                if sprite == self.player:
                    if self.player_visible or not self.player_invincible:
                        sprite.render(self.screen)
                else:
                    sprite.render(self.screen)

            for enemy in [self.enemy_slime_2]:
                if enemy.on_ground and pg.time.get_ticks() % 60 == 0:
                    enemy.velocity_y = -SLIME_JUMP_FORCE
                    enemy.on_ground = False

            for enemy in [self.enemy_slime_3]:
                if enemy.on_ground and pg.time.get_ticks() % 40 == 0:
                    enemy.velocity_y = -SLIME_JUMP_FORCE
                    enemy.on_ground = False

            # Обработка столкновений всех сущностей
            for sprite in self.sprites:
                ground, top, right, left = sprite.check_collision(collision_tiles)

                # Гравитация
                sprite.rect.y += sprite.velocity_y
                sprite.y += sprite.velocity_y
                if not sprite.on_ground:
                    sprite.velocity_y += GRAVITY_ACCELERATION

                if abs(sprite.velocity_y) > MAX_FALL_SPEED:
                    sprite.velocity_y = MAX_FALL_SPEED if sprite.velocity_y > 0 else -MAX_FALL_SPEED

                # Обработка столкновений с тайлами
                for wall in collision_tiles:
                    if sprite.rect.colliderect(wall):
                        if sprite.velocity_y > 0 and ground:
                            sprite.rect.bottom = ground.top
                            sprite.y = ground.y - sprite.rect.height
                            sprite.velocity_y = 0
                            sprite.on_ground = True
                            sprite.jump_count = 0
                            if sprite.ent_type == 'player':
                                self.jump_sound.play()

                        elif sprite.velocity_y < 0 and top:
                            sprite.rect.top = wall.bottom
                            sprite.y = wall.y + wall.height
                            sprite.velocity_y = 0

                        if left:
                            sprite.x -= sprite.velocity_x
                            sprite.velocity_x = 0

                        if right:
                            sprite.x -= sprite.velocity_x
                            sprite.velocity_x = 0

            # Проверка на смерть
            if self.player.health <= 0 and not self.game_over:
                self.game_over = True
                self.fade_alpha = 0

            # Проверка на достижение конца уровня
            if (self.player.rect.x >= self.map_width - 930 and
                self.player.rect.y <= self.map_height - 640 and
                not self.victory):
                self.victory = True
                pg.mixer.music.stop()
                self.victory_music.play()

            if not self.showed_messages["start"] and pg.time.get_ticks() > 1000:
                self.show_message("Чтобы двигаться и прыгать, нажимайте стрелочки", 3000)
                self.showed_messages["start"] = True

            # Отрисовка
            self.screen.blit(pg.transform.scale(self.background_image_fd, (480, 320)), (480, 320))
            self.screen.blit(pg.transform.scale(self.background_image_fwd, (480, 320)), (480, 0))
            self.screen.blit(pg.transform.scale(self.background_image_fwd, (480, 320)), (0, 320))
            self.screen.blit(pg.transform.scale(self.background_image_fwd, (480, 320)), (0, 0))

            # Отрисовка тайлов карты
            for layer in self.tmx_data.visible_layers:
                if hasattr(layer, 'data'):
                    for x, y, gid in layer:
                        tile = self.tmx_data.get_tile_image_by_gid(gid)
                        if tile:
                            self.screen.blit(tile, (x * self.tmx_data.tilewidth, y * self.tmx_data.tileheight))

            # Отрисовка всех спрайтов
            for sprite in self.sprites:
                sprite.update()
                sprite.render(self.screen)

            # Обновляем камеру
            self.camera.update_quarter(self.player)

            # Отрисовываем через камеру
            self.camera.draw(self.sprites, self.tmx_data)

            # Обработка game over
            if self.game_over:
                self.handle_game_over()

            # Отрисовка HP
            health_text = font.render(f"HP: {self.player.health}", True, (255, 255, 255))
            self.screen.blit(health_text, (10, 10))

            self.draw_message()
            pg.display.flip()
            self.clock.tick(FPS)

        pg.quit()


class QuarterCamera:
    """
    Делит экран на четыре части
    """
    def __init__(self, game, level_width, level_height):
        self.game = game
        self.display_surf = pg.display.get_surface()

        self.quarters = [
            pg.Rect(0, 0, WIDTH // 2, HEIGHT // 2),
            pg.Rect(WIDTH // 2, 0, WIDTH // 2, HEIGHT // 2),
            pg.Rect(0, HEIGHT // 2, WIDTH // 2, HEIGHT // 2),
            pg.Rect(WIDTH // 2, HEIGHT // 2, WIDTH // 2, HEIGHT // 2)
        ]
        self.current_quarter = 0


    def update_quarter(self, player):
        player_center = player.rect.center
        if player_center[0] < WIDTH // 2:
            self.current_quarter = 0 if player_center[1] < HEIGHT // 2 else 2
        else:
            self.current_quarter = 1 if player_center[1] < HEIGHT // 2 else 3


    def draw(self, sprites, tmx_data):
        quarter = self.quarters[self.current_quarter]

        self.display_surf.blit(pg.transform.scale(self.game.background_image_fd, (480, 320)), (480, 320))
        self.display_surf.blit(pg.transform.scale(self.game.background_image_fwd, (480, 320)), (480, 0))
        self.display_surf.blit(pg.transform.scale(self.game.background_image_fwd, (480, 320)), (0, 320))
        self.display_surf.blit(pg.transform.scale(self.game.background_image_fwd, (480, 320)), (0, 0))

        self.display_surf.set_clip(quarter)

        for layer in tmx_data.visible_layers:
            if hasattr(layer, 'data'):
                for x, y, gid in layer:
                    tile_x = x * tmx_data.tilewidth
                    tile_y = y * tmx_data.tileheight
                    if quarter.collidepoint(tile_x, tile_y):
                        tile = tmx_data.get_tile_image_by_gid(gid)
                        if tile:
                            self.display_surf.blit(tile, (tile_x, tile_y))

        for sprite in sprites:
            if quarter.colliderect(sprite.rect):
                sprite.render(self.display_surf)

        self.display_surf.set_clip(None)

        pg.draw.line(self.display_surf, (50, 50, 50), (WIDTH // 2, 0), (WIDTH // 2, HEIGHT), 2)
        pg.draw.line(self.display_surf, (50, 50, 50), (0, HEIGHT // 2), (WIDTH, HEIGHT // 2), 2)

        if self.game.game_over:
            self.game.handle_game_over()