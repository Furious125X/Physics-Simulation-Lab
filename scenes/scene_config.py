import pygame

from scenes.spring_scene import SpringScene
from scenes.collision_scene import CollisionScene
from scenes.newton_cradle_scene import NewtonCradleScene
from scenes.rope_scene import RopeScene
from scenes.cloth_scene import ClothScene
from scenes.static_collision_scene import StaticCollisionScene


SCENE_CONFIG = [

    {
        "scene_id": "spring",
        "name": "Spring Demo",
        "description": (
            "Demonstrates spring forces, gravity, damping, "
            "and an anchored constraint."
        ),
        "shortcut": pygame.K_1,
        "scene_class": SpringScene
    },

    {
        "scene_id": "collision",
        "name": "Collision Demo",
        "description": (
            "Demonstrates circle-to-circle collisions, "
            "restitution, friction, and static bodies."
        ),
        "shortcut": pygame.K_2,
        "scene_class": CollisionScene
    },

    {
        "scene_id": "newton_cradle",
        "name": "Newton's Cradle",
        "description": (
            "Demonstrates constrained pendulum motion "
            "and collision-based momentum transfer."
        ),
        "shortcut": pygame.K_3,
        "scene_class": NewtonCradleScene
    },

    {
        "scene_id": "rope",
        "name": "Rope Scene",
        "description": (
            "Demonstrates a chain of bodies connected "
            "by distance constraints."
        ),
        "shortcut": pygame.K_4,
        "scene_class": RopeScene
    },

    {
        "scene_id": "cloth",
        "name": "Cloth Scene",
        "description": (
            "Demonstrates a grid of bodies connected "
            "by distance constraints."
        ),
        "shortcut": pygame.K_5,
        "scene_class": ClothScene
    },

    {
        "scene_id": "static_collision",
        "name": "Floor Test",
        "description": (
            "Demonstrates collisions between dynamic "
            "bodies and immovable static bodies."
        ),
        "shortcut": pygame.K_6,
        "scene_class": StaticCollisionScene
    }

]