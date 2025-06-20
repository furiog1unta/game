import pygame
import random
import sys

from .config import (SCREEN_WIDTH, SCREEN_HEIGHT, FPS, PLAYER_WIDTH, PLATFORM_WIDTH,
                     ENEMY_WIDTH, WHITE, BLACK, GOLD, BACKGROUND_IMAGE, MOVE_SPEED)
from .ui import Menu
from .entities import Player, Platform, Enemy
from .score import HighScore


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Doodle Jump")
        self.clock = pygame.time.Clock()
        self.menu = Menu(self.screen)
        self.game_state = "menu"
        self.high_score = HighScore()
        self.new_high_score = False
        self.reset_game()

    def reset_game(self):
        self.player = Player(SCREEN_WIDTH // 2 - PLAYER_WIDTH // 2, SCREEN_HEIGHT - 200)
        self.platforms = []
        self.enemies = []
        self.camera_y = 0
        self.game_over = False
        self.new_high_score = False
        self.enemy_score_threshold = 2000
        self.generate_initial_platforms()
        self.generate_initial_enemies()

    def generate_initial_platforms(self):
        self.platforms.append(Platform(SCREEN_WIDTH // 2 - PLATFORM_WIDTH // 2, SCREEN_HEIGHT - 120))
        
        for i in range(1, 10):
            x = random.randint(0, SCREEN_WIDTH - PLATFORM_WIDTH)
            y = SCREEN_HEIGHT - 120 - i * 100
            self.platforms.append(Platform(x, y))

    def generate_initial_enemies(self):
        self.enemies.clear()

    def generate_new_platforms(self):
        while self.platforms[-1].y > self.player.y - SCREEN_HEIGHT:
            x = random.randint(0, SCREEN_WIDTH - PLATFORM_WIDTH)
            y = self.platforms[-1].y - random.randint(50, 150)
            self.platforms.append(Platform(x, y))

    def spawn_enemy(self):
        x = random.randint(0, SCREEN_WIDTH - ENEMY_WIDTH)
        y = self.player.y - random.randint(100, 300)
        self.enemies.append(Enemy(x, y))

    def draw_game_over_screen(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))

        font_large = pygame.font.Font(None, 74)
        font_small = pygame.font.Font(None, 36)
        
        texts = {
            'game_over': font_large.render("Game Over!", True, WHITE),
            'score': font_small.render(f"Score: {self.player.score}", True, WHITE),
            'high_score': font_small.render(f"Best Score: {self.high_score.high_score}", True, GOLD),
            'restart': font_small.render("Press SPACE to play again", True, WHITE),
            'menu': font_small.render("Press M to return to menu", True, WHITE),
            'quit': font_small.render("Press ESC to quit", True, WHITE)
        }

        if self.new_high_score:
            texts['new_high_score'] = font_large.render("New High Score!", True, GOLD)

        y_offset = SCREEN_HEIGHT // 2 - 150
        for text in texts.values():
            self.screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, y_offset))
            y_offset += 50

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                elif event.key == pygame.K_SPACE and self.game_over:
                    self.reset_game()
                    self.game_state = "playing"
                elif event.key == pygame.K_m and self.game_over:
                    self.game_state = "menu"

        if self.game_state == "playing":
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.player.vel_x = -MOVE_SPEED
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.player.vel_x = MOVE_SPEED
            if keys[pygame.K_SPACE]:
                self.player.shoot()

        return True

    def check_collisions(self):
        for bullet in self.player.bullets[:]:
            for enemy in self.enemies[:]:
                if (bullet.active and enemy.alive and
                    bullet.x < enemy.x + enemy.width and
                    bullet.x + bullet.width > enemy.x and
                    bullet.y < enemy.y + enemy.height and
                    bullet.y + bullet.height > enemy.y):

                    bullet.active = False
                    enemy.alive = False
                    self.player.score += 100
                    break

        for enemy in self.enemies:
            if (enemy.alive and
                self.player.x < enemy.x + enemy.width and
                self.player.x + self.player.width > enemy.x and
                self.player.y < enemy.y + enemy.height and
                self.player.y + self.player.height > enemy.y):
                self.game_over = True
                self.game_state = "game_over"
                self.new_high_score = self.high_score.update(self.player.score)

    def update(self):
        if self.game_state == "playing":
            self.player.move(self.platforms)
            self.player.update_bullets()
            
            for platform in self.platforms:
                platform.update()
        
            for enemy in self.enemies:
                enemy.update()

            if self.player.y < self.camera_y + SCREEN_HEIGHT // 2:
                self.camera_y = self.player.y - SCREEN_HEIGHT // 2

            self.generate_new_platforms()

            self.platforms = [p for p in self.platforms if p.y < self.player.y + SCREEN_HEIGHT]
            self.enemies = [e for e in self.enemies if e.y < self.player.y + SCREEN_HEIGHT and e.alive]

            if self.player.y > self.camera_y + SCREEN_HEIGHT:
                self.game_over = True
                self.game_state = "game_over"
                self.new_high_score = self.high_score.update(self.player.score)

            self.player.score = max(self.player.score, -int(self.player.y))

            while self.player.score >= self.enemy_score_threshold:
                self.spawn_enemy()
                self.enemy_score_threshold += 2000

            self.check_collisions()

    def draw(self):
        if self.game_state == "menu":
            self.menu.draw()
        else:
            if BACKGROUND_IMAGE:
                self.screen.blit(BACKGROUND_IMAGE, (0, 0))
            else:
                self.screen.fill(WHITE)

            if self.game_state == "playing":
                for platform in self.platforms:
                    platform.draw(self.screen, self.camera_y)
                

                for enemy in self.enemies:
                    enemy.draw(self.screen, self.camera_y)
                
                self.player.draw(self.screen, self.camera_y)

                font = pygame.font.Font(None, 36)
                score_text = font.render(f'Score: {self.player.score}', True, BLACK)
                high_score_text = font.render(f'Best: {self.high_score.high_score}', True, GOLD)
                self.screen.blit(score_text, (10, 10))
                self.screen.blit(high_score_text, (10, 50))
            elif self.game_state == "game_over":
                self.draw_game_over_screen()

            pygame.display.flip()

    def run(self):
        running = True
        while running:
            if self.game_state == "menu":
                action = self.menu.handle_input()
                if action == "quit":
                    running = False
                elif action == "start":
                    self.reset_game()
                    self.game_state = "playing"
            else:
                running = self.handle_input()
                self.update()
            
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run() 