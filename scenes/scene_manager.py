import pygame

from scenes.scenes import (
    SpringScene,
    CollisionScene,
    NewtonCradleScene,
    RopeScene,
    ClothScene,
    StaticCollisionScene
)

class SceneDefinition:

    def __init__(self, scene_id, name, shortcut, scene_class):
        self.scene_id = scene_id
        self.name = name
        self.shortcut = shortcut
        self.scene_class = scene_class

class SceneManager:

    def __init__(self):

        self.scene_registry = [
            SceneDefinition(
                "spring",
                "Spring Demo",
                pygame.K_1,
                SpringScene
            ),

            SceneDefinition(
                "collision",
                "Collision Demo",
                pygame.K_2,
                CollisionScene
            ),

            SceneDefinition(
                "newton_cradle",
                "Newton's Cradle",
                pygame.K_3,
                NewtonCradleScene
            ),

            SceneDefinition(
                "rope",
                "Rope Scene",
                pygame.K_4,
                RopeScene
            ),

            SceneDefinition(
                "cloth",
                "Cloth Scene",
                pygame.K_5,
                ClothScene
            ),

            SceneDefinition(
                "static_collision",
                "Floor Test",
                pygame.K_6,
                StaticCollisionScene
            )
        ]

        self.current_scene = SpringScene()

    @property
    def world(self):
        return self.current_scene.world

    def switch_scene(self, shortcut):

        definition = self.get_scene_by_shortcut(shortcut)

        if definition is None:
            return False

        self.current_scene = definition.scene_class()

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

    def get_scene_by_shortcut(self, shortcut):

        for definition in self.scene_registry:

            if definition.shortcut == shortcut:
                return definition

        return None