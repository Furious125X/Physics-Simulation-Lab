import os
import pygame

from render.renderer import Renderer
from scenes.scene_manager import SceneManager
from physics.vector import Vector2


WIDTH = 800
HEIGHT = 600
FIXED_DT = 1 / 120


pygame.init()


screenshot_directory = "screenshots"
os.makedirs(
    screenshot_directory,
    exist_ok=True
)

recording_directory = "recordings"
os.makedirs(
    recording_directory,
    exist_ok=True
)


font = pygame.font.SysFont(None, 24)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Physics Simulation Lab")

clock = pygame.time.Clock()

renderer = Renderer(screen)
scene_manager = SceneManager()


debug_menu = font.render(
    "F2: Collision Grid  F3: Collision Normals  "
    "F4: Velocity Vectors  F5: Force Vectors  "
    "F6: Bounding Boxes  F7: Sleeping",
    True,
    (255, 255, 255)
)


debug = False

running = True
accumulator = 0

screenshot_count = 0
take_screenshot = False

recording_count = 0
recording = False


def build_scene_menu(scene_manager):
    entries = []

    for definition in scene_manager.scene_registry:
        key_name = pygame.key.name(definition.shortcut)

        entries.append(
            f"{key_name}: {definition.name}"
        )

    return "   ".join(entries)


while running:

    frame_time = clock.tick(60) / 1000
    accumulator += frame_time

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False
            continue

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_r:
                scene_manager.reset_scene()
                continue

            elif event.key == pygame.K_F1:
                scene_manager.world.debug_draw = (
                    not scene_manager.world.debug_draw
                )

                debug = not debug
                continue

            elif event.key == pygame.K_F2:
                scene_manager.world.show_grid_debug = (
                    not scene_manager.world.show_grid_debug
                )
                continue

            elif event.key == pygame.K_F3:
                scene_manager.world.show_collision_normals = (
                    not scene_manager.world.show_collision_normals
                )
                continue

            elif event.key == pygame.K_F4:
                scene_manager.world.show_velocity_vectors = (
                    not scene_manager.world.show_velocity_vectors
                )
                continue

            elif event.key == pygame.K_F5:
                scene_manager.world.show_force_vectors = (
                    not scene_manager.world.show_force_vectors
                )
                continue

            elif event.key == pygame.K_F6:
                scene_manager.world.show_bounding_boxes = (
                    not scene_manager.world.show_bounding_boxes
                )
                continue

            elif event.key == pygame.K_F7:
                scene_manager.world.show_sleeping = (
                    not scene_manager.world.show_sleeping
                )
                continue

            elif event.key == pygame.K_F8:
                take_screenshot = True
                continue

            elif event.key == pygame.K_F9:

                if not recording:
                    renderer.start_recording()
                    recording = True

                else:
                    filename = os.path.join(
                        recording_directory,
                        f"recording_{recording_count:04d}.mp4"
                    )

                    renderer.stop_recording(
                        filename,
                        fps=60
                    )

                    recording = False
                    recording_count += 1

                continue

            elif event.key == pygame.K_EQUALS:
                renderer.camera.zoom *= 1.1
                renderer.camera.zoom = min(
                    renderer.camera.zoom,
                    5.0
                )
                continue

            elif event.key == pygame.K_MINUS:
                renderer.camera.zoom /= 1.1
                renderer.camera.zoom = max(
                    renderer.camera.zoom,
                    0.1
                )
                continue

        scene_manager.handle_event(event)

    while accumulator >= FIXED_DT:
        scene_manager.update(FIXED_DT)
        accumulator -= FIXED_DT

    keys = pygame.key.get_pressed()

    if keys[pygame.K_LEFT]:
        renderer.camera.move(Vector2(1, 0))

    if keys[pygame.K_RIGHT]:
        renderer.camera.move(Vector2(-1, 0))

    if keys[pygame.K_UP]:
        renderer.camera.move(Vector2(0, 1))

    if keys[pygame.K_DOWN]:
        renderer.camera.move(Vector2(0, -1))

    screen.fill((20, 20, 20))

    scene_manager.draw(renderer)

    menu_text = (
        build_scene_menu(scene_manager)
        + "   R: Reset"
    )

    menu = font.render(
        menu_text,
        True,
        (255, 255, 255)
    )

    pygame.draw.rect(
        screen,
        (0, 0, 0),
        (6, 6, 780, 56)
    )

    screen.blit(
        menu,
        (10, 10)
    )

    fps_text = font.render(
        f"FPS: {clock.get_fps():.1f}",
        True,
        (255, 255, 255)
    )

    screen.blit(
        fps_text,
        (10, 35)
    )

    if debug:
        screen.blit(
            debug_menu,
            (10, 60)
        )

    if recording:
        recording_text = font.render(
            "REC",
            True,
            (255, 80, 80)
        )

        screen.blit(
            recording_text,
            (10, 58)
        )

    pygame.display.flip()

    if take_screenshot:
        filename = os.path.join(
            screenshot_directory,
            f"screenshot_{screenshot_count:04d}.png"
        )

        renderer.save_screenshot(filename)

        screenshot_count += 1
        take_screenshot = False

    if recording:
        renderer.capture_recording_frame()


pygame.quit()