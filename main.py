import pygame

from render.renderer import Renderer
from scenes.scenes import SpringScene, CollisionScene, NewtonCradleScene, RopeScene, ClothScene, StaticCollisionScene

WIDTH = 800
HEIGHT = 600
FIXED_DT = 1 / 120

pygame.init()

font = pygame.font.SysFont(None, 24)

fps_timer = 0
fps_value = 0

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Physics Simulation Lab")

clock = pygame.time.Clock()

renderer = Renderer(screen)

current_scene = SpringScene()

debug_menu = font.render(
    "F2: Collision Grid  F3: Collison Normals F4: Velocity vectors F5: Force Vectors",
    True,
    (255, 255, 255)
)
debug = False

running = True
accumulator = 0

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
                
        current_scene.handle_event(event)

    while accumulator >= FIXED_DT:
        current_scene.update(FIXED_DT)
        accumulator -= FIXED_DT

    screen.fill((20, 20, 20))

    current_scene.draw(renderer)
    current_scene.world.draw_debug(renderer)

    menu = font.render(
        "1: Spring Demo   2: Collision Demo  3: Newton's Cradle 4: Rope Scene 5: Cloth Scene 6:Floor Test F1:Debug Menu",
        True,
        (255, 255, 255)
    )

    pygame.draw.rect(screen, (0, 0, 0), (6, 6, 120, 56))
    screen.blit(menu, (10, 10))
    

    fps_text = font.render(f"FPS: {fps_value:.1f}", True, (255, 255, 255))
    screen.blit(fps_text, (10, 35))

    if debug :
        screen.blit(debug_menu, (10, 60))

    pygame.display.flip()

pygame.quit()