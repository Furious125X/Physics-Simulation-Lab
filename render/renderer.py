import pygame


class Renderer:
    def __init__(self, screen):
        self.screen = screen

    def draw_body(self, body):
        pygame.draw.circle(
            self.screen,
            body.color,
            (int(body.position.x), int(body.position.y)),
            body.radius
        )
    
    def draw_spring(self, spring) :
        pygame.draw.line(self.screen,(255,255,255), (int(spring.body1.position.x), int(spring.body1.position.y)), 
        (int(spring.body2.position.x), int(spring.body2.position.y)),spring.width)