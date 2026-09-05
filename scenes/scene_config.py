import pygame

from scenes.spring_scene import SpringScene
from scenes.collision_scene import CollisionScene
from scenes.newton_cradle_scene import NewtonCradleScene
from scenes.rope_scene import RopeScene
from scenes.cloth_scene import ClothScene
from scenes.static_collision_scene import StaticCollisionScene
from scenes.pendulum_scene import PendulumScene
from scenes.double_pendulum_scene import DoublePendulumScene
from scenes.projectile_scene import ProjectileScene
from scenes.inclined_plane_scene import InclinedPlaneScene
from scenes.atwood_machine_scene import AtwoodMachineScene
from scenes.orbital_mechanics_scene import OrbitalMechanicsScene
from scenes.elastic_collision_scene import ElasticCollisionScene
from scenes.bridge_scene import BridgeScene


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
        "shortcut": pygame.K_a,
        "scene_class": ClothScene
    },

    {
        "scene_id": "static_collision",
        "name": "Floor Test",
        "description": (
            "Demonstrates collisions between dynamic "
            "bodies and immovable static bodies."
        ),
        "shortcut": pygame.K_5,
        "scene_class": StaticCollisionScene
    },

    {
        "scene_id": "pendulum",
        "name": "Simple Pendulum",
        "description": (
            "Demonstrates gravitational pendulum motion "
            "using a fixed-length anchor constraint."
        ),
        "shortcut": pygame.K_6,
        "scene_class": PendulumScene
    },

    {
        "scene_id": "double_pendulum",
        "name": "Double Pendulum",
        "description": (
            "Demonstrates coupled pendulum motion "
            "using chained distance constraints."
        ),
        "shortcut": pygame.K_7,
        "scene_class": DoublePendulumScene
    },

    {
        "scene_id": "projectile",
        "name": "Projectile Motion",
        "description": (
            "Demonstrates projectile motion under gravity "
            "and floor collision."
        ),
        "shortcut": pygame.K_8,
        "scene_class": ProjectileScene
    },

    {
        "scene_id": "inclined_plane",
        "name": "Inclined Plane",
        "description": (
            "Demonstrates gravity, surface reaction, "
            "and friction on an inclined plane."
        ),
        "shortcut": pygame.K_9,
        "scene_class": InclinedPlaneScene
    },

    {
        "scene_id": "atwood_machine",
        "name": "Atwood Machine",
        "description": (
            "Demonstrates coupled motion of two unequal "
            "masses using a fixed-length rope."
        ),
        "shortcut": pygame.K_0,
        "scene_class": AtwoodMachineScene
    },

    {
        "scene_id": "orbital_mechanics",
        "name": "Orbital Mechanics",
        "description": (
            "Demonstrates gravitational attraction "
            "and orbital motion."
        ),
        "shortcut": pygame.K_b,
        "scene_class": OrbitalMechanicsScene
    },

    {
        "scene_id": "elastic_collision",
        "name": "Elastic vs Inelastic",
        "description": (
            "Demonstrates how restitution changes "
            "collision energy transfer."
        ),
        "shortcut": pygame.K_c,
        "scene_class": ElasticCollisionScene
    },

    {
        "scene_id": "bridge",
        "name": "Bridge Simulation",
        "description": (
            "Demonstrates structural deformation "
            "under gravitational loading."
        ),
        "shortcut": pygame.K_d,
        "scene_class": BridgeScene
    },

]