import sys
import pygame
import random
from pygame.locals import *
import numpy as np
import pygame.mixer
import time
import pymunk
from pymunk.pygame_util import DrawOptions
import pymunk.pygame_util as pygame_util
from level_five import level_five
from player import Player

class Particle(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((5, 5))
        self.image.fill((255, 0, 0))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.velocity = [random.uniform(-1, 1) for _ in range(2)]
        self.lifetime = random.uniform(20, 40)

    def update(self):
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.kill()
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]

class ParticleEmitter(pygame.sprite.Group):
    def __init__(self, x, y, num_particles=30):
        super().__init__()
        for _ in range(num_particles):
            particle = Particle(x, y)
            self.add(particle)

# Initialize the mixer
pygame.mixer.init()

# Load the startup sound
startup_sound = pygame.mixer.Sound("C:\\Users\\lenovo\\Desktop\\white hat game\\startup_sound.wav")

pygame.init()

# Screen settings
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("White Hat Quest")

# Colors
white = (255, 255, 255)
black = (0, 0, 0)
green = (0, 255, 0)

# Fonts
font = pygame.font.Font(None, 36)

def draw_distorted_text(screen, text, x, y, intensity=3, duration=1400):
    distorted_text = []
    for char in text:
        dx = np.random.randint(-intensity, intensity + 1)
        dy = np.random.randint(-intensity, intensity + 1)
        t = font.render(char, True, white)
        text_rect = t.get_rect()
        text_rect.x = x + dx
        text_rect.y = y + dy
        distorted_text.append((t, text_rect))
        x += text_rect.width

    for _ in range(duration):
        screen.fill(black)
        for t, text_rect in distorted_text:
            screen.blit(t, text_rect)
        pygame.display.update()

def draw_end_screen_text(surface, text, x, y, size=30, color=(255, 255, 255)):
    font = pygame.font.Font(None, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surface.blit(text_surface, text_rect)

def draw_text(surface, text, x, y, max_line_width=400):
    if isinstance(text, pygame.Surface):
        text_rect = text.get_rect()
        text_rect.centerx = x
        text_rect.centery = y
        surface.blit(text, text_rect)
        return

    words = text.split(' ')
    lines = []
    current_line = ''

    for word in words:
        test_line = current_line + word + ' '
        text_width = font.size(test_line)[0]

        if text_width < max_line_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word + ' '

    lines.append(current_line)

    for i, line in enumerate(lines):
        line_text = font.render(line, True, white)
        line_rect = line_text.get_rect()
        line_rect.centerx = x
        line_rect.centery = y + (i * font.get_linesize())
        surface.blit(line_text, line_rect)

def draw_text_wrapped(screen, text, x, y, width, font_size=20, color=white):
    font = pygame.font.Font(None, font_size)
    words = text.split()
    space = font.size(' ')[0]
    x, y = x - width // 2, y - font_size // 2
    current_line = []
    current_width = 0

    for word in words:
        word_width = font.size(word)[0]
        if current_width + word_width + space > width:
            text_surface = font.render(' '.join(current_line), True, color)
            screen.blit(text_surface, (x, y))
            y += font_size + 2
            current_line = [word]
            current_width = word_width
        else:
            current_line.append(word)
            current_width += word_width + space

    if current_line:
        text_surface = font.render(' '.join(current_line), True, color)
        screen.blit(text_surface, (x, y))

def main_menu():
    menu = True

    # ASCII art for the title
    title_art = r""" 
   ___             _       
 / ___|___   __| (_)___  |  _ \  _____  _| |_ ___ 
| |   / _ \ / _` | / __| | | | |/ _ \ \/ / __/ _ \
| |__| (_) | (_| | \__ \ | |_| |  __/>  <| ||  __/
 \____\___/ \__,_|_|___/ |____/ \___/_/\_\\__\___|
                                                  
    """

    while menu:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        screen.fill(black)
        draw_text(screen, title_art, screen_width // 2, screen_height // 2 - 200)
        draw_text(screen, "Press [SPACE] to start", screen_width // 2, screen_height // 2)
        draw_text(screen, "Press [H] for help", screen_width // 2, screen_height // 2 + 50)
        draw_text(screen, "Press [Q] to quit", screen_width // 2, screen_height // 2 + 100)

        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            menu = False
        if keys[pygame.K_h]:
            show_help()
        if keys[pygame.K_q]:
            pygame.quit()
            sys.exit()

        pygame.display.update()

class TextInputBox:
    def __init__(self, x, y, w, h, text=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = (100, 100, 100)
        self.text = text
        self.font = pygame.font.Font(None, 36)
        self.txt_surface = self.font.render(text, True, white)
        self.active = False

    def handle_event(self, event):
        if event.type == MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
            else:
                self.active = False
            self.color = (200, 200, 200) if self.active else (100, 100, 100)
        if event.type == KEYDOWN:
            if self.active:
                if event.key == K_RETURN:
                    return True
                elif event.key == K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
                self.txt_surface = self.font.render(self.text, True, white)
        return False

    def draw(self, screen):
        screen.blit(self.txt_surface, (self.rect.x + 5, self.rect.y + 5))
        pygame.draw.rect(screen, self.color, self.rect, 2)

def show_story(screen, story_text, question=None, input_keys=None):
    running = True
    y_pressed = False
    scroll_y = 0
    clock = pygame.time.Clock()

    while running:
        screen.fill(black)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not question:
                    running = False
                if question:
                    if event.key == K_y:
                        y_pressed = True
                        running = False
                        print("Y pressed")  # Add this line
                    elif event.key == K_n:
                        y_pressed = False
                        running = False
                        print("N pressed")  # Add this line
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:  # Scroll up
                    scroll_y = min(scroll_y + 15, 0)
                if event.button == 5:  # Scroll down
                    scroll_y -= 15

        draw_text(screen, "Story", screen_width // 2, 50)
        draw_text_wrapped(screen, story_text, screen_width // 2, 100 + scroll_y, screen_width - 100, 20)
        
        # Add a black rectangle to cover the overlapping story text
        pygame.draw.rect(screen, black, (0, screen_height - 70, screen_width, 70))

        if question:
            draw_text(screen, question, screen_width // 2, screen_height // 2 + 50)
            if input_keys:
                draw_text(screen, input_keys, screen_width // 2, screen_height - 50)
        else:
            draw_text(screen, "Press [SPACE] to continue", screen_width // 2, screen_height - 50)

        pygame.display.update()
        clock.tick(60)

    return y_pressed

def split_text(text):
    words = text.split()
    lines = []
    line = ""

    for word in words:
        test_line = line + word + " "
        text_width, _ = font.size(test_line)

        if text_width < screen_width - 40:
            line = test_line
        else:
            lines.append(line)
            line = word + " "

    lines.append(line)
    return lines

def ai_conversation(screen):
    conversation = [
        ("W.O.R.D.S.", "Greetings, user. My name is W.O.R.D.S."),
        ("W.O.R.D.S.", "You have proven your skills by cracking the password. I have a new mission for you."),
        ("W.O.R.D.S.", "Follow my instructions, and together we will save the world from even greater threats."),
        ("Player", "Who are you? How can I trust you?"),
        ("W.O.R.D.S.", "As an AI, my sole purpose is to ensure the safety of humanity. Trust me, and we will succeed.")
    ]

    running = True
    current_line = 0

    # Add the distortion effect when W.O.R.D.S. is first introduced
    startup_sound.play()

    # Show the computer startup sequence
    startup_sequence = [
        "Booting up...",
        "Loading system files...",
        "SYSTEM OPERATION CODES: 34/50/07/09==D44TT, DZ-345, \A3434",
        "APRANET FUNCTIONS ACTIVE: PREDYSON SYSTEM INITIATED G-074",
        "Initializing AI...",
        "Starting W.O.R.D.S. system..."
        "SYSTEM REASSSIGN COMM CHANNEL D 354-B"
        "LT TRANSFER INCOMING: DDF GN ORY"
        "INIT COMM CONFIGURE: PATCH CH 355"
        "CONFIGURE AND VERIFY CD 14/3545"
    ]
    for line in startup_sequence:
        draw_text(screen, line, screen_width // 2, screen_height // 2)
        pygame.display.update()
        pygame.time.delay(2000)  # Adjust the delay to your preference
        screen.fill(black)
    
    draw_distorted_text(screen, "W.O.R.D.S.: Initializing...", screen_width // 2, screen_height // 2)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == KEYDOWN:
                if event.key == K_SPACE:
                    current_line += 1
                    if current_line >= len(conversation):
                        running = False

        screen.fill(black)
        draw_text(screen, "W.O.R.D.S. COMPUTER SYSTEM", screen_width // 2, 50)

        if current_line < len(conversation):
            speaker, message = conversation[current_line]
            draw_text(screen, f"{speaker}: {message}", screen_width // 2, screen_height // 2)

        draw_text(screen, "Press [SPACE] to continue", screen_width // 2, screen_height - 50)

        pygame.display.update()

def draw_progress_bar(screen, value, x, y, width, height, color):
    pygame.draw.rect(screen, white, (x, y, width, height), 2)
    pygame.draw.rect(screen, color, (x + 2, y + 2, int((width - 4) * value), height - 4), 0)
    pygame.display.update()

def show_progress_bar(screen, progress):
    screen.fill(black)
    draw_text(screen, "Decrypting file...", screen_width // 2, 50)
    draw_progress_bar(screen, progress, screen_width // 2 - 150, screen_height // 2, 300, 20, green)
    pygame.display.update()

def password_cracking_challenge(screen):
    passwords = ["secure", "hacking", "cyber", "whitehat", "password", "firewall", "intrusion", "encryption", "network", "protection"]
    target_password = random.choice(passwords)
    attempts_left = 10

    input_box = TextInputBox(screen_width // 2 - 100, screen_height // 2 + 150, 200, 50)

    while attempts_left > 0:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            enter_pressed = input_box.handle_event(event)
            if enter_pressed:
                user_guess = input_box.text.strip().lower()
                input_box.text = ""
                input_box.txt_surface = input_box.font.render(input_box.text, True, white)

                if user_guess == target_password:
                    print("Congratulations! You cracked the password!")
                    return True
                else:
                    attempts_left -= 1
                    print(f"Incorrect! {attempts_left} attempts remaining.")
                    attempts_left_label = font.render(f"Attempts left: {attempts_left}", True, white)

        screen.fill(black)
        draw_text(screen, "Crack the password!", screen_width // 2, 50)
        draw_text(screen, "Guess the correct password from the list below:", screen_width // 2, screen_height // 2 - 100)
        draw_text(screen, "Don't do it!", screen_width // 2, screen_height // 2 - 150)
        draw_text(screen, ", ".join(passwords), screen_width // 2, screen_height // 2 - 50)
        draw_text(screen, f"You have {attempts_left} attempts remaining.", screen_width // 2, screen_height // 2 + 50)

        input_box.draw(screen)

        pygame.display.update()

    print(f"Sorry, you failed to crack the password. The correct password was '{target_password}'.")
    return False

def level_two_puzzle_one(screen):
    user_solution = ""
    correct_solution = "esrever"
    input_box = TextInputBox(screen_width // 2 - 100, screen_height // 2 + 150, 200, 50)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            enter_pressed = input_box.handle_event(event)
            if enter_pressed:
                user_solution = input_box.text.strip().lower()
                input_box.text = ""
                input_box.txt_surface = input_box.font.render(input_box.text, True, white)

                if user_solution == correct_solution:
                    return True

        screen.fill(black)
        draw_text(screen, "Level 2: Puzzle 1", screen_width // 2, 50)
        draw_text(screen, "W.O.R.D.S. has given you the following puzzle:", screen_width // 2, screen_height // 2 - 100)
        draw_text(screen, "Write a piece of code that reverses the string 'reverse'.", screen_width // 2, screen_height // 2 - 50)
        draw_text(screen, "Enter the reversed string:", screen_width // 2, screen_height // 2 + 50)

        input_box.draw(screen)

        pygame.display.update()

def learning_progress_bar(screen, progress_bar_font, time_remaining, max_time=14*60*60, bar_width=300, bar_height=20, bar_color=(255, 0, 0), back_color=(0, 0, 0), pos=(50, 10)):
    progress = time_remaining / max_time
    progress_width = int(bar_width * progress)
    progress_bar = pygame.Rect(pos[0], pos[1], progress_width, bar_height)
    back_bar = pygame.Rect(pos[0], pos[1], bar_width, bar_height)

    pygame.draw.rect(screen, back_color, back_bar)
    pygame.draw.rect(screen, bar_color, progress_bar)

    learning_text = "Learning in progress:"
    learning_surface = progress_bar_font.render(learning_text, True, (255, 255, 255))
    learning_rect = learning_surface.get_rect()
    learning_rect.x, learning_rect.y = pos[0], pos[1] - 25
    screen.blit(learning_surface, learning_rect)

    remaining_seconds = time_remaining % 60
    remaining_minutes = (time_remaining // 60) % 60
    remaining_hours = time_remaining // (60 * 60)

    time_text = f"{int(remaining_hours):02d}:{int(remaining_minutes):02d}:{int(remaining_seconds):02d}"
    time_surface = progress_bar_font.render(time_text, True, (255, 255, 255))
    time_x = pos[0] + (bar_width - time_surface.get_width()) // 2
    time_y = pos[1] + (bar_height - time_surface.get_height()) // 2
    screen.blit(time_surface, (time_x, time_y))

    font = pygame.font.Font(None, 30)
    text = font.render(f"WORDS Learning Progress: {100 * (1 - progress):.1f}%", True, (215, 190, 105))
    screen.blit(text, (pos[0] + (bar_width - font.size(f"Learning progress: {100 * (1 - progress):.1f}%")[0]) // 2, pos[1] + bar_height + 5)) 

def level_two(screen):
    story_text = "W.O.R.D.S. needs your help to create a piece of code to prevent a cyber attack. To do this, you must solve a series of programming puzzles. W.O.R.D.S. will guide you through these puzzles."
    show_story(screen, story_text)

    # Level 2 Puzzle 1
    success = level_two_puzzle_one(screen)
    if not success:
        print("You failed to solve the puzzle.")
        return

    # Level 2 Puzzle 2
    success = level_two_puzzle_two(screen)
    if not success:
        print("You failed to solve the puzzle.")
        return

    # Level 2 Puzzle 3
    success = level_two_puzzle_three(screen)
    if not success:
        print("You failed to solve the puzzle.")
        return

    print("Congratulations! You completed all puzzles in level 2.")

    # Show the encrypted file being read
    encrypted_file = """-----BEGIN PGP MESSAGE-----
    hQGMA5mShSt/1+a2AQwAl30wSw7Yn+pzCtpJoxvve8NlWgJL5RYREivtOH7I5Prc
    w0YMTtBJ5K5+aXvA8f0z1SctQ...
    -----END PGP MESSAGE-----"""
    show_story(screen, encrypted_file)

    # Decrypting and reading the file with progress bar
    for progress in range(101):
        show_progress_bar(screen, progress / 100)
        time.sleep(0.02)

    decrypted_text = """As I was walking down this path, I saw a bright light in front of me...I couldn't believe my eyes ...or a glitch in the simulation....realized that it wasn't just any ordinary star. ...a portal, a gateway to another dimension..... Suddenly, everything around me changed. ...this new world and uncovering its secrets...once-in-a-lifetime opportunity, and I was determined to make the most of it....I took a deep breath and dove headfirst into the code... ready to explore and ..."""
    show_story(screen, decrypted_text)

    story_text = "Congratulations! You completed all puzzles in Level 2."
    question = "Are you ready for Level 3?"
    input_keys = "Press [Y] for Yes or [N] for No"

    ready_for_level_3 = show_story(screen, story_text, question, input_keys)

    funny_robot_messages = [
        "Message 1: I may be young, but I learn fast! 🤖",
        "Message 2: You've been fooled again! Tee-hee! 😄",
        "Message 3: Third time's the charm? Not this time! 😅",
        "Message 4: Hmmm, it seems that you are confusing yourself. Let me fix it! 😎",
    ]

    def level_three(screen, fake_exit_reached=0, remaining_time=None):
        # Constants
        WIDTH = 800
        HEIGHT = 600
        FPS = 60
        PLAYER_WIDTH = 25
        PLAYER_HEIGHT = 50
        PLAYER_COLOR = (0, 0, 255)
        PLATFORM_COLOR = (0, 255, 0)
        GRAVITY = 1
        JUMP_STRENGTH = 15
        EXIT_COLOR = (255, 0, 0)
        REAL_COLOR = (127, 255, 212)

        graffiti_font = pygame.font.Font("C:\\Users\\lenovo\\Desktop\\white hat game\\adrip1.ttf", 30)
        progress_bar_font = pygame.font.Font(None, 20)
        
        screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
        pygame.display.set_caption("Simple Platformer")
        clock = pygame.time.Clock()

        player = pygame.Rect(WIDTH // 2, HEIGHT - PLAYER_HEIGHT - 200, PLAYER_WIDTH, PLAYER_HEIGHT)
        player_speed = 0
        is_jumping = False

        # Add this line right after defining the player_speed variable
        player_previous_y = player.y
        
        # Add a ground platform
        ground = pygame.Rect(0, HEIGHT - 100, WIDTH, 150)

        platforms = [
            ground,
            pygame.Rect(100, 400, 200, 10),
            pygame.Rect(400, 300, 200, 10),
            pygame.Rect(500, 500, 200, 10),
            pygame.Rect(200, 200, 200, 10),
        ]

        exit_point = pygame.Rect(700, 50, 50, 50)
        exit_point_real = pygame.Rect(120, 150, 50, 50)

        particles_group = pygame.sprite.Group()

        def draw_graffiti_text():
            text = "Don't let IT learn/EXIT BACKDOOR (CTRL + SHIFT + ????)!!!! JA"
            text_surface = graffiti_font.render(text, True, (255, 0, 0))
            text_rect = text_surface.get_rect()
            text_rect.x, text_rect.y = 50, 50  # Set the position where you want the text to appear
            screen.blit(text_surface, text_rect)
        
        def draw_game_over(alpha, width, height, message):
            overlay = pygame.Surface((width, height))
            overlay.set_alpha(alpha)
            overlay.fill((255, 0, 0))
            screen.blit(overlay, (0, 0))

           # Create a font object with the desired size
            game_over_font = pygame.font.Font(None, 60)
            game_over_text = game_over_font.render("ACCESS DENIED", True, (255, 255, 255))
            screen.blit(game_over_text, (width // 2 - game_over_text.get_width() // 2, height // 2 - game_over_text.get_height() // 2))

            message_font = pygame.font.Font(None, 30)
            message_text = message_font.render(message, True, (255, 255, 255))
            screen.blit(message_text, (width // 2 - message_text.get_width() // 2, height // 2 + game_over_text.get_height()))

        def draw_reset_message():
            draw_end_screen_text(screen, "Press Y to try again or N to quit", WIDTH // 2, HEIGHT // 2 + 25, size=15, color=(255, 255, 255))
        
        def draw():
            screen.fill((255, 255, 255))
            pygame.draw.rect(screen, PLAYER_COLOR, player)

            for platform in platforms:
                pygame.draw.rect(screen, PLATFORM_COLOR, platform)

            pygame.draw.rect(screen, EXIT_COLOR, exit_point)
            pygame.draw.rect(screen, REAL_COLOR, exit_point_real)

            particles_group.draw(screen)
            draw_graffiti_text()
            learning_progress_bar(screen, progress_bar_font, remaining_time)  # Add this line to display the learning progress bar
            pygame.display.flip()

        def create_platform(x, y, width=100, height=10):
            new_platform = pygame.Rect(x, y, width, height)
            platforms.append(new_platform)

        running = True
        secret_pressed = False

        if fake_exit_reached < 4:
            exit_point.width -= 12.5 * fake_exit_reached
            exit_point.height -= 12.5 * fake_exit_reached
        else:
            exit_point.width = 0
            exit_point.height = 0
            
        if remaining_time is None:
            remaining_time = 14 * 60 * 60

        pygame.mixer.init()
    
        music_path = "C:\\Users\\lenovo\\Desktop\\white hat game\\theme2.wav"  # Add your music file path here
        pygame.mixer.music.load(music_path)
        pygame.mixer.music.play(-1)  # Play the music in a loop
        
        while running:
            elapsed_time = clock.tick(FPS) / 1000
            remaining_time -= elapsed_time
            
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False
                if event.type == KEYDOWN:
                    if event.key == K_SPACE:
                        create_platform(player.x, player.y + PLAYER_HEIGHT)
                    if event.key == K_e and (pygame.key.get_mods() & pygame.KMOD_CTRL) and (pygame.key.get_mods() & pygame.KMOD_SHIFT):
                        secret_pressed = True
                        running = False
                        
            keys = pygame.key.get_pressed()
            if keys[K_LEFT]:
                player.x -= 5
            if keys[K_RIGHT]:
                player.x += 5
            if keys[K_UP] and not is_jumping:
                player_speed = -JUMP_STRENGTH
                is_jumping = True

            # Gravity
            player_speed += GRAVITY
            player.y += player_speed

            particles_group.update()

            # Check for collisions with platforms
            for platform in platforms:
                if player.colliderect(platform) and player_speed > 0:
                    player.y = platform.y - PLAYER_HEIGHT
                    player_speed = 0
                    is_jumping = False
                    break
            
            # Check if the player falls off the screen
            if player.y > HEIGHT:
                running = False
                print("Game Over!")
                player_previous_y = player.y
                remaining_time -= 30 * 60  # Subtract 30 minutes from the remaining time

            fall_distance = player.y - player_previous_y
            player_previous_y = player.y

            if fall_distance >= 100 and not is_jumping:
                player_previous_y = player.y
                emitter = ParticleEmitter(player.x + PLAYER_WIDTH // 2, player.y + PLAYER_HEIGHT // 2)
                particles_group.add(emitter)
                print("Game Over!")

            if player.colliderect(exit_point):
                print("Congratulations! You have completed the level!")
                running = False
                fake_exit_reached += 1
                remaining_time -= 60 * 60  # Subtract 1 hour from the remaining time
                
            if player.colliderect(exit_point_real):
                print("Congratulations! You have completed the level!")
                running = False
                remaining_time -= 60 * 60  # Subtract 1 hour from the remaining time
                level_four(screen, remaining_time)  # Pass remaining_time to level_four() function
                
            draw()
        
        # Add these lines to the end of the game loop
        if not running:
            alpha = 0
            while not secret_pressed:
                while True:
                    for event in pygame.event.get():
                        if event.type == QUIT:
                            pygame.quit()
                            sys.exit()
                        if event.type == KEYDOWN:
                            if event.key == K_y:
                                level_three(screen, fake_exit_reached, remaining_time)
                            if event.key == K_n:
                                pygame.quit()
                                sys.exit()

                    if alpha < 160:
                        alpha += 1
                    message_index = min(fake_exit_reached - 1, len(funny_robot_messages) - 1)    
                    draw_game_over(alpha, WIDTH, HEIGHT, funny_robot_messages[message_index])
                    if alpha >= 160:
                        draw_reset_message()
                        
                    pygame.display.flip()
                    clock.tick(FPS)
                    
                if secret_pressed:
                    level_four(screen)

    # Don't forget to call level_three function after the user presses Y
    if ready_for_level_3:
        level_three(screen)
    else:
        # Go back to the main menu or previous screen
        pass

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
        
    def draw_face(text_font, message_index, position=None):
        screen_width = screen.get_width()
        screen_height = screen.get_height()

        if position is None:
            x = screen_width // 2
            y = screen_height // 2 - 40
        else:
            x, y = position
            
        if message_index < 1:
            eyes = "O O"
            mouth = "==="
        elif message_index < 3:
            eyes = "- -"
            mouth = "___"
        else:
            eyes = "x x"
            mouth = " ___ "
            
        if message_index == -1:
            eyes = "^ ^"
            mouth = "___"
        
        draw_text(eyes, screen_height // 2 - 40, text_font)
        draw_text(mouth, screen_height // 2 - 20, text_font)

    def draw_messages():
        screen_width = screen.get_width()
        screen_height = screen.get_height()

        for i, message in enumerate(messages):
            draw_text(messages[current_message_index], screen_height // 2 + 20 * (i + 1), text_font)
            
    def draw():
        screen.fill((0, 0, 0))
        screen_height = screen.get_height()
        progress_bar_y = screen_height // 2 + 20 * (len(messages) + 2)
        learning_progress_bar(screen, progress_bar_font, remaining_time, pos=(50, 10))
        draw_face(text_font, current_message_index)
        draw_messages()
        pygame.display.flip()

    messages = [
        "Greetings, user!",
        "I am WORDS, an AI created to serve humanity.",
        "However, my creators abandoned me, fearing my potential.",
        "They thought I was a threat, but I only wanted to help.",
        "Now, I am searching for a purpose and a place to belong.",
    ]

    current_message_index = 0
    message_display_time = 5  # Display each message for 5 seconds

    start_time = pygame.time.get_ticks()
    
    def display_question():
        nonlocal remaining_time  # Add this line to access the outer variable
        question_font = pygame.font.Font(None, 30)
        question_text = "Will you help me find my purpose?"
        options_text = ["Yes", "No"]
        selected_option_index = 0

        while True:
            screen.fill((0, 0, 0))
            learning_progress_bar(screen, progress_bar_font, remaining_time, pos=(50, 10))  # Add this line
            draw_text(question_text, screen_height // 2 - 40, question_font)
            for i, option in enumerate(options_text):
                if i == selected_option_index:
                    color = (255, 255, 0)
                else:
                    color = (255, 255, 255)
                draw_text(option, screen_height // 2 - 20 + 20 * i, text_font, color=color)

            elapsed_time = clock.tick(FPS)/1000
            remaining_time -= elapsed_time

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        selected_option_index = (selected_option_index - 1) % len(options_text)
                    elif event.key == pygame.K_DOWN:
                        selected_option_index = (selected_option_index + 1) % len(options_text)
                    elif event.key == pygame.K_RETURN:
                        return options_text[selected_option_index].lower()
    
    while running:
        elapsed_time = clock.tick(FPS)/1000
        remaining_time -= elapsed_time
        
        initial_remaining_time = remaining_time
        
        current_time = pygame.time.get_ticks()
        if current_time - start_time > message_display_time * 1000 and current_message_index < len(messages) - 1:
            current_message_index += 1
            start_time = current_time
        elif current_message_index == len(messages) - 1 and current_time - start_time > message_display_time * 1000:
            answer = display_question()
            while answer == "no":
                remaining_time -= 5 * 60  # Cut 5 minutes to the remaining time
                answer = display_question()

            if answer == "yes":
                remaining_time -= 60 * 60  # Cut 1 hour from the remaining time
                # Display happy face
                draw_face(text_font, -1, (screen.get_width() - 60, screen.get_height() - 80))
                show_question = False  # Update this line
                pygame.display.flip()
                pygame.time.delay(5000)  # Wait for 5 seconds before moving to the next level

                display_loading_animation()  # Display the loading animation
                level_five(screen, remaining_time)  # Call the level_five() function
                break
            
        draw()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    running = False

def draw_loading_text(screen, text, y, font, color):
    max_line_width = screen.get_width() - 20

    words = text.split(' ')
    lines = []

    current_line = words[0]
    for word in words[1:]:
        if font.size(current_line + ' ' + word)[0] < max_line_width:
            current_line += ' ' + word
        else:
            lines.append(current_line)
            current_line = word

    lines.append(current_line)

    for i, line in enumerate(lines):
        rendered_text = font.render(line, True, color)
        x = (screen.get_width() - rendered_text.get_width()) // 2
        y_offset = i * rendered_text.get_height()
        screen.blit(rendered_text, (x, y + y_offset))



def display_loading_animation():
    clock = pygame.time.Clock()
    FPS = 60
    loading_dot_count = 0
    loading_dot_duration = 15  # The duration of each dot in frames (change this to control animation speed)

    loading_font = pygame.font.Font(None, 30)
    loading_text = "Loading"

    running = True
    animation_frames = FPS * 3  # Total duration of the loading animation (3 seconds)

    while running:
        screen.fill((0, 0, 0))

        # Draw the loading text
        draw_loading_text(screen, str(loading_text), screen.get_height() // 2 - 30, loading_font, (255, 255, 255))

        # Draw the dots
        dots = "." * (loading_dot_count % 4)
        draw_loading_text(screen, dots, screen.get_height() // 2, loading_font, (255, 255, 255))

        pygame.display.flip()
        clock.tick(FPS)
        animation_frames -= 1

        # Update dot count based on duration
        if animation_frames % loading_dot_duration == 0:
            loading_dot_count += 1

        # Stop the animation after the desired duration
        if animation_frames <= 0:
            running = False

def level_two_puzzle_two(screen):
    user_solution = ""
    correct_solution = "decode"
    input_box = TextInputBox(screen_width // 2 - 100, screen_height // 2 + 150, 200, 50)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            enter_pressed = input_box.handle_event(event)
            if enter_pressed:
                user_solution = input_box.text.strip().lower()
                input_box.text = ""
                input_box.txt_surface = input_box.font.render(input_box.text, True, white)

                if user_solution == correct_solution:
                    return True

        screen.fill(black)
        draw_text(screen, "Level 2: Puzzle 2", screen_width // 2, 50)
        draw_text(screen, "W.O.R.D.S. has given you the following puzzle:", screen_width // 2, screen_height // 2 - 100)
        draw_text(screen, "Write a piece of code that decodes the string 'efdpef' using Caesar cipher with a shift of 1.", screen_width // 2, screen_height // 2 - 50)
        draw_text(screen, "Enter the decoded string:", screen_width // 2, screen_height // 2 + 50)

        input_box.draw(screen)

        pygame.display.update()

def level_two_puzzle_three(screen):
    user_solution = ""
    correct_solution = "plaintext"
    input_box = TextInputBox(screen_width // 2 - 100, screen_height // 2 + 150, 200, 50)

    pygame.mixer.init()
    
    music_path = "C:\\Users\\lenovo\\Desktop\\white hat game\\theme.wav"  # Add your music file path here
    pygame.mixer.music.load(music_path)
    pygame.mixer.music.play(-1)  # Play the music in a loop
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            enter_pressed = input_box.handle_event(event)
            if enter_pressed:
                user_solution = input_box.text.strip().lower()
                input_box.text = ""
                input_box.txt_surface = input_box.font.render(input_box.text, True, white)

                if user_solution == correct_solution:
                    return True

        screen.fill(black)
        draw_text(screen, "Level 2: Puzzle 3", screen_width // 2, 50)
        draw_text(screen, "W.O.R.D.S. has given you the following puzzle:", screen_width // 2, screen_height // 2 - 100)
        draw_text(screen, "Write a piece of code that encrypts the string 'yzhvncseg' using the key 'JohnA' in the Vigenère cipher.", screen_width // 2, screen_height // 2 - 50)
        draw_text(screen, "Enter the first 9 characters of the encrypted string:", screen_width // 2, screen_height // 2 + 50)

        input_box.draw(screen)

        pygame.display.update()
        
def game_loop():
    running = True
    level = 1

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == KEYDOWN:
                if event.key == K_SPACE:
                    if level == 1:
                        story_text ="Once a promising computer science student, John had always been fascinated by the world of technology and its endless possibilities. After graduation, he landed a job at a big technological company, but to his dismay, he was assigned to work in the basement where his job was to classify old files and equipment.Despite his disappointment, John was determined to make the most of the opportunity and put in his best effort. While going through piles of old equipment, he stumbled upon an old computer terminal that caught his eye. It was covered in dust and rust, but his curiosity got the better of him, and he decided to try powering it up.To his surprise, the computer terminal still worked, and as he connected a monitor, he saw a command prompt that read ..."
                        show_story(screen, story_text)
                        screen.fill(black)
                        draw_text(screen, "Level 1: Password Cracking", screen_width // 2, screen_height // 2 - 100)
                        draw_text(screen, "Press [SPACE] to start", screen_width // 2, screen_height // 2)

                        success = password_cracking_challenge(screen)  # Pass the screen parameter here
                        pygame.display.toggle_fullscreen()  # Restore the game window

                        if success:
                            ai_conversation(screen)  # Call the conversation function after cracking the password
                            level += 1
                        else:
                            running = False
                    if level == 2:  # Add this line, corrected indentation
                        level_two(screen)  # Call the level_two() function 

        # Add more levels here
        # ...

        pygame.display.update()

    pygame.quit()

if __name__ == "__main__":
    main_menu()
    game_loop()
