from sprite_object import *
from random import randint, random, choice

class NPC(AnimatedSprite):
    def __init__(self, game, path='resources/sprites/npc/soldier/0.png',
                 pos=(10.5,5.5), scale=0.6, shift=0.38, animation_time=180):
        super().__init__(game, path, pos, scale, shift, animation_time)
        self.attack_images = self.get_images(self.path + '/attack')
        self.death_images = self.get_images(self.path + '/death')
        self.idle_images = self.get_images(self.path + '/idle')
        self.pain_images = self.get_images(self.path + '/pain')
        self.walk_images = self.get_images(self.path + '/walk')

        self.attack_dist = randint(3, 6)
        self.speed = 0.03
        self.size = 10
        self.health = 100
        self.attack_damage = 10
        self.accuracy = 0.15
        self.alive = True
        self.pain = False
        self.ray_cast_value = False
        self.frame_counter = 0
    
    def update(self):
        self.check_animation_time()
        self.get_sprite()
        self.run_logic()
        # self.draw_ray_cast()

    def animate_death(self):
        if not self.alive:
            if self.game.global_trigger and self.frame_counter < len(self.death_images) - 1:
                self.death_images.rotate(-1)
                self.image = self.death_images[0]
                self.frame_counter += 1
    
    def animate_pain():
        self.animate(self.pain_images)
        if self.animation_trigger:
            self.pain = False

    def check_hit_in_npc(self):
        if self.ray_cast_value and self.game.player.shot:
            if HALF_WIDTH - self.sprite_half_width < self.screen_x < HALF_WIDTH + self.sprite_half_width:
                self.game.sound.npc_pain.play()
                self.game.player.shot = False
                self.pain = True
                self.health -= self.game.weapon.damage
                self.check_health()
    
    def check_health(self):
        if self.health < 1:
            self.alive = False
            self.game.sound.npc_death.play()

    def run_logic(self):
        if self.alive:
            self.ray_cast_value = self.ray_cast_player_npc()
            self.check_hit_in_npc()
            if self.pain():
                self.animate_pain()
            else:
                self.animate(self.idle_images)
        else:
            self.animate_death()

    @property
    def map_pos(self):
        return int(self.x), int(self.y)

    def ray_cast_player_npc(self):
        if self.game.player.map_pos == self.map_pos:
            return True

        wall_dist_vert, wall_dist_hor = 0, 0
        player_dist_vert, player_dist_hor = 0, 0 

        ox, oy = self.game.player.pos
        x_map, y_map = self.game.player.map_pos

        ray_angle = self.theta
        
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
            if tile_horizontals == self.map_pos:
                player_dist_hor = depth_horizontals
                break
            if tile_horizontals in self.game.map.world_map:
                wall_dist_hor = depth_horizontals
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
            if tile_verticals == self.map_pos:
                player_dist_vert = depth_verticals
                break
            if tile_verticals in self.game.map.world_map:
                wall_dist_vert = depth_verticals
                break

            x_verticals += dx
            y_verticals += dy
            depth_verticals += delta_depth
        
        player_dist = max(player_dist_vert, player_dist_hor)
        wall_dist = max(wall_dist_vert, wall_dist_hor)

        if 0 < player_dist < wall_dist or not wall_dist:
            return True
        return False
    
    def draw_ray_cast(self):
        pg.draw.circle(self.game.screen, 'red', (100 * self.x, 100 * self.y), 15)
        if self.ray_cast_player_npc():
            pg.draw.line(self.game.screen, 'orange', (100 * self.game.player.x, 100 * self.game.player.y),
            (100 * self.x, 100 * self.y), 2)
