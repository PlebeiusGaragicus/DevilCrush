import sys
import platform
import time
import logging
import random
import math
logger = logging.getLogger()

import pygame

from src.config import *

SCREEN = None
SCREEN_WIDTH = 700
SCREEN_HEIGHT = 700
FRAME_RATE = 60

devil_x_pos = 40
devil_y_pos = SCREEN_HEIGHT - 40

# Enemy configuration
enemies = []
last_enemy_spawn = 0
ENEMY_SPAWN_COOLDOWN = 0.5  # seconds

# List to store active projectiles [(x, y, dx, dy), ...]  # Added dx, dy for diagonal movement
projectiles = []
last_shot_time = 0
last_scatter_time = 0
SHOT_COOLDOWN = 0.25  # seconds
SCATTER_COOLDOWN = 1.0  # seconds



def check_collision(x1, y1, x2, y2, radius1=5, radius2=10):
    # Calculate distance between two points
    distance = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
    return distance < (radius1 + radius2)

def update():
    global devil_x_pos, last_shot_time, last_scatter_time, projectiles, last_enemy_spawn
    
    current_time = time.time()
    keys = pygame.key.get_pressed()

    # Spawn new enemy
    if current_time - last_enemy_spawn >= ENEMY_SPAWN_COOLDOWN:
        y_pos = random.randint(50, SCREEN_HEIGHT - 200)  # Random height, keeping some space at bottom
        direction = random.choice([-1, 1])  # Random direction
        speed = random.uniform(2, 5)  # Random speed between 2 and 5
        new_enemy = {
            "x": SCREEN_WIDTH - 10 if direction < 0 else 10,
            "y": y_pos,
            "speed": speed,
            "direction": direction
        }
        enemies.append(new_enemy)
        last_enemy_spawn = current_time
    
    # Update player position based on mouse
    mouse_x, _ = pygame.mouse.get_pos()
    devil_x_pos = mouse_x
    
    # Shoot projectile with spacebar
    if keys[pygame.K_SPACE] and current_time - last_shot_time >= SHOT_COOLDOWN:
        projectiles.append([devil_x_pos, devil_y_pos, 0, -9])  # Straight up
        last_shot_time = current_time
    
    # Scatter shot with B key
    if keys[pygame.K_b] and current_time - last_scatter_time >= SCATTER_COOLDOWN:
        num_projectiles = random.randint(4, 7)  # Random number of projectiles
        speed = 9  # Uniform speed for all projectiles
        for _ in range(num_projectiles):
            angle = random.uniform(-45, 45)  # Random angle between -45 and 45 degrees
            rad = math.radians(angle)
            dx = math.sin(rad) * speed
            dy = -math.cos(rad) * speed  # Negative because y increases downward
            projectiles.append([devil_x_pos, devil_y_pos, dx, dy])
        last_scatter_time = current_time
    
    # Update projectiles and check collisions
    for projectile in projectiles[:]:
        projectile[0] += projectile[2]  # Update x with dx
        projectile[1] += projectile[3]  # Update y with dy
        
        # Check collision with each enemy
        for enemy in enemies[:]:
            if check_collision(projectile[0], projectile[1], enemy["x"], enemy["y"]):
                if projectile in projectiles:
                    projectiles.remove(projectile)
                enemies.remove(enemy)
                break
        
        if projectile[1] < 0 or projectile[0] < 0 or projectile[0] > SCREEN_WIDTH:  # Remove if off screen
            projectiles.remove(projectile)
    
    # Update enemy positions
    for enemy in enemies:
        enemy["x"] += enemy["speed"] * enemy["direction"]
        
        # Bounce off screen edges
        if enemy["x"] <= 10 or enemy["x"] >= SCREEN_WIDTH - 10:
            enemy["direction"] *= -1
    
    # Keep the devil within screen bounds
    devil_x_pos = max(10, min(devil_x_pos, SCREEN_WIDTH - 10))


def draw():
    # fill screen with green color
    # SCREEN.fill((150, 0, 150))
    SCREEN.fill((20, 10, 50))


    # draw projectiles
    for proj_x, proj_y, _, _ in projectiles:
        pygame.draw.circle(SCREEN, (255, 0, 0), (int(proj_x), int(proj_y)), 5, 0)

    # draw enemies
    for enemy in enemies:
        pygame.draw.circle(SCREEN, (0, 255, 255), (int(enemy["x"]), int(enemy["y"])), 10, 0)

    # draw a circle
    pygame.draw.circle(SCREEN, (255, 0, 0), (devil_x_pos, devil_y_pos), 10, 0)



def main():
    pygame.init()
    pygame.font.init()
    
    # Hide the cursor
    pygame.mouse.set_visible(False)

    # Create a clock to control frame rate
    clock = pygame.time.Clock()

    _info = pygame.display.Info()
    # width, height = _info.current_w, _info.current_h


    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), flags=pygame.NOFRAME | pygame.DOUBLEBUF | pygame.HWSURFACE | pygame.SRCALPHA)
    global SCREEN
    SCREEN = screen

    pygame.display.set_caption( "Devil Crush!" )


    running = True
    while running:
        try:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    continue
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    running = False
                    continue

            update()
            draw()

            pygame.display.flip()
            
            # Control the frame rate (30 FPS for slower movement)
            clock.tick( FRAME_RATE )

        except KeyboardInterrupt:
            logger.info("KeyboardInterrupt")
            running = False

        except NotImplementedError as e:
            logger.exception(e)
            running = False

        except Exception as e:
            logger.exception(e)
            running = False

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()