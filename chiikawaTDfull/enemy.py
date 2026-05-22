import pygame as pg
import constants as c
from pygame.math import Vector2
from enemy_data import MOMONGA_DATA

class Enemy(pg.sprite.Sprite):
    def __init__(self, enemy_type, waypoints, images):
        pg.sprite.Sprite.__init__(self)
        self.waypoints = waypoints
        self.pos = Vector2(self.waypoints[0])
        self.target_waypoint = 1

        #enemy stats
        self.health = MOMONGA_DATA[enemy_type]["health"]
        self.speed = MOMONGA_DATA[enemy_type]["speed"]

        self.image = images.get(enemy_type)
        self.rect = self.image.get_rect()
        self.rect.center = self.pos

    def check_health(self, world):
        if self.health <= 0:
            self.kill()
            world.money += c.REWARD

    def update(self, world):
        self.move(world)
        self.check_health(world)

    def move(self, world):

        #define taget waypoint
        if self.target_waypoint < len(self.waypoints):
            self.target = Vector2(self.waypoints[self.target_waypoint])
            self.movement = self.target - self.pos
        else:
            #enemy reached end of path
            self.kill()
            world.health -= 10

        #calculate distance to target!
        dist = self.movement.length()
        #check if remaining distance is greater than enemy speed
        if dist >= self.speed:
            self.pos += self.movement.normalize() * self.speed
        else:
            if dist != 0:
                self.pos += self.movement.normalize() * dist
            self.target_waypoint += 1

        self.rect.center = self.pos

