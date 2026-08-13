from physics.vector import Vector2


class Camera:

    def __init__(self):
        self.position = Vector2()
        self.zoom = 1.0
        self.pan_speed = 10.0

    def world_to_screen(self, position):
        relative = position - self.position
        return relative * self.zoom

    def screen_to_world(self, position):
        return position / self.zoom + self.position

    def pan(self, screen_delta):
        self.position -= screen_delta / self.zoom

    def move(self, direction):
        self.pan(direction * self.pan_speed)