import pygame
import random

# Initialize Pygame
pygame.init()

# Image dimensions
BACKGROUND_WIDTH = 288
BACKGROUND_HEIGHT = 512
FLOOR_HEIGHT = 112

# Screen configuration
SCREEN_WIDTH = BACKGROUND_WIDTH
SCREEN_HEIGHT = BACKGROUND_HEIGHT + FLOOR_HEIGHT
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# Load images
background_img = pygame.image.load('assets/sprites/background.png').convert()
floor_img = pygame.image.load('assets/sprites/floor.png').convert()
pipe_img = pygame.image.load('assets/sprites/pipe-green.png').convert()
message_img = pygame.image.load('assets/sprites/message.png').convert_alpha()
gameover_img = pygame.image.load('assets/sprites/gameover.png').convert_alpha()
icon_img = pygame.image.load('assets/icons/red_bird.png').convert_alpha()
pygame.display.set_icon(icon_img)

# Load number images from 0 to 9
number_images = [pygame.image.load(f'assets/sprites/{i}.png').convert_alpha() for i in range(10)]

# Load bird frames
bird_frames = [
    pygame.image.load('assets/sprites/redbird-downflap.png').convert_alpha(),
    pygame.image.load('assets/sprites/redbird-midflap.png').convert_alpha(),
    pygame.image.load('assets/sprites/redbird-upflap.png').convert_alpha()
]

# Load sounds
wing_sound = pygame.mixer.Sound('assets/audios/wing.wav')
point_sound = pygame.mixer.Sound('assets/audios/point.wav')
hit_sound = pygame.mixer.Sound('assets/audios/hit.wav')

# Clock configuration
clock = pygame.time.Clock()

# Screen update speed
FPS = 60

# Fixed distance between pipes
PIPE_GAP = 150

class Bird(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.frames = bird_frames  # Load bird frames for animation
        self.frame_index = 0  # Start with the first frame
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect(center=(100, BACKGROUND_HEIGHT // 2))
        self.gravity = 0  # Initialize gravity

    def update(self):
        self.gravity += 0.5  # Increment gravity
        self.rect.y += self.gravity  # Apply gravity to bird's position

        # If the bird hits the ground, remove it from the game
        if self.rect.bottom >= BACKGROUND_HEIGHT:
            self.kill()

        # Bird animation logic
        self.frame_index += 0.1
        if self.frame_index >= len(self.frames):
            self.frame_index = 0
        self.image = self.frames[int(self.frame_index)]

    def flap(self):
        self.gravity = -10  # Make the bird jump
        wing_sound.play()  # Play wing sound

class Pipe(pygame.sprite.Sprite):
    def __init__(self, x, y, is_top=False, speed=5):
        super().__init__()
        self.image = pipe_img  # Load pipe image
        if is_top:
            self.image = pygame.transform.flip(self.image, False, True)  # Flip the image if it's the top pipe
            self.rect = self.image.get_rect(midbottom=(x, y))
        else:
            self.rect = self.image.get_rect(midtop=(x, y))
        self.speed = speed  # Set pipe speed
        self.passed = False  # Track if the bird has passed this pipe

    def update(self):
        self.rect.x -= self.speed  # Move the pipe left
        # Remove the pipe if it goes off the screen
        if self.rect.right < 0:
            self.kill()

def reset_game():
    bird = Bird()  # Create a new bird
    all_sprites = pygame.sprite.Group()  # Create a new sprite group for all sprites
    pipes = pygame.sprite.Group()  # Create a new sprite group for pipes
    all_sprites.add(bird)  # Add the bird to all sprites group
    return bird, all_sprites, pipes  # Return the bird and sprite groups

def draw_score(score, screen):
    score_str = str(score)
    total_width = sum(number_images[int(digit)].get_width() for digit in score_str)
    x_offset = (SCREEN_WIDTH - total_width) // 2  # Center the score

    # Draw each digit of the score
    for digit in score_str:
        screen.blit(number_images[int(digit)], (x_offset, 50))  # Adjust height as needed
        x_offset += number_images[int(digit)].get_width()

def main():
    pygame.display.set_caption("Flappy Bird")  # Set the window title

    bird, all_sprites, pipes = reset_game()  # Reset the game

    SPAWNPIPE = pygame.USEREVENT
    pygame.time.set_timer(SPAWNPIPE, 1200)  # Set timer for pipe spawn

    running = True
    game_active = False
    game_over = False
    score = 0
    pipe_speed = 5

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False  # Exit the game loop
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if game_over:
                        # Reset the game after game over
                        game_over = False
                        game_active = True
                        bird, all_sprites, pipes = reset_game()
                        score = 0
                        pipe_speed = 5  # Reset pipe speed
                    elif not game_active:
                        # Start the game if it's not active
                        game_active = True
                        bird, all_sprites, pipes = reset_game()
                        score = 0
                        pipe_speed = 5  # Reset pipe speed
                    else:
                        bird.flap()  # Make the bird flap
            if event.type == SPAWNPIPE and game_active:
                # Spawn new pipes
                pipe_height = random.randint(100, BACKGROUND_HEIGHT - PIPE_GAP - 100)
                top_pipe = Pipe(SCREEN_WIDTH, pipe_height, is_top=True, speed=pipe_speed)
                bottom_pipe = Pipe(SCREEN_WIDTH, pipe_height + PIPE_GAP, is_top=False, speed=pipe_speed)
                all_sprites.add(top_pipe)
                all_sprites.add(bottom_pipe)
                pipes.add(top_pipe)
                pipes.add(bottom_pipe)

        if game_active:
            all_sprites.update()  # Update all sprites

            # Check for collisions
            if pygame.sprite.spritecollideany(bird, pipes) or bird.rect.bottom >= BACKGROUND_HEIGHT:
                hit_sound.play()  # Play hit sound
                game_active = False
                game_over = True

            for pipe in pipes:
                if not pipe.passed and pipe.rect.right < bird.rect.left:
                    pipe.passed = True
                    score += 1
                    point_sound.play()  # Play point sound

            # Increase pipe speed based on score
            pipe_speed = 5 + (score // 2) * 0.1

            # Draw background and sprites
            SCREEN.blit(background_img, (0, 0))
            all_sprites.draw(SCREEN)
            SCREEN.blit(floor_img, (0, BACKGROUND_HEIGHT))

            # Draw score
            draw_score(score // 2, SCREEN)

        else:
            # Draw background and floor
            SCREEN.blit(background_img, (0, 0))
            SCREEN.blit(floor_img, (0, BACKGROUND_HEIGHT))
            
            if game_over:
                # Show game over screen
                gameover_rect = gameover_img.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
                SCREEN.blit(gameover_img, gameover_rect)
                draw_score(score // 2, SCREEN)
            else:
                # Show start screen
                message_rect = message_img.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
                SCREEN.blit(message_img, message_rect)

        pygame.display.update()  # Update the display
        clock.tick(FPS)  # Control the frame rate

    pygame.quit()  # Quit Pygame

if __name__ == "__main__":
    main()  # Run the main function
