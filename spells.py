import pygame
import math
import random

# Colors for spell effects
YELLOW = (255, 255, 0)
BRIGHT_YELLOW = (255, 255, 150)
WHITE = (255, 255, 255)
BLUE = (0, 150, 255)
ORANGE = (255, 165, 0)
BRIGHT_ORANGE = (255, 200, 100)

# Spell constants
LIGHTNING_DAMAGE = 5
LIGHTNING_RANGE = 200
LIGHTNING_COOLDOWN = 5000  # 5 seconds in milliseconds

FIREBALL_DAMAGE = 8
FIREBALL_SPEED = 5
FIREBALL_COOLDOWN = 3000  # 3 seconds

FREEZE_DURATION = 3000  # 3 seconds
FREEZE_RADIUS = 150
FREEZE_COOLDOWN = 8000  # 8 seconds

class SpellManager:
    def __init__(self):
        self.combo_buffer = []
        self.combo_timeout = 1000  # 1 second to complete combo
        self.last_key_time = 0
        self.last_update_time = pygame.time.get_ticks()
        
        # Available spells (unlocked when selected)
        self.unlocked_spells = []
        
        # Spell upgrade levels (tracks how many times each spell has been selected)
        self.spell_levels = {
            'lightning': 0,
            'fireball': 0,
            'freeze': 0
        }
        
        # Cooldowns
        self.lightning_cooldown = 0
        self.fireball_cooldown = 0
        self.freeze_cooldown = 0
        
    def update(self, current_time):
        # Calculate time delta
        delta = current_time - self.last_update_time
        self.last_update_time = current_time
        
        # Clear combo buffer if timeout exceeded
        if current_time - self.last_key_time > self.combo_timeout:
            self.combo_buffer = []
        
        # Update cooldowns
        if self.lightning_cooldown > 0:
            self.lightning_cooldown = max(0, self.lightning_cooldown - delta)
        if self.fireball_cooldown > 0:
            self.fireball_cooldown = max(0, self.fireball_cooldown - delta)
        if self.freeze_cooldown > 0:
            self.freeze_cooldown = max(0, self.freeze_cooldown - delta)
    
    def add_key_to_combo(self, key, current_time):
        """Add a key press to the combo buffer"""
        self.last_key_time = current_time
        self.combo_buffer.append(key)
        
        # Keep only last 4 keys
        if len(self.combo_buffer) > 4:
            self.combo_buffer.pop(0)
    
    def unlock_spell(self, spell_name):
        """Unlock a spell for use or upgrade it"""
        if spell_name not in self.unlocked_spells:
            self.unlocked_spells.append(spell_name)
        # Increment spell level
        self.spell_levels[spell_name] += 1
    
    def get_spell_level(self, spell_name):
        """Get the upgrade level of a spell"""
        return self.spell_levels.get(spell_name, 0)
    
    def check_lightning_combo(self, current_time):
        """Check if lightning spell combo is complete (Q -> W -> E -> R)"""
        if 'lightning' not in self.unlocked_spells or self.lightning_cooldown > 0:
            return False
        
        combo = [pygame.K_q, pygame.K_w, pygame.K_e, pygame.K_r]
        if self.combo_buffer == combo:
            self.combo_buffer = []
            self.lightning_cooldown = LIGHTNING_COOLDOWN
            return True
        return False
    
    def check_fireball_combo(self, current_time):
        """Check if fireball spell combo is complete (E -> R -> F)"""
        if 'fireball' not in self.unlocked_spells or self.fireball_cooldown > 0:
            return False
        
        combo = [pygame.K_e, pygame.K_r, pygame.K_f]
        if len(self.combo_buffer) >= 3 and self.combo_buffer[-3:] == combo:
            self.combo_buffer = []
            self.fireball_cooldown = FIREBALL_COOLDOWN
            return True
        return False
    
    def check_freeze_combo(self, current_time):
        """Check if freeze spell combo is complete (I -> C -> E)"""
        if 'freeze' not in self.unlocked_spells or self.freeze_cooldown > 0:
            return False
        
        combo = [pygame.K_i, pygame.K_c, pygame.K_e]
        if len(self.combo_buffer) >= 3 and self.combo_buffer[-3:] == combo:
            self.combo_buffer = []
            self.freeze_cooldown = FREEZE_COOLDOWN
            return True
        return False


class LightningSpell(pygame.sprite.Sprite):
    def __init__(self, start_pos, target_pos, upgrade_level=1):
        super().__init__()
        self.start_pos = start_pos
        self.target_pos = target_pos
        self.duration = 500  # Lightning effect lasts 0.5 seconds
        self.creation_time = pygame.time.get_ticks()
        self.upgrade_level = upgrade_level
        
        # Scale damage and effects with upgrade level
        self.damage = LIGHTNING_DAMAGE + (upgrade_level - 1) * 3
        self.chain_count = upgrade_level  # Chain to more enemies per level
        
        self.hit_enemies = set()  # Track which enemies have been hit
        
        # Create a transparent surface for sprite (required for pygame sprite)
        self.image = pygame.Surface((1, 1), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=start_pos)
        
        # Create lightning segments for visual effect
        self.segments = self._generate_lightning_path()
        
    def _generate_lightning_path(self):
        """Generate a jagged lightning path from start to target"""
        segments = []
        num_segments = 5
        
        dx = self.target_pos[0] - self.start_pos[0]
        dy = self.target_pos[1] - self.start_pos[1]
        
        current_pos = list(self.start_pos)
        
        for i in range(num_segments):
            progress = (i + 1) / num_segments
            
            # Calculate next point with some randomness
            next_x = self.start_pos[0] + dx * progress + random.randint(-20, 20)
            next_y = self.start_pos[1] + dy * progress + random.randint(-20, 20)
            
            # Last segment should always hit target
            if i == num_segments - 1:
                next_x = self.target_pos[0]
                next_y = self.target_pos[1]
            
            segments.append((tuple(current_pos), (next_x, next_y)))
            current_pos = [next_x, next_y]
        
        return segments
    
    def update(self, current_time):
        """Update lightning spell"""
        if current_time - self.creation_time > self.duration:
            self.kill()
    
    def draw(self, surface):
        """Draw the lightning effect"""
        # Draw multiple lightning bolts for effect
        for i in range(3):
            offset = i * 2
            for start, end in self.segments:
                color = BRIGHT_YELLOW if i == 0 else YELLOW
                thickness = 3 - i
                pygame.draw.line(surface, color, start, end, thickness)
    
    def check_hit(self, enemy):
        """Check if enemy is within lightning range and hasn't been hit yet"""
        if id(enemy) in self.hit_enemies:
            return False
        
        # Check if enemy is close to any lightning segment
        for start, end in self.segments:
            dist = self._point_to_line_distance(
                (enemy.rect.centerx, enemy.rect.centery),
                start, end
            )
            if dist < 30:  # Lightning hit radius
                self.hit_enemies.add(id(enemy))
                return True
        return False
    
    def _point_to_line_distance(self, point, line_start, line_end):
        """Calculate minimum distance from point to line segment"""
        px, py = point
        x1, y1 = line_start
        x2, y2 = line_end
        
        # Vector from line start to end
        dx = x2 - x1
        dy = y2 - y1
        
        if dx == 0 and dy == 0:
            return math.hypot(px - x1, py - y1)
        
        # Calculate parameter t for closest point on line
        t = max(0, min(1, ((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy)))
        
        # Find closest point on line segment
        closest_x = x1 + t * dx
        closest_y = y1 + t * dy
        
        return math.hypot(px - closest_x, py - closest_y)


class FireballSpell(pygame.sprite.Sprite):
    def __init__(self, start_pos, direction, upgrade_level=1):
        super().__init__()
        self.upgrade_level = upgrade_level
        
        # Scale size with upgrade level
        base_size = 40
        size = base_size + (upgrade_level - 1) * 10
        radius = size // 2
        
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(self.image, ORANGE, (radius, radius), radius)
        pygame.draw.circle(self.image, BRIGHT_ORANGE, (radius, radius), int(radius * 0.6))
        
        self.rect = self.image.get_rect(center=start_pos)
        self.direction = direction
        
        # Scale damage and speed with upgrade level
        self.damage = FIREBALL_DAMAGE + (upgrade_level - 1) * 4
        self.speed = FIREBALL_SPEED + (upgrade_level - 1) * 0.5
        
        self.lifetime = 3000 + (upgrade_level - 1) * 1000  # Longer lifetime per level
        self.creation_time = pygame.time.get_ticks()
        self.hit_enemies = set()  # Track which enemies have been hit
    
    def update(self, current_time, screen_rect):
        """Update fireball position"""
        self.rect.x += self.direction[0] * self.speed
        self.rect.y += self.direction[1] * self.speed
        
        # Remove if off screen or lifetime expired
        if not screen_rect.colliderect(self.rect) or current_time - self.creation_time > self.lifetime:
            self.kill()


class FreezeSpell(pygame.sprite.Sprite):
    def __init__(self, center_pos, upgrade_level=1):
        super().__init__()
        self.center_pos = center_pos
        self.upgrade_level = upgrade_level
        
        # Scale radius and duration with upgrade level
        self.radius = FREEZE_RADIUS + (upgrade_level - 1) * 50
        self.duration = FREEZE_DURATION + (upgrade_level - 1) * 1000
        self.slow_multiplier = 0.3 - (upgrade_level - 1) * 0.05  # Slows more per level (min 0.1)
        self.slow_multiplier = max(0.1, self.slow_multiplier)
        
        self.creation_time = pygame.time.get_ticks()
        self.affected_enemies = {}  # enemy_id: original_speed
        
        # Create a transparent surface for sprite (required for pygame sprite)
        self.image = pygame.Surface((1, 1), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=center_pos)
    
    def update(self, current_time):
        """Update freeze spell"""
        if current_time - self.creation_time > self.duration:
            # Restore enemy speeds before killing
            self.restore_enemy_speeds()
            self.kill()
    
    def draw(self, surface, current_time):
        """Draw the freeze effect"""
        # Pulsing effect
        elapsed = current_time - self.creation_time
        pulse = abs(math.sin(elapsed / 200)) * 0.3 + 0.7
        
        # Draw expanding rings
        for i in range(3):
            radius = int(self.radius * pulse) - i * 20
            if radius > 0:
                alpha = int(100 * (1 - i / 3))
                color = (*BLUE[:3], alpha) if len(BLUE) == 4 else BLUE
                pygame.draw.circle(surface, color, self.center_pos, radius, 2)
    
    def is_in_range(self, enemy_pos):
        """Check if position is within freeze radius"""
        dx = enemy_pos[0] - self.center_pos[0]
        dy = enemy_pos[1] - self.center_pos[1]
        return math.hypot(dx, dy) <= self.radius
    
    def freeze_enemy(self, enemy):
        """Apply freeze effect to enemy"""
        enemy_id = id(enemy)
        if enemy_id not in self.affected_enemies:
            # Store original speed and reduce it
            if hasattr(enemy, 'original_speed'):
                self.affected_enemies[enemy_id] = enemy.original_speed
            else:
                # Detect enemy type and store appropriate speed
                if hasattr(enemy, 'health') and enemy.health > 10:
                    self.affected_enemies[enemy_id] = 1.5  # Boss
                elif hasattr(enemy, 'health') and enemy.health > 1:
                    self.affected_enemies[enemy_id] = 1  # Tank
                else:
                    self.affected_enemies[enemy_id] = 2  # Regular
            
            # Slow down enemy
            enemy.speed_multiplier = self.slow_multiplier
    
    def restore_enemy_speeds(self):
        """Restore all affected enemies to normal speed"""
        # This will be handled in the main game loop
        pass


# Spell info for selection menu
SPELL_INFO = {
    'lightning': {
        'name': 'Lightning Strike',
        'combo': 'Q-W-E-R',
        'description': 'Chain lightning that damages enemies',
        'damage': LIGHTNING_DAMAGE,
        'cooldown': LIGHTNING_COOLDOWN / 1000
    },
    'fireball': {
        'name': 'Fireball',
        'combo': 'E-R-F',
        'description': 'Launch a powerful fireball',
        'damage': FIREBALL_DAMAGE,
        'cooldown': FIREBALL_COOLDOWN / 1000
    },
    'freeze': {
        'name': 'Freeze Field',
        'combo': 'I-C-E',
        'description': 'Slow enemies in a radius',
        'duration': FREEZE_DURATION / 1000,
        'cooldown': FREEZE_COOLDOWN / 1000
    }
}
