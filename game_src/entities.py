import pygame
import random
from .config import (PLAYER_WIDTH, PLAYER_HEIGHT, PLAYER_IMAGE, GRAVITY, JUMP_SPEED, 
                     FRICTION, SCREEN_WIDTH, SCREEN_HEIGHT, BLUE, PLATFORM_WIDTH, 
                     PLATFORM_HEIGHT, GREEN, ORANGE, RED, ENEMY_WIDTH, ENEMY_HEIGHT, 
                     ENEMY_IMAGE, BLACK)

class Bullet:
    def __init__(self, x, y, direction):
        self.x = x
        self.y = y
        self.width = 8
        self.height = 8
        self.vel_x = 10 * direction
        self.vel_y = 0
        self.active = True

    def update(self):
        if not self.active:
            return
        self.x += self.vel_x
        self.y += self.vel_y
        if self.x < 0 or self.x > SCREEN_WIDTH:
            self.active = False

    def draw(self, screen, camera_y):
        if self.active:
            pygame.draw.circle(screen, BLACK, (int(self.x + self.width//2), int(self.y - camera_y + self.height//2)), 4)

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = PLAYER_WIDTH
        self.height = PLAYER_HEIGHT
        self.vel_x = 0
        self.vel_y = 0
        self.score = 0
        self.jumping = False
        self.facing_right = True
        self.bullets = []
        self.shoot_cooldown = 0

    def shoot(self):
        if self.shoot_cooldown == 0:
            direction = 1 if self.facing_right else -1
            bullet_x = self.x + (self.width if self.facing_right else 0)
            bullet_y = self.y + self.height // 2
            self.bullets.append(Bullet(bullet_x, bullet_y, direction))
            self.shoot_cooldown = 30

    def update_bullets(self):
        for bullet in self.bullets[:]:
            bullet.update()
            if not bullet.active:
                self.bullets.remove(bullet)
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

    def move(self, platforms):
        self.vel_y += GRAVITY
        
        if self.vel_x > 0:
            self.facing_right = True
        elif self.vel_x < 0:
            self.facing_right = False
        
        self.x += self.vel_x
        self.y += self.vel_y

        if self.vel_x > 0:
            self.vel_x = max(0, self.vel_x - FRICTION)
        elif self.vel_x < 0:
            self.vel_x = min(0, self.vel_x + FRICTION)

        for platform in platforms:
            if (self.vel_y > 0 and 
                self.y + self.height >= platform.y and
                self.y + self.height <= platform.y + platform.height + 10 and
                self.x + self.width > platform.x and
                self.x < platform.x + platform.width):
                self.vel_y = JUMP_SPEED
                self.jumping = True

        if self.x < 0:
            self.x = SCREEN_WIDTH
        elif self.x > SCREEN_WIDTH:
            self.x = 0

    def draw(self, screen, camera_y):
        if PLAYER_IMAGE:
            if self.facing_right:
                screen.blit(PLAYER_IMAGE, (self.x, self.y - camera_y))
            else:
                flipped_image = pygame.transform.flip(PLAYER_IMAGE, True, False)
                screen.blit(flipped_image, (self.x, self.y - camera_y))
        else:
            pygame.draw.rect(screen, BLUE, (self.x, self.y - camera_y, self.width, self.height))
        
        for bullet in self.bullets:
            bullet.draw(screen, camera_y)

class Platform:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = PLATFORM_WIDTH
        self.height = PLATFORM_HEIGHT
        self.type = random.choice(['normal', 'disappearing', 'moving'])
        self.visible = True
        self.move_direction = 1
        self.move_speed = 2

    def update(self):
        if self.type == 'moving':
            self.x += self.move_speed * self.move_direction
            if self.x <= 0 or self.x + self.width >= SCREEN_WIDTH:
                self.move_direction *= -1

    def draw(self, screen, camera_y):
        if self.visible:
            color = GREEN if self.type == 'normal' else ORANGE if self.type == 'disappearing' else RED
            pygame.draw.rect(screen, color, (self.x, self.y - camera_y, self.width, self.height))

class Enemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = ENEMY_WIDTH
        self.height = ENEMY_HEIGHT
        self.vel_x = random.choice([-2, 2])
        self.vel_y = 0
        self.alive = True

    def update(self):
        if not self.alive:
            return
        
        self.x += self.vel_x
        self.y += self.vel_y
        
        if self.x <= 0 or self.x + self.width >= SCREEN_WIDTH:
            self.vel_x *= -1

    def draw(self, screen, camera_y):
        if self.alive:
            if ENEMY_IMAGE:
                image_to_draw = ENEMY_IMAGE
                if self.vel_x < 0:
                    image_to_draw = pygame.transform.flip(ENEMY_IMAGE, True, False)
                screen.blit(image_to_draw, (self.x, self.y - camera_y))
            else:
                pygame.draw.rect(screen, RED, (self.x, self.y - camera_y, self.width, self.height)) 