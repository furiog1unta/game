import pygame
from .config import SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, BLACK, GREEN, RED

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