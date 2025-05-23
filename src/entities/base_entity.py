import pygame as pg

from settings import *


class Entity(pg.sprite.Sprite):
    """
    Класс, при помощи которого на карте можно спавнить спрайты.
    """

    def __init__(
            self,
            ent_type: str,
            group: pg.sprite.Group,
            x: int,
            y: int,
            img: str,
            health: int,
            damage: int,
            walk_frames: list,
            attack_frames: list,
    ):
        """
        Инициализация всех вспомогательных переменных
        для корректной обработки действий спрайта.
        """

        super().__init__(group)
        self.group = group

        self.x = x
        self.y = y

        self.health = health
        self.damage = damage
        self.walk_frames = [pg.image.load(f) for f in walk_frames]
        self.attack_frames = [pg.image.load(f) for f in attack_frames]
        self.current_frames_list = self.walk_frames

        self.ent_type = ent_type

        self.current_frame = 0
        self.image = self.walk_frames[self.current_frame]
        self.static_image = pg.image.load(img)
        self.frame_delay = 10
        self.frame_timer = 0
        self.facing_right = True

        self.rect = self.image.get_rect()
        self.rect.x = x + 5
        self.rect.y = y

        self.velocity_y = 0
        self.velocity_x = 0

        self.collision_right = False
        self.collision_left = False
        self.collision_top = False
        self.on_ground = False
        self.do_attack = False
        self.jump = False
        self.prev_attack = False
        self.jump_count = 0

    def check_collision(self, collision_tiles: list[pg.Rect]) -> tuple:
        """
        Реализация "сенсора". Позволяет определить,
        какой стены спрайт касается снизу, слева, сверху, справа.
        """

        ground_sensor = pg.Rect(
            self.rect.left + 2,
            self.rect.bottom,
            self.rect.width - 4,
            5,
        )

        right_sensor = pg.Rect(
            self.rect.right,
            self.rect.top + 5,
            3,
            self.rect.height - 10,
        )

        left_sensor = pg.Rect(
            self.rect.left - 3,
            self.rect.top + 5,
            3,
            self.rect.height - 10,
        )

        ceiling_sensor = pg.Rect(
            self.rect.left + 2,
            self.rect.top - 5,
            self.rect.width - 4,
            5,
        )

        self.on_ground = False
        self.collision_right = False
        self.collision_left = False

        ground, top, left, right = None, None, None, None
        for tile in collision_tiles:
            if ground_sensor.colliderect(tile):
                self.on_ground = True
                ground = tile

            if right_sensor.colliderect(tile):
                self.collision_right = True
                right = tile

            if left_sensor.colliderect(tile):
                self.collision_left = True
                left = tile

            if ceiling_sensor.colliderect(tile):
                self.collision_top = True
                top = tile

        return ground, top, right, left

    def update(self):
        """
        Функция обновления значений переменных
        """

        self.rect.x = self.x
        self.rect.y = self.y

        self.frame_timer += 1

        if self.do_attack and self.current_frame == len(self.attack_frames) - 1:
            self.current_frame = 0
            self.do_attack = False

        if self.frame_timer >= self.frame_delay:
            self.frame_timer = 0
            if not self.do_attack:
                self.current_frame = (self.current_frame + 1) % len(self.walk_frames)
                self.image = self.walk_frames[self.current_frame]

            else:
                self.current_frame = (self.current_frame + 1) % len(self.attack_frames)
                if self.facing_right:
                    self.image = self.attack_frames[self.current_frame]

                else:
                    self.image = pg.transform.flip(self.attack_frames[self.current_frame], True, False)

    def render(self, screen: pg.Surface):
        """
        Функция отрисовки спрайта на экране и обработки его движения.
        """

        pressed = pg.key.get_pressed()

        moving_left = pressed[pg.K_LEFT] and self.velocity_x < 0
        moving_right = pressed[pg.K_RIGHT] and self.velocity_x > 0

        if moving_left and self.facing_right and not self.do_attack:
            self.facing_right = False
            self.walk_frames = [pg.transform.flip(frame, True, False) for frame in self.walk_frames]
            self.image = self.walk_frames[self.current_frame]

        if moving_right and not self.facing_right and not self.do_attack:
            self.facing_right = True
            self.walk_frames = [pg.transform.flip(frame, True, False) for frame in self.walk_frames]
            self.image = self.walk_frames[self.current_frame]

        if self.do_attack and not self.prev_attack:
            self.current_frame = 0
            if self.facing_right:
                self.image = self.attack_frames[0]

            else:
                self.image = pg.transform.flip(self.attack_frames[0], True, False)

        if self.velocity_x != 0 or self.do_attack:
            screen.blit(self.image, (self.x, self.y))

        elif self.velocity_x == 0 and self.facing_right and not self.do_attack:
            screen.blit(self.static_image, (self.x, self.y))

        elif self.velocity_x == 0 and not self.do_attack:
            screen.blit(pg.transform.flip(self.static_image, True, False), (self.x, self.y))

        self.prev_attack = self.do_attack

    def get_distance_to_another_entity(self, entity):
        return ((self.x - entity.x) ** 2 + (self.y - entity.y) ** 2) ** 0.5
