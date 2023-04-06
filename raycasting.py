import pygame as pg
import math
from settings import *

class RayCasting:
    def __init__(self, game):
        self.game = game

    def ray_cast(self):
        ox, oy = self.game.player.pos
        x_map, y_map = self.game.player.map_pos

        ray_angle = self.game.player.angle - HALF_FOV + 0.0001
        for ray in range(NUM_RAYS):
            sin_a = math.sin(ray_angle)
            cos_a = math.cos(ray_angle)

            #horizontals
            y_horizontals, dy = (y_map + 1, 1) if sin_a > 0 else (y_map - 1e-6, -1)
            
            depth_horizontals = (y_horizontals - oy) / sin_a
            x_horizontals =  ox + depth_horizontals * cos_a

            delta_depth = dy / sin_a
            dx = delta_depth * cos_a

            for i in range(MAX_DEPTH):
                tile_horizontals = int(x_horizontals), int(y_horizontals)
                if tile_horizontals in self.game.map.world_map:
                    break

                y_horizontals += dx
                x_horizontals += dy
                depth_horizontals += delta_depth

            #verticals
            x_verticals, dx = (x_map + 1, 1) if cos_a > 0 else (x_map - 1e-6, -1)

            depth_verticals = (x_verticals - ox) / cos_a
            y_verticals = oy + depth_verticals * sin_a

            delta_depth = dx / cos_a
            dy = delta_depth * sin_a

            for i in range(MAX_DEPTH):
                tile_verticals = int(x_verticals), int(y_verticals)
                if tile_verticals in self.game.map.world_map:
                    break

                x_verticals += dx
                y_verticals += dy
                depth_verticals += delta_depth

            #depth
            if depth_verticals < depth_horizontals:
                depth = depth_verticals
            else:
                depth = depth_horizontals

            #draw for debug
            pg.draw.line(self.game.screen, 'yellow', (100 * ox, 100 * oy),
                        (100 * ox + 100 * depth * cos_a, 100 * oy + 100 * depth * sin_a), 2)

            ray_angle += DELTA_ANGLE

    def update(self):
        self.ray_cast()