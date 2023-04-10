import pygame as pg
import math
from settings import *

class RayCasting:
    def __init__(self, game):
        self.game = game
        self.ray_casting_result = []
        self.object_to_render = []
        self.textures = self.game.object_render.wall_textures

    def get_objects_to_render(self):
        self.objects_to_render = []
        for ray, values in enumerate(self.ray_casting_result):
            depth, proj_height, texture, offset = values

            if proj_height < HEIGHT:
                wall_column = self.textures[texture].subsurface(
                    offset * (TEXTURE_SIZE - SCALE), 0, SCALE, TEXTURE_SIZE
                )
                wall_column = pg.transform.scale(wall_column, (SCALE, proj_height))
                wall_pos = (ray * SCALE, HALF_HEIGHT - proj_height // 2)
            else:
                texture_height = TEXTURE_SIZE * HEIGHT / proj_height
                wall_column = self.textures[texture].subsurface(
                    offset * (TEXTURE_SIZE - SCALE), HALF_TEXTURE_SIZE - texture_height // 2,
                    SCALE, texture_height
                )
                wall_column = pg.transform.scale(wall_column, (SCALE, HEIGHT))
                wall_pos = (ray * SCALE , 0)

            self.objects_to_render.append((depth, wall_column, wall_pos))

    def ray_cast(self):
        self.ray_casting_result = []
        texture_verticals, texture_horizontals = 1, 1
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
                    texture_horizontals = self.game.map.world_map[tile_horizontals]
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
                    texture_verticals = self.game.map.world_map[tile_verticals]
                    break

                x_verticals += dx
                y_verticals += dy
                depth_verticals += delta_depth

            #depth, texture offset
            if depth_verticals < depth_horizontals:
                depth, texture = depth_verticals, texture_verticals
                y_verticals %= 1
                offset = y_verticals if cos_a > 0 else (1 - y_verticals)
            else:
                depth, texture = depth_horizontals, texture_horizontals
                x_horizontals %= 1
                offset = (1 - x_horizontals) if sin_a > 0 else x_horizontals

            #remove fishbowl effect
            depth *= math.cos(self.game.player.angle - ray_angle)

            #projection
            proj_height = SCREEN_DIST / (depth + 0.0001)

            #ray_casting result
            self.ray_casting_result.append((depth, proj_height, texture, offset))  

            ray_angle += DELTA_ANGLE

    def update(self):
        self.ray_cast()
        self.get_objects_to_render()