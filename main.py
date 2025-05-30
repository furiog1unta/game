import pygame
import random
import sys
import json
import os

pygame.init()


SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
HIGH_SCORE_FILE = "high_score.json"

GRAVITY = 0.5
JUMP_SPEED = -15
MOVE_SPEED = 5
FRICTION = 0.5

PLAYER_WIDTH = 40
PLAYER_HEIGHT = 40
PLATFORM_WIDTH = 100
PLATFORM_HEIGHT = 20


WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
ORANGE = (255, 165, 0)
RED = (255, 0, 0)
GRAY = (128, 128, 128)
GOLD = (255, 215, 0)

class Button:
    def __init__(self, x, y, width, height, text, color, hover_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False

    def draw(self, screen):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, BLACK, self.rect, 2)

        font = pygame.font.Font(None, 36)
        text_surface = font.render(self.text, True, BLACK)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.is_hovered:
                return True
        return False

class Menu:
    def __init__(self, screen):
        self.screen = screen
        self.title_font = pygame.font.Font(None, 74)
        self.buttons = [
            Button(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2, 200, 50, "Start Game", GREEN, (100, 255, 100)),
            Button(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 + 70, 200, 50, "Quit", RED, (255, 100, 100))
        ]

    def draw(self):
        self.screen.fill(WHITE)

        title = self.title_font.render("Doodle Jump", True, BLACK)
        title_rect = title.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//4))
        self.screen.blit(title, title_rect)

        
        for button in self.buttons:
            button.draw(self.screen)

        pygame.display.flip()

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            
            for i, button in enumerate(self.buttons):
                if button.handle_event(event):
                    if i == 0:
                        return "start"
                    elif i == 1:
                        return "quit"
        return None

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

    def move(self, platforms):
        self.vel_y += GRAVITY
        
        
        self.x += self.vel_x
        self.y += self.vel_y


        if self.vel_x > 0:
            self.vel_x = max(0, self.vel_x - FRICTION)
        elif self.vel_x < 0:
            self.vel_x = min(0, self.vel_x + FRICTION)

        
        for platform in platforms:
            if (self.vel_y > 0 and 
                self.y + self.height >= platform.y and
                self.y + self.height <= platform.y + platform.height and
                self.x + self.width > platform.x and
                self.x < platform.x + platform.width):
                self.vel_y = JUMP_SPEED
                self.jumping = True

        
        if self.x < 0:
            self.x = SCREEN_WIDTH
        elif self.x > SCREEN_WIDTH:
            self.x = 0

    def draw(self, screen, camera_y):
        pygame.draw.rect(screen, BLUE, (self.x, self.y - camera_y, self.width, self.height))

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

class HighScore:
    def __init__(self):
        self.high_score = self.load_high_score()

    def load_high_score(self):
        try:
            if os.path.exists(HIGH_SCORE_FILE):
                with open(HIGH_SCORE_FILE, 'r') as f:
                    return json.load(f)['high_score']
            return 0
        except:
            return 0

    def save_high_score(self):
        try:
            with open(HIGH_SCORE_FILE, 'w') as f:
                json.dump({'high_score': self.high_score}, f)
        except:
            pass

    def update(self, score):
        if score > self.high_score:
            self.high_score = score
            self.save_high_score()
            return True
        return False

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Doodle Jump")
        self.clock = pygame.time.Clock()
        self.menu = Menu(self.screen)
        self.game_state = "menu"  # "menu", "playing", "game_over"
        self.high_score = HighScore()
        self.new_high_score = False
        self.reset_game()

    def reset_game(self):
        self.player = Player(SCREEN_WIDTH // 2 - PLAYER_WIDTH // 2, SCREEN_HEIGHT - 140)
        self.platforms = []
        self.camera_y = 0
        self.game_over = False
        self.new_high_score = False
        self.generate_initial_platforms()

    def generate_initial_platforms(self):
        self.platforms.append(Platform(SCREEN_WIDTH // 2 - PLATFORM_WIDTH // 2, SCREEN_HEIGHT - 100))
        
        for i in range(1, 10):
            x = random.randint(0, SCREEN_WIDTH - PLATFORM_WIDTH)
            y = SCREEN_HEIGHT - 100 - i * 100
            self.platforms.append(Platform(x, y))

    def generate_new_platforms(self):
        while self.platforms[-1].y > self.player.y - SCREEN_HEIGHT:
            x = random.randint(0, SCREEN_WIDTH - PLATFORM_WIDTH)
            y = self.platforms[-1].y - random.randint(50, 150)
            self.platforms.append(Platform(x, y))

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

        return True

    def update(self):
        if self.game_state == "playing":
            self.player.move(self.platforms)
            for platform in self.platforms:
                platform.update()

            if self.player.y < self.camera_y + SCREEN_HEIGHT // 2:
                self.camera_y = self.player.y - SCREEN_HEIGHT // 2

            
            self.generate_new_platforms()

            
            self.platforms = [p for p in self.platforms if p.y < self.player.y + SCREEN_HEIGHT]

            
            if self.player.y > self.camera_y + SCREEN_HEIGHT:
                self.game_over = True
                self.game_state = "game_over"
                self.new_high_score = self.high_score.update(self.player.score)

            
            self.player.score = max(self.player.score, -int(self.player.y))

    def draw(self):
        if self.game_state == "menu":
            self.menu.draw()
        else:
            self.screen.fill(WHITE)

            if self.game_state == "playing":
                for platform in self.platforms:
                    platform.draw(self.screen, self.camera_y)
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