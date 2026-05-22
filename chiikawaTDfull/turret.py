import pygame as pg
import constants as c
from turret_data import TURRET_DATA
import math

class Turret(pg.sprite.Sprite):
    def __init__(self, image, tile_x, tile_y):
        pg.sprite.Sprite.__init__(self)

        #other variables for turret
        self.upgrade_lvl = 1
        self.range = TURRET_DATA[self.upgrade_lvl - 1].get("range")
        self.cooldown = TURRET_DATA[self.upgrade_lvl - 1].get("cooldown")
        self.selected = False
        self.target = None

        #position variables
        self.tile_x = tile_x
        self.tile_y = tile_y

        #calculate center position of turret based on tile coordinates
        self.x = (self.tile_x + 0.5) * c.TILE_SIZE
        self.y = (self.tile_y + 0.5) * c.TILE_SIZE
        # store full list of turret images for different levels
        self.sprites = image      
        self.level = 0
        self.image = self.sprites[self.level]
        self.rect = self.image.get_rect()
        self.rect.center = (self.x, self.y)

        #create range visual
        self.range_image = pg.Surface((self.range * 2, self.range * 2))
        self.range_image.fill((0, 0, 0))
        self.range_image.set_colorkey((0, 0, 0))
        pg.draw.circle(self.range_image, "grey100", (self.range, self.range), self.range)
        self.range_image.set_alpha(100)
        self.range_rect = self.range_image.get_rect()
        self.range_rect.center = self.rect.center

    def update(self, enemy_group):
        self.pick_target(enemy_group)

    def pick_target(self, enemy_group):
        self.target = None
        closest_enemy = None
        closest_dist = float("inf")

        for enemy in enemy_group:
            x_dist = enemy.pos[0] - self.x
            y_dist = enemy.pos[1] - self.y
            dist = math.sqrt(x_dist ** 2 + y_dist ** 2)

            if dist < self.range and dist < closest_dist:
                closest_enemy = enemy
                closest_dist = dist
                self.target.health -= c.DAMAGE
                print("HIT!")
                break

        self.target = closest_enemy

    def upgrade_recruit(self):
        self.upgrade_lvl += 1
        self.range = TURRET_DATA[self.upgrade_lvl - 1].get("range")    
        self.cooldown = TURRET_DATA[self.upgrade_lvl - 1].get("cooldown")

        #create range visual again with new range
        self.range_image = pg.Surface((self.range * 2, self.range * 2))
        self.range_image.fill((0, 0, 0))
        self.range_image.set_colorkey((0, 0, 0))
        pg.draw.circle(self.range_image, "grey100", (self.range, self.range), self.range)
        self.range_image.set_alpha(100)
        self.range_rect = self.range_image.get_rect()
        self.range_rect.center = self.rect.center

        #upgrade turret image
        if self.level < len(self.sprites) - 1:
            self.level += 1
            self.image = self.sprites[self.level]

    def draw(self, surface):
        surface.blit(self.image, self.rect)
        if self.selected:
            surface.blit(self.range_image, self.range_rect)