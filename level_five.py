import pygame
import sys
import random
from player import Player


def level_four(screen, remaining_time):
    clock = pygame.time.Clock()
    FPS = 60

    progress_bar_font = pygame.font.Font(None, 30)
    text_font = pygame.font.Font(None, 30)
    running = True

    def draw_text(text, y, font, color=(255, 255, 255)):
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.centerx = screen.get_width() // 2
        text_rect.y = y
        screen.blit(text_surface, text_rect)

    while running:
        elapsed_time = clock.tick(FPS)/1000
        remaining_time -= elapsed_time
        
        initial_remaining_time = remaining_time
        
        current_time = pygame.time.get_ticks()
        if current_time - start_time > message_display_time * 1000 and current_message_index < len(messages) - 1:
            current_message_index += 1
            start_time = current_time
            
class DataFragment(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load(r'C:/Users/lenovo/Desktop/white hat game/data.png')
        self.rect = self.image.get_rect()

    def draw(self, screen):
        screen.blit(self.image, self.rect)

class Enemy(pygame.sprite.Sprite):
    def __init__(self, desired_width=50, desired_height=50):  # Add default values for width and height
        super().__init__()
        original_image = pygame.image.load(r'C:/Users/lenovo/Desktop/white hat game/enemy.png')
        self.image = pygame.transform.scale(original_image, (desired_width, desired_height))
        self.rect = self.image.get_rect()
        self.speed_x = random.choice([-2, 2])

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.rect.y -= self.speed
            if event.key == pygame.K_DOWN:
                self.rect.y += self.speed
            if event.key == pygame.K_LEFT:
                self.rect.x -= self.speed
            if event.key == pygame.K_RIGHT:
                self.rect.x += self.speed

    def update(self, screen):
        # Keep the player within the screen boundaries
        self.rect.x = max(0, min(screen.get_width() - self.rect.width, self.rect.x))
        self.rect.y = max(0, min(screen.get_height() - self.rect.height, self.rect.y))
        self.rect.x += self.speed_x
        if self.rect.x <= 0 or self.rect.x + self.rect.width >= screen.get_width():
            self.speed_x *= -1


    def draw(self, screen):
        screen.blit(self.image, self.rect)

def generate_data_fragments(screen):
    data_fragments = []
    for _ in range(5):  # Adjust the number of data fragments as needed
        fragment = DataFragment()
        fragment.rect.x = random.randint(0, screen.get_width() - fragment.rect.width)
        fragment.rect.y = random.randint(0, screen.get_height() - fragment.rect.height)
        data_fragments.append(fragment)
    return data_fragments

def generate_enemies(screen):
    enemies = []
    for _ in range(10):  # Adjust the number of enemies as needed
        enemy = Enemy()
        enemy.rect.x = random.randint(0, screen.get_width() - enemy.rect.width)
        enemy.rect.y = random.randint(0, screen.get_height() - enemy.rect.height)
        enemies.append(enemy)
    return enemies

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, color=(255, 255, 255)):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)


def level_five(screen, remaining_time):
    clock = pygame.time.Clock()
    FPS = 60
    text_font = pygame.font.Font(None, 30)
    running = True

    def draw_text(text, y, font, color=(255, 255, 255)):
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.centerx = screen.get_width() // 2
        text_rect.y = y
        screen.blit(text_surface, text_rect)

    def draw_countdown():
        draw_text(f"Time remaining: {int(remaining_time)} seconds", 200, text_font)
                
    # Initialize level variables, load assets, and set up the storyline
    pygame.font.init()
    ai_font = pygame.font.Font(None, 30)
    background = pygame.image.load(r'C:/Users/lenovo/Desktop/white hat game/background.png')
    
    player_x = screen.get_width() // 2
    player_y = screen.get_height() // 2
    player_width = 50  # Replace with your desired player width
    player_height = 50  # Replace with your desired player height
    player = Player(x=player_x, y=player_y, width=player_width, height=player_height)
    enemies = generate_enemies(screen)
    data_fragments = generate_data_fragments(screen)
    collected_fragments = 0
    fragments_needed = len(data_fragments)
    
    pygame.mixer.init()
    music_path = "C:\\Users\\lenovo\\Desktop\\white hat game\\theme3.wav"  # Add your music file path here
    pygame.mixer.music.load(music_path)
    pygame.mixer.music.play(-1)  # Play the music in a loop

    ai_manipulation_counter = 0
    
    while running:
        screen.fill((0, 0, 0))
        screen.blit(background, (0, 0))
        remaining_time -= 1 / FPS

        # Create a ground platform
        ground_platform = Platform(0, screen.get_height() - 50, screen.get_width(), 50)

        # Create additional platforms
        platforms = [
            Platform(100, 300, 200, 20),
            Platform(400, 200, 200, 20),
            Platform(700, 100, 200, 20),
            # Add more platforms as needed
        ]

        # Add the ground platform to the platforms list
        platforms.append(ground_platform)

        # Draw platforms
        for platform in platforms:
            platform.draw(screen)

        player.apply_gravity()
        player.handle_keys()
        player.update()  # Assuming your Player class has an update method
        player.handle_platform_collisions(platforms)

        # Check for user input and update game state
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            # Add event handling for level-specific gameplay mechanics
            player.handle_event(event)  # Assuming your Player class has a handle_event method

        # Update game objects, animations, and level progress
        player.update()  # Assuming your Player class has an update method
        for enemy in enemies:
            enemy.update(screen)  # Assuming your Enemy class has an update method

        # Environmental storytelling: update the game world based on AI's influence
        # You can add environmental changes, such as shifting walls, flickering lights, etc.

        # Meta-gameplay elements: have the AI communicate with the player
        if ai_manipulation_counter % 300 == 0:  # Every 5 seconds
            ai_message = "I'm watching you..."
            message_surface = ai_font.render(ai_message, True, (255, 255, 255))
            screen.blit(message_surface, (screen.get_width() // 2 - message_surface.get_width() // 2, 50))

        # Dynamic game mechanics: manipulate the gameplay experience
        if random.random() < 0.01:  # 1% chance per frame
            # Change game rules, player abilities, or generate new challenges
            # Example: change player's speed randomly
            player.speed = random.randint(3, 10)

        ai_manipulation_counter += 1


        # Draw the updated game objects and scene
        player.draw(screen)  # Assuming your Player class has a draw method
        for enemy in enemies:
            enemy.draw(screen)  # Assuming your Enemy class has a draw method
            
        # Check for player collision with data fragments
        for fragment in data_fragments:
            if player.rect.colliderect(fragment.rect):
                data_fragments.remove(fragment)
                collected_fragments += 1

                # Increase enemy spawn rate as more fragments are collected
                if collected_fragments % 2 == 0:
                    enemies.extend(generate_enemies(screen))
        
        # Draw data fragments
        for fragment in data_fragments:
            fragment.draw(screen)

        # Draw exit door after collecting all fragments
        if collected_fragments == fragments_needed:
            exit_door_image = pygame.image.load(r'C:/Users/lenovo/Desktop/white hat game/exit_door.png')
            exit_door_rect = exit_door_image.get_rect()
            exit_door_rect.x = screen.get_width() // 2 - exit_door_rect.width // 2
            exit_door_rect.y = screen.get_height() // 2 - exit_door_rect.height // 2
            screen.blit(exit_door_image, exit_door_rect)

        # Check for player collision with exit door after collecting all fragments
            if player.rect.colliderect(exit_door_rect):
                running = False
                # Proceed to next level or show the end screen
                print("Level completed!")
                
        draw_countdown()        
        pygame.display.flip()
        clock.tick(FPS)
