import pygame
import random
import math
from button import Button
import pygame_widgets
from pygame_widgets.slider import Slider
from pygame_widgets.textbox import TextBox


# Initialize Pygame and constants
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))

# Colors
WHITE = (255, 255, 255)
RED = (200, 0, 0)
GREEN = (0, 200, 0)
DARK_RED = (100, 0, 0)
PURPLE = (128, 0, 128)

# Game constants/settings
PLAYER_SPEED = 3
ENEMY_SPEED = 2
TANK_ENEMY_SPEED = 1  # Slower speed for tank enemy
BOSS_ENEMY_SPEED = 1.5  # Speed for boss enemy
PROJECTILE_SPEED = 7
PROJECTILE_SIZE = 10  # Base projectile size
enemy_dmg = 1
EXP = 0
LVL = 1
SPAWNRATE = 2000  # Initial enemy spawn rate in milliseconds
NEXT_WAVE_TIME = 30000  # Time until next wave in milliseconds

# Timed events
SPAWN_ENEMY = pygame.USEREVENT + 1
FIRE_PROJECTILE = pygame.USEREVENT + 2
SPAWN_TANK_ENEMY = pygame.USEREVENT + 3

# Set timers for spawning enemies and firing projectiles

pygame.time.set_timer(SPAWN_ENEMY, SPAWNRATE)
pygame.time.set_timer(FIRE_PROJECTILE, 1000)
pygame.time.set_timer(SPAWN_TANK_ENEMY, SPAWNRATE * 2)  # Spawn tank enemies less frequently


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

# --- Tank Enemy class ---
class TankEnemy(pygame.sprite.Sprite):
    def __init__(self, player):
        super().__init__()
        # Tank Enemy representation (a larger dark red square)
        self.image = pygame.Surface((30, 30))
        self.image.fill(DARK_RED)

        # Spawn enemy at random edge position
        x = random.choice([0, WIDTH])
        y = random.choice([0, HEIGHT])
        self.rect = self.image.get_rect(center=(x, y))
        self.player = player  # Reference to player for tracking
        self.health = 3  # Takes 3 hits to kill
    
    def update(self):
        # Enemy movement towards player (slower than regular enemy)
        dx = self.player.rect.centerx - self.rect.centerx
        dy = self.player.rect.centery - self.rect.centery
        dist = math.hypot(dx, dy)
        if dist == 0:
            dist = 1  # Prevent division by zero
        dx, dy, = dx / dist, dy / dist  # Normalize direction vector

        # Update enemy position with slower speed
        self.rect.x += dx * TANK_ENEMY_SPEED
        self.rect.y += dy * TANK_ENEMY_SPEED

# --- Boss Enemy class ---
class BossEnemy(pygame.sprite.Sprite):
    def __init__(self, player):
        super().__init__()
        # Boss Enemy representation (a large purple square)
        self.image = pygame.Surface((50, 50))
        self.image.fill(PURPLE)

        # Spawn boss at random edge position
        x = random.choice([0, WIDTH])
        y = random.choice([0, HEIGHT])
        self.rect = self.image.get_rect(center=(x, y))
        self.player = player  # Reference to player for tracking
        self.health = 20  # Takes 20 hits to kill
    
    def update(self):
        # Boss movement towards player
        dx = self.player.rect.centerx - self.rect.centerx
        dy = self.player.rect.centery - self.rect.centery
        dist = math.hypot(dx, dy)
        if dist == 0:
            dist = 1  # Prevent division by zero
        dx, dy, = dx / dist, dy / dist  # Normalize direction vector

        # Update boss position
        self.rect.x += dx * BOSS_ENEMY_SPEED
        self.rect.y += dy * BOSS_ENEMY_SPEED

# --- Projectile class ---
class Projectile(pygame.sprite.Sprite):
    def __init__(self, pos, direction, size=10):
        super().__init__()
        # Projectile representation (a white square)
        self.image = pygame.Surface((size, size))
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


# --- Main menu Functions ---

def main_menu():
    pygame.display.set_caption("Spellwalk - Main Menu")

    while True:
        # Fill the background
        screen.fill((0, 0, 0))
        mouse_pos = pygame.mouse.get_pos()

        menu_text = pygame.font.Font(None, 80).render("Spellwalk", True, WHITE)
        screen.blit(menu_text, (WIDTH // 2 - menu_text.get_width() // 2, 100))

        # Create buttons
        play_button = Button(None, (WIDTH // 2, HEIGHT // 2 - 50), "Play", pygame.font.Font(None, 40), WHITE, GREEN)
        options_button = Button(None, (WIDTH // 2, HEIGHT // 2 + 10), "Options", pygame.font.Font(None, 40), WHITE, GREEN)
        quit_button = Button(None, (WIDTH // 2, HEIGHT // 2 + 70), "Quit", pygame.font.Font(None, 40), WHITE, GREEN)

        #Update and draw buttons
        for button in [play_button, options_button, quit_button]:
            button.change_color(mouse_pos)
            button.update(screen)

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_button.check_for_input(mouse_pos):
                    play()
                if options_button.check_for_input(mouse_pos):
                    options()
                if quit_button.check_for_input(mouse_pos):
                    pygame.quit()
                    return
                
        # Update the display
        pygame.display.flip()
                

def options():
    
    global enemy_dmg
    slider = Slider(screen, 300, 300, 200, 20, min=1, max=10, step=1, initial=enemy_dmg)
    textbox = TextBox(screen, 300, 250, 200, 40,
                      fontSize=24, textColour=WHITE, colour=(40,40,40),
                      borderThickness=2, borderColour=WHITE)
    textbox.disable()
    textbox.setText(f"Enemy DMG: {int(enemy_dmg)}")

    while True:
        # Display options menu
        screen.fill((50, 50, 50))
        options_text = pygame.font.Font(None, 60).render("Options Menu - Press ESC to return", True, WHITE)
        screen.blit(options_text, (WIDTH // 2 - options_text.get_width() // 2, 100))



        # Event handling
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    enemy_dmg = int(slider.getValue())
                    return
                
        textbox.setText(f"Enemy DMG: {int(slider.getValue())}")
        enemy_dmg = int(slider.getValue())

        pygame_widgets.update(events)
        pygame.display.flip()

def play():
    global EXP, LVL
    running = True
    timer = pygame.time.get_ticks()
    clock = pygame.time.Clock()
    wave = 1
    while running:
        elapsed_time = pygame.time.get_ticks() - timer
        if elapsed_time > NEXT_WAVE_TIME + (wave - 1) * 10000:
            pygame.time.set_timer(SPAWN_ENEMY, SPAWNRATE // 2)
            wave += 1  # Increase spawn rate after 30 seconds
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

            # Spawn tank enemy event (only if player is level 5 or above)
            elif event.type == SPAWN_TANK_ENEMY:
                if LVL >= 5:
                    enemies.add(TankEnemy(player))

            # Fire projectile event
            elif event.type == FIRE_PROJECTILE:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                dx = mouse_x - player.rect.centerx
                dy = mouse_y - player.rect.centery
                dist = math.hypot(dx, dy)
                if dist == 0:
                    dist = 1
                direction = (dx / dist, dy / dist)
                # Projectile size increases with level
                proj_size = PROJECTILE_SIZE + (LVL - 1) * 2
                projectiles.add(Projectile(player.rect.center, direction, proj_size))

        # Update all sprite groups
        player_group.update(keys)
        enemies.update()
        projectiles.update()


        # Collision detection for projectiles hitting enemies
        for e in pygame.sprite.groupcollide(enemies, projectiles, False, True):
            # Check if enemy is a BossEnemy
            if isinstance(e, BossEnemy):
                e.health -= 1
                if e.health <= 0:
                    e.kill()
                    EXP += 10  # Give more XP for killing boss enemy
            # Check if enemy is a TankEnemy
            elif isinstance(e, TankEnemy):
                e.health -= 1
                if e.health <= 0:
                    e.kill()
                    EXP += 3  # Give more XP for killing tank enemy
            else:
                e.kill()
                EXP += 1
            
            # Check for level up
            old_lvl = LVL
            if EXP >= LVL * 5:
                LVL += 1
                EXP = 0
                player.health += 10  # Heal player on level up
                # Projectile size increases by 2 pixels per level (handled in projectile creation)
                
                # Spawn boss every 10 levels
                if LVL % 10 == 0:
                    enemies.add(BossEnemy(player))


        # Check for collisions between player and enemies
        if pygame.sprite.spritecollideany(player, enemies):
            player.health -= enemy_dmg
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
        
        # Draw EXP and LVL
        font = pygame.font.Font(None, 30)
        exp_text = font.render(f"EXP: {EXP}", True, WHITE)
        lvl_text = font.render(f"LVL: {LVL}", True, WHITE)
        screen.blit(exp_text, (10, 40))
        screen.blit(lvl_text, (10, 70))
    
        # Update the display
        pygame.display.flip()
    player.health = 100  # Reset player health for next game
    player.rect.center = (WIDTH // 2, HEIGHT // 2)  # Reset player position
    enemies.empty()  # Clear enemies
    projectiles.empty()  # Clear projectiles
    main_menu()
    # ...existing code...


# --- Main game loop ---
def main():
    main_menu()

if __name__ == "__main__":
    main()