import pygame
import random
import math
from button import Button
import pygame_widgets
from pygame_widgets.slider import Slider
from pygame_widgets.textbox import TextBox
from spells import SpellManager, LightningSpell, FireballSpell, FreezeSpell, SPELL_INFO


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
        self.speed_multiplier = 1.0  # For spell effects
    
    def update(self):
        # Enemy movement towards player
        dx = self.player.rect.centerx - self.rect.centerx
        dy = self.player.rect.centery - self.rect.centery
        dist = math.hypot(dx, dy)
        if dist == 0:
            dist = 1 # Prevent division by zero
        dx, dy, = dx / dist, dy / dist # Normalize direction vector

        # Update enemy position with speed multiplier
        self.rect.x += dx * ENEMY_SPEED * self.speed_multiplier
        self.rect.y += dy * ENEMY_SPEED * self.speed_multiplier

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
        self.speed_multiplier = 1.0  # For spell effects
    
    def update(self):
        # Enemy movement towards player (slower than regular enemy)
        dx = self.player.rect.centerx - self.rect.centerx
        dy = self.player.rect.centery - self.rect.centery
        dist = math.hypot(dx, dy)
        if dist == 0:
            dist = 1  # Prevent division by zero
        dx, dy, = dx / dist, dy / dist  # Normalize direction vector

        # Update enemy position with slower speed
        self.rect.x += dx * TANK_ENEMY_SPEED * self.speed_multiplier
        self.rect.y += dy * TANK_ENEMY_SPEED * self.speed_multiplier

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
        self.speed_multiplier = 1.0  # For spell effects
    
    def update(self):
        # Boss movement towards player
        dx = self.player.rect.centerx - self.rect.centerx
        dy = self.player.rect.centery - self.rect.centery
        dist = math.hypot(dx, dy)
        if dist == 0:
            dist = 1  # Prevent division by zero
        dx, dy, = dx / dist, dy / dist  # Normalize direction vector

        # Update boss position
        self.rect.x += dx * BOSS_ENEMY_SPEED * self.speed_multiplier
        self.rect.y += dy * BOSS_ENEMY_SPEED * self.speed_multiplier

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

def spell_selection_menu(spell_manager):
    """Display spell selection menu when player reaches level 3"""
    available_spells = ['lightning', 'fireball', 'freeze']
    selected_spell = None
    
    # Create spell option boxes
    spell_rects = []
    for i, spell_key in enumerate(available_spells):
        x = WIDTH // 4 + i * (WIDTH // 4)
        y = HEIGHT // 2
        rect = pygame.Rect(x - 100, y - 80, 200, 160)
        spell_rects.append((rect, spell_key))
    
    while selected_spell is None:
        screen.fill((20, 20, 40))
        
        # Title
        title_font = pygame.font.Font(None, 60)
        title_text = title_font.render("Choose Your Spell!", True, WHITE)
        screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 50))
        
        subtitle_font = pygame.font.Font(None, 30)
        subtitle_text = subtitle_font.render("Click to select", True, WHITE)
        screen.blit(subtitle_text, (WIDTH // 2 - subtitle_text.get_width() // 2, 110))
        
        mouse_pos = pygame.mouse.get_pos()
        
        # Draw spell options
        for rect, spell_key in spell_rects:
            spell_info = SPELL_INFO[spell_key]
            
            # Check if mouse is hovering
            is_hovering = rect.collidepoint(mouse_pos)
            border_color = (255, 215, 0) if is_hovering else WHITE
            bg_color = (60, 60, 80) if is_hovering else (40, 40, 60)
            
            # Draw box
            pygame.draw.rect(screen, bg_color, rect)
            pygame.draw.rect(screen, border_color, rect, 3)
            
            # Draw spell name
            name_font = pygame.font.Font(None, 32)
            name_text = name_font.render(spell_info['name'], True, WHITE)
            screen.blit(name_text, (rect.centerx - name_text.get_width() // 2, rect.top + 15))
            
            # Draw combo
            combo_font = pygame.font.Font(None, 24)
            combo_text = combo_font.render(f"Combo: {spell_info['combo']}", True, (200, 200, 255))
            screen.blit(combo_text, (rect.centerx - combo_text.get_width() // 2, rect.top + 50))
            
            # Draw description
            desc_font = pygame.font.Font(None, 18)
            desc_text = desc_font.render(spell_info['description'], True, (180, 180, 180))
            screen.blit(desc_text, (rect.centerx - desc_text.get_width() // 2, rect.top + 80))
            
            # Draw stats
            stat_font = pygame.font.Font(None, 18)
            y_offset = 105
            if 'damage' in spell_info:
                stat_text = stat_font.render(f"DMG: {spell_info['damage']}", True, (255, 100, 100))
                screen.blit(stat_text, (rect.centerx - stat_text.get_width() // 2, rect.top + y_offset))
                y_offset += 20
            if 'duration' in spell_info:
                stat_text = stat_font.render(f"Duration: {spell_info['duration']}s", True, (100, 200, 255))
                screen.blit(stat_text, (rect.centerx - stat_text.get_width() // 2, rect.top + y_offset))
                y_offset += 20
            if 'cooldown' in spell_info:
                stat_text = stat_font.render(f"CD: {spell_info['cooldown']}s", True, (200, 200, 100))
                screen.blit(stat_text, (rect.centerx - stat_text.get_width() // 2, rect.top + y_offset))
        
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return None
            if event.type == pygame.MOUSEBUTTONDOWN:
                for rect, spell_key in spell_rects:
                    if rect.collidepoint(mouse_pos):
                        selected_spell = spell_key
                        break
        
        pygame.display.flip()
    
    # Unlock the selected spell
    spell_manager.unlock_spell(selected_spell)
    return selected_spell

def play():
    global EXP, LVL
    running = True
    timer = pygame.time.get_ticks()
    clock = pygame.time.Clock()
    wave = 1
    spell_manager = SpellManager()
    spell_effects = pygame.sprite.Group()  # For lightning, fireballs, freeze effects
    has_shown_spell_menu = False
    
    while running:
        current_time = pygame.time.get_ticks()
        elapsed_time = current_time - timer
        
        # Show spell selection menu at level 3
        if LVL >= 3 and not has_shown_spell_menu:
            spell_selection_menu(spell_manager)
            has_shown_spell_menu = True
        
        if elapsed_time > NEXT_WAVE_TIME + (wave - 1) * 10000:
            pygame.time.set_timer(SPAWN_ENEMY, SPAWNRATE // 2)
            wave += 1  # Increase spawn rate after 30 seconds
        clock.tick(60) # 60 FPS
        
        # Update spell manager
        spell_manager.update(current_time)
        
        screen.fill((30, 30, 30)) # Clear screen with dark background
        # Get pressed keys
        keys = pygame.key.get_pressed()

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # Track key presses for spell combos
            elif event.type == pygame.KEYDOWN:
                spell_manager.add_key_to_combo(event.key, current_time)

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
        
        # Check for spell combos
        if spell_manager.check_lightning_combo(current_time):
            mouse_pos = pygame.mouse.get_pos()
            lightning = LightningSpell(player.rect.center, mouse_pos)
            spell_effects.add(lightning)
        
        if spell_manager.check_fireball_combo(current_time):
            mouse_pos = pygame.mouse.get_pos()
            dx = mouse_pos[0] - player.rect.centerx
            dy = mouse_pos[1] - player.rect.centery
            dist = math.hypot(dx, dy)
            if dist == 0:
                dist = 1
            direction = (dx / dist, dy / dist)
            fireball = FireballSpell(player.rect.center, direction)
            spell_effects.add(fireball)
        
        if spell_manager.check_freeze_combo(current_time):
            freeze = FreezeSpell(player.rect.center)
            spell_effects.add(freeze)

        # Update all sprite groups
        player_group.update(keys)
        enemies.update()
        projectiles.update()
        
        # Update spell effects
        for effect in spell_effects:
            if isinstance(effect, LightningSpell):
                effect.update(current_time)
            elif isinstance(effect, FireballSpell):
                effect.update(current_time, screen.get_rect())
            elif isinstance(effect, FreezeSpell):
                effect.update(current_time)


        # Spell effects on enemies
        for effect in spell_effects:
            if isinstance(effect, LightningSpell):
                for enemy in enemies:
                    if effect.check_hit(enemy):
                        if isinstance(enemy, BossEnemy):
                            enemy.health -= effect.damage
                            if enemy.health <= 0:
                                enemy.kill()
                                EXP += 10
                        elif isinstance(enemy, TankEnemy):
                            enemy.health -= effect.damage
                            if enemy.health <= 0:
                                enemy.kill()
                                EXP += 3
                        else:
                            enemy.kill()
                            EXP += 1
            
            elif isinstance(effect, FireballSpell):
                hit_enemies = pygame.sprite.spritecollide(effect, enemies, False)
                for enemy in hit_enemies:
                    effect.kill()  # Fireball disappears on hit
                    if isinstance(enemy, BossEnemy):
                        enemy.health -= effect.damage
                        if enemy.health <= 0:
                            enemy.kill()
                            EXP += 10
                    elif isinstance(enemy, TankEnemy):
                        enemy.health -= effect.damage
                        if enemy.health <= 0:
                            enemy.kill()
                            EXP += 3
                    else:
                        enemy.kill()
                        EXP += 1
                    break  # Fireball only hits one enemy
            
            elif isinstance(effect, FreezeSpell):
                for enemy in enemies:
                    if effect.is_in_range((enemy.rect.centerx, enemy.rect.centery)):
                        effect.freeze_enemy(enemy)
        
        # Reset enemy speeds if freeze effect expires
        for enemy in enemies:
            if hasattr(enemy, 'speed_multiplier'):
                # Check if any freeze effect is affecting this enemy
                frozen = False
                for effect in spell_effects:
                    if isinstance(effect, FreezeSpell):
                        if effect.is_in_range((enemy.rect.centerx, enemy.rect.centery)):
                            frozen = True
                            break
                if not frozen:
                    enemy.speed_multiplier = 1.0

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
        
        # Draw spell effects
        for effect in spell_effects:
            if isinstance(effect, LightningSpell):
                effect.draw(screen)
            elif isinstance(effect, FreezeSpell):
                effect.draw(screen, current_time)
        
        # Spell effects are sprites, so fireballs draw automatically via the group
        spell_effects.draw(screen)

        # Draw health bar
        pygame.draw.rect(screen, RED, (10, 10, 100, 20))
        pygame.draw.rect(screen, GREEN, (10, 10, player.health, 20))
        
        # Draw EXP and LVL
        font = pygame.font.Font(None, 30)
        exp_text = font.render(f"EXP: {EXP}", True, WHITE)
        lvl_text = font.render(f"LVL: {LVL}", True, WHITE)
        screen.blit(exp_text, (10, 40))
        screen.blit(lvl_text, (10, 70))
        
        # Draw unlocked spells and cooldowns
        if spell_manager.unlocked_spells:
            spell_ui_y = 100
            small_font = pygame.font.Font(None, 20)
            for spell_key in spell_manager.unlocked_spells:
                spell_info = SPELL_INFO[spell_key]
                
                # Determine cooldown
                cooldown_remaining = 0
                if spell_key == 'lightning':
                    cooldown_remaining = spell_manager.lightning_cooldown
                elif spell_key == 'fireball':
                    cooldown_remaining = spell_manager.fireball_cooldown
                elif spell_key == 'freeze':
                    cooldown_remaining = spell_manager.freeze_cooldown
                
                # Display spell name and combo
                if cooldown_remaining > 0:
                    cd_seconds = cooldown_remaining / 1000
                    spell_text = small_font.render(f"{spell_info['name']}: {cd_seconds:.1f}s", True, (150, 150, 150))
                else:
                    spell_text = small_font.render(f"{spell_info['name']}: {spell_info['combo']}", True, (100, 255, 100))
                
                screen.blit(spell_text, (10, spell_ui_y))
                spell_ui_y += 25
    
        # Update the display
        pygame.display.flip()
    
    # Reset game state after death
    global EXP, LVL
    player.health = 100  # Reset player health for next game
    player.rect.center = (WIDTH // 2, HEIGHT // 2)  # Reset player position
    enemies.empty()  # Clear enemies
    projectiles.empty()  # Clear projectiles
    EXP = 0  # Reset experience
    LVL = 1  # Reset level
    main_menu()
    # ...existing code...


# --- Main game loop ---
def main():
    main_menu()

if __name__ == "__main__":
    main()