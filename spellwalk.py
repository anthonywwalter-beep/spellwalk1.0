import pygame
import random
import math

# Initialize Pygame and constants
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))

# Colors
WHITE = (255, 255, 255)
RED = (200, 0, 0)
GREEN = (0, 200, 0)

# Game constants/settings
PLAYER_SPEED = 5
ENEMY_SPEED = 2
PROJECTILE_SPEED = 7

# Timed events
SPAWN_ENEMY = pygame.USEREVENT + 1
FIRE_PROJECTILE = pygame.USEREVENT + 2

# Set timers for spawning enemies and firing projectiles
pygame.time.set_timer(SPAWN_ENEMY, 2000)
pygame.time.set_timer(FIRE_PROJECTILE, 1000)


# --- Player class ---
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # Player representation(a green square)
        self.image = pygame.Surface((30, 30))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        self.health = 100 # Player health

    def update(self, keys):
        # Player movement based on key presses
        dx = dy = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx = -PLAYER_SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx = PLAYER_SPEED
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy = -PLAYER_SPEED
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy = PLAYER_SPEED
        
        # Update player position
        self.rect.x += dx
        self.rect.y += dy
        # Keep player within screen bounds
        self.rect.clamp_ip(screen.get_rect())

# --- Enemy class ---
class Enemy(pygame.sprite.Sprite):
    def __init__(self, player):
        super().__init__()
        # Enemy representation (a red square)
        self.image = pygame.Surface((20, 20))
        self.image.fill(RED)

        # Spawn enemy at random edge position
        x = random.choice([0, WIDTH])
        y = random.choice([0, HEIGHT])
        self.rect = self.image.get_rect(center=(x, y))
        self.player = player # Reference to player for tracking
    
    def update(self):
        # Enemy movement towards player
        dx = self.player.rect.centerx - self.rect.centerx
        dy = self.player.rect.centery - self.rect.centery
        dist = math.hypot(dx, dy)
        if dist == 0:
            dist = 1 # Prevent division by zero
        dx, dy, = dx / dist, dy / dist # Normalize direction vector

        # Update enemy position
        self.rect.x += dx * ENEMY_SPEED
        self.rect.y += dy * ENEMY_SPEED

# --- Projectile class ---
class Projectile(pygame.sprite.Sprite):
    def __init__(self, pos, direction):
        super().__init__()
        # Projectile representation (a white square)
        self.image = pygame.Surface((10, 10))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect(center=pos)
        self.direction = direction # Direction vector

    def update(self):
        # Update projectile position
        self.rect.x += self.direction[0] * PROJECTILE_SPEED
        self.rect.y += self.direction[1] * PROJECTILE_SPEED

        # Remove projectile if it goes off-screen
        if not screen.get_rect().colliderect(self.rect):
            self.kill()

# --- Sprite groups ---
player = Player()
player_group = pygame.sprite.Group(player)
enemies = pygame.sprite.Group()
projectiles = pygame.sprite.Group()


# --- Main game loop ---
running = True
clock = pygame.time.Clock()
while running:
    clock.tick(60) # 60 FPS
    screen.fill((30, 30, 30)) # Clear screen with dark background
    # Get pressed keys
    keys = pygame.key.get_pressed()

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Spawn enemy event
        elif event.type == SPAWN_ENEMY:
            enemies.add(Enemy(player))

        # Fire projectile event
        elif event.type == FIRE_PROJECTILE:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            dx = mouse_x - player.rect.centerx
            dy = mouse_y - player.rect.centery
            dist = math.hypot(dx, dy)
            if dist == 0:
                dist = 1
            direction = (dx / dist, dy / dist)
            projectiles.add(Projectile(player.rect.center, direction))

    # Update all sprite groups
    player_group.update(keys)
    enemies.update()
    projectiles.update()


    # Collision detection for projectiles hitting enemies
    for e in pygame.sprite.groupcollide(enemies, projectiles, True, True):
        pass  # Enemy hit by projectile

    # Check for collisions between player and enemies
    if pygame.sprite.spritecollideany(player, enemies):
        player.health -= 0.1
        if player.health <= 0:
            print("Game Over")
            running = False

    # Draw all sprite groups
    player_group.draw(screen)
    enemies.draw(screen)
    projectiles.draw(screen)

    # Draw health bar
    pygame.draw.rect(screen, RED, (10, 10, 100, 20))
    pygame.draw.rect(screen, GREEN, (10, 10, player.health, 20))
    
    # Update the display
    pygame.display.flip()

pygame.quit()
# ...existing code...