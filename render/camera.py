from physics.vector import Vector2


class Camera:

    def __init__(self):
        self.position = Vector2()

    def world_to_screen(self, position):
        return position - self.position

    def screen_to_world(self, position):
        return position + self.position