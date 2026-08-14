import pygame
import os

from render.renderer import Renderer
from scenes.scenes import SpringScene, CollisionScene, NewtonCradleScene, RopeScene, ClothScene, StaticCollisionScene
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

fps_timer = 0
fps_value = 0

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Physics Simulation Lab")

clock = pygame.time.Clock()

renderer = Renderer(screen)

current_scene = SpringScene()

debug_menu = font.render(
    "F2: Collision Grid  F3: Collison Normals F4: Velocity vectors F5: Force Vectors F6: Bounding Boxes",
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

while running:

    frame_time = clock.tick(60) / 1000
    fps_timer += frame_time
    fps_value = clock.get_fps()
    accumulator += frame_time

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:

            if event.key == pygame.K_1:
                current_scene = SpringScene()

            elif event.key == pygame.K_2:
                current_scene = CollisionScene()

            elif event.key == pygame.K_3:
                current_scene = NewtonCradleScene()

            elif event.key == pygame.K_4:
                current_scene = RopeScene()
            
            elif event.key == pygame.K_5:
                current_scene = ClothScene()
            
            elif event.key == pygame.K_6:
                current_scene = StaticCollisionScene()

            elif event.key == pygame.K_F1:
                current_scene.world.debug_draw = not current_scene.world.debug_draw
                debug = not debug
            elif event.key == pygame.K_F2:
                current_scene.world.show_grid_debug = not current_scene.world.show_grid_debug

            elif event.key == pygame.K_F3:
                current_scene.world.show_collision_normals = not current_scene.world.show_collision_normals

            elif event.key == pygame.K_F4:
                current_scene.world.show_velocity_vectors = not current_scene.world.show_velocity_vectors

            elif event.key == pygame.K_F5:
                current_scene.world.show_force_vectors = not current_scene.world.show_force_vectors

            elif event.key == pygame.K_F6:
                current_scene.world.show_bounding_boxes = not current_scene.world.show_bounding_boxes

            elif event.key == pygame.K_F8:
                take_screenshot = True

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

            elif event.key == pygame.K_EQUALS:
                renderer.camera.zoom *= 1.1
                renderer.camera.zoom = min(renderer.camera.zoom, 5.0)

            elif event.key == pygame.K_MINUS:
                renderer.camera.zoom /= 1.1
                renderer.camera.zoom = max(renderer.camera.zoom, 0.1)
                
        current_scene.handle_event(event)

    while accumulator >= FIXED_DT:
        current_scene.update(FIXED_DT)
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

    current_scene.draw(renderer)
    current_scene.world.draw_debug(renderer)

    menu = font.render(
        "1: Spring Demo   2: Collision Demo  3: Newton's Cradle 4: Rope Scene 5: Cloth Scene 6:Floor Test F1:Debug Menu",
        True,
        (255, 255, 255)
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

    pygame.draw.rect(screen, (0, 0, 0), (6, 6, 120, 56))
    screen.blit(menu, (10, 10))
    

    fps_text = font.render(f"FPS: {fps_value:.1f}", True, (255, 255, 255))
    screen.blit(fps_text, (10, 35))

    if debug :
        screen.blit(debug_menu, (10, 60))

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