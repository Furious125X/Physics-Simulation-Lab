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

    def __init__(
        self,
        scene_id,
        name,
        description,
        shortcut,
        scene_class
    ):
        self.scene_id = scene_id
        self.name = name
        self.description = description
        self.shortcut = shortcut
        self.scene_class = scene_class


class SceneManager:

    def __init__(self):

        self.scene_registry = [

            SceneDefinition(
                "spring",
                "Spring Demo",
                "Demonstrates spring forces, gravity, damping, and an anchored constraint.",
                pygame.K_1,
                SpringScene
            ),

            SceneDefinition(
                "collision",
                "Collision Demo",
                "Demonstrates circle-to-circle collisions, restitution, friction, and static bodies.",
                pygame.K_2,
                CollisionScene
            ),

            SceneDefinition(
                "newton_cradle",
                "Newton's Cradle",
                "Demonstrates constrained pendulum motion and collision-based momentum transfer.",
                pygame.K_3,
                NewtonCradleScene
            ),

            SceneDefinition(
                "rope",
                "Rope Scene",
                "Demonstrates a chain of bodies connected by distance constraints.",
                pygame.K_4,
                RopeScene
            ),

            SceneDefinition(
                "cloth",
                "Cloth Scene",
                "Demonstrates a grid of bodies connected by distance constraints.",
                pygame.K_5,
                ClothScene
            ),

            SceneDefinition(
                "static_collision",
                "Floor Test",
                "Demonstrates collisions between dynamic bodies and immovable static bodies.",
                pygame.K_6,
                StaticCollisionScene
            )
        ]

        self.current_scene_definition = self.scene_registry[0]
        self.current_scene = self.create_scene(
            self.current_scene_definition
        )

    @property
    def world(self):
        return self.current_scene.world

    @property
    def scene_metadata(self):
        return {
            "id": self.current_scene_definition.scene_id,
            "name": self.current_scene_definition.name,
            "description": self.current_scene_definition.description,
            "shortcut": self.current_scene_definition.shortcut
        }

    def switch_scene(self, shortcut):

        definition = self.get_scene_by_shortcut(shortcut)

        if definition is None:
            return False

        self.activate_scene(definition)

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

    def get_scene_by_id(self, scene_id):

        for definition in self.scene_registry:

            if definition.scene_id == scene_id:
                return definition

        return None

    def create_scene(self, definition):
        return definition.scene_class()

    def reset_scene(self):
        self.activate_scene(
            self.current_scene_definition
        )

    def activate_scene(self, definition):
        self.current_scene_definition = definition
        self.current_scene = self.create_scene(definition)

    def get_scene_help(self, definition):
        key_name = pygame.key.name(definition.shortcut)

        return (
            f"{key_name}: {definition.name} - "
            f"{definition.description}"
        )

    def get_current_scene_help(self):
        return self.get_scene_help(
            self.current_scene_definition
        )

    def get_all_scene_help(self):
        help_entries = []

        for definition in self.scene_registry:
            help_entries.append(
                self.get_scene_help(definition)
            )

        return help_entries