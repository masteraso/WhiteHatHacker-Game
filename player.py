import pygame

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, color=(0, 0, 255)):
        super().__init__()
        self.image = pygame.image.load(r'C:/Users/lenovo/Desktop/white hat game/player.png')
        self.image = pygame.transform.scale(self.image, (width, height))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed_x = 5
        self.is_jumping = False
        self.previous_y = self.rect.y
        self.gravity = 1
        self.velocity_y = 0

    def apply_gravity(self):
        self.rect.y += self.velocity_y
        self.velocity_y += self.gravity

    def update(self):
        self.previous_y = self.rect.y
        self.rect.y += self.velocity_y

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def move_left(self, speed=5):
        self.rect.x -= speed

    def move_right(self, speed=5):
        self.rect.x += speed

    def jump(self, jump_strength=10):  # Increased jump_strength from 15 to 20
        if not self.is_jumping:
            self.velocity_y = -jump_strength
            self.is_jumping = True

    def handle_event(self, event):
        pass  # No need to handle individual keydown events

    def handle_keys(self):  # New method to handle continuous key presses
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            self.jump()
        if keys[pygame.K_LEFT]:
            self.move_left(self.speed_x)
        if keys[pygame.K_RIGHT]:
            self.move_right(self.speed_x)

    def handle_platform_collisions(self, platforms):
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.velocity_y > 0:  # Moving downward
                    self.rect.bottom = platform.rect.top
                elif self.velocity_y < 0:  # Moving upward
                    self.rect.top = platform.rect.bottom
                self.velocity_y = 0
