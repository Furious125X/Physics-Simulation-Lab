import pygame

from scenes.scene_config import SCENE_CONFIG


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

        self.scene_registry = []

        for config in SCENE_CONFIG:

            definition = SceneDefinition(
                config["scene_id"],
                config["name"],
                config["description"],
                config["shortcut"],
                config["scene_class"]
            )

            self.scene_registry.append(definition)

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