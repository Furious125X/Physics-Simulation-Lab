import pygame


class Renderer:
    def __init__(self, screen):
        self.screen = screen

    def draw_body(self, body):
        pygame.draw.circle(
            self.screen,
            (255, 255, 255),
            (int(body.position.x), int(body.position.y)),
            body.radius
        )