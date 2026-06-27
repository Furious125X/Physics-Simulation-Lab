import pygame


class Renderer:
    def __init__(self, screen):
        self.screen = screen

    def draw_ball(self, body):
        pygame.draw.circle(
            self.screen,
            (255, 255, 255),
            (int(body.x), int(body.y)),
            body.radius
        )