import pygame

from scenes.scenes import (
    SpringScene,
    CollisionScene,
    NewtonCradleScene,
    RopeScene,
    ClothScene,
    StaticCollisionScene
)


class SceneManager:

    def __init__(self):

        self.scene_registry = {
            pygame.K_1: SpringScene,
            pygame.K_2: CollisionScene,
            pygame.K_3: NewtonCradleScene,
            pygame.K_4: RopeScene,
            pygame.K_5: ClothScene,
            pygame.K_6: StaticCollisionScene
        }

        self.current_scene = SpringScene()

    @property
    def world(self):
        return self.current_scene.world

    def switch_scene(self, key):
        scene_class = self.scene_registry.get(key)

        if scene_class is None:
            return False

        self.current_scene = scene_class()
        return True

    def handle_event(self, event):

        if event.type == pygame.KEYDOWN:

            if self.switch_scene(event.key):
                return

            return

        self.current_scene.handle_event(event)

    def update(self, dt):
        self.current_scene.update(dt)

    def draw(self, renderer):
        self.current_scene.draw(renderer)
        self.current_scene.world.draw_debug(renderer)