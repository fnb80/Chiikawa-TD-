import pygame as pg
import constants as c
from enemy_data import MOMONGA_WAVE_DATA

class World():
    def __init__(self, data, map_image):
        self.level = 1
        self.health = c.HEALTH
        self.money = c.MONEY
        self.tile_map = []
        self.waypoints = []
        self.level_data = data
        self.image = map_image
        self.momonga_list = []
        self.spawned_momonga = 0

        self.width = self.level_data["width"]
        self.height = self.level_data["height"]

    def process_data(self):
        #sort data to get waypoint info and tilemap info
        for layer in self.level_data["layers"]:
            # accept tile layers regardless of name (Tiled often names them "Tile Layer 1")
            if layer.get("type") == "tilelayer":
                self.tile_map = layer.get("data", [])
            elif layer["name"] == "waypoints":
                for obj in layer["objects"]:
                    waypoint_data = obj["polyline"]
                    self.process_waypoints(waypoint_data, obj)

    def process_waypoints(self, data, obj):
        #get waypoint data to get xy coordinates for enemy path
        for point in data:
            x = obj["x"] + point["x"]
            y = obj["y"] + point["y"]
            self.waypoints.append((x, y))

    def process_enemies(self):
        enemies = MOMONGA_WAVE_DATA[self.level - 1]
        for enemy_type, count in enemies.items():
            for _ in range(count):
                self.momonga_list.append(enemy_type)

    def draw(self, surface):
        surface.blit(self.image, (0, 0))