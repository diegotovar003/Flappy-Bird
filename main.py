import pygame
import random

# Inicialización de Pygame
pygame.init()

# Dimensiones de las imágenes
BACKGROUND_WIDTH = 288
BACKGROUND_HEIGHT = 512
FLOOR_HEIGHT = 112

# Configuración de la pantalla
SCREEN_WIDTH = BACKGROUND_WIDTH
SCREEN_HEIGHT = BACKGROUND_HEIGHT + FLOOR_HEIGHT
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# Cargar imágenes
background_img = pygame.image.load('C:\\Users\\David Tovar\\Documents\\VS CODE DEVELOPER\\FlappyBird\\assets\\sprites\\background.png').convert()
floor_img = pygame.image.load('C:\\Users\\David Tovar\\Documents\\VS CODE DEVELOPER\\FlappyBird\\assets\\sprites\\floor.png').convert()
pipe_img = pygame.image.load('C:\\Users\\David Tovar\\Documents\\VS CODE DEVELOPER\\FlappyBird\\assets\\sprites\\pipe-green.png').convert()
message_img = pygame.image.load('C:\\Users\\David Tovar\\Documents\\VS CODE DEVELOPER\\FlappyBird\\assets\\sprites\\message.png').convert_alpha()
gameover_img = pygame.image.load('C:\\Users\\David Tovar\\Documents\\VS CODE DEVELOPER\\FlappyBird\\assets\\sprites\\gameover.png').convert_alpha()

# Cargar el ícono de la aplicación
icon_img = pygame.image.load('C:\\Users\\David Tovar\\Documents\\VS CODE DEVELOPER\\FlappyBird\\assets\\icons\\red_bird.png').convert_alpha()
pygame.display.set_icon(icon_img)

# Cargar imágenes de números del 0 al 9
number_images = [pygame.image.load(f'C:\\Users\\David Tovar\\Documents\\VS CODE DEVELOPER\\FlappyBird\\assets\\sprites\\{i}.png').convert_alpha() for i in range(10)]

# Cargar imágenes del pájaro
bird_frames = [
    pygame.image.load('C:\\Users\\David Tovar\\Documents\\VS CODE DEVELOPER\\FlappyBird\\assets\\sprites\\redbird-downflap.png').convert_alpha(),
    pygame.image.load('C:\\Users\\David Tovar\\Documents\\VS CODE DEVELOPER\\FlappyBird\\assets\\sprites\\redbird-midflap.png').convert_alpha(),
    pygame.image.load('C:\\Users\\David Tovar\\Documents\\VS CODE DEVELOPER\\FlappyBird\\assets\\sprites\\redbird-upflap.png').convert_alpha()
]

# Cargar sonidos
wing_sound = pygame.mixer.Sound('C:\\Users\\David Tovar\\Documents\\VS CODE DEVELOPER\\FlappyBird\\assets\\audios\\wing.wav')
point_sound = pygame.mixer.Sound('C:\\Users\\David Tovar\\Documents\\VS CODE DEVELOPER\\FlappyBird\\assets\\audios\\point.wav')
hit_sound = pygame.mixer.Sound('C:\\Users\\David Tovar\\Documents\\VS CODE DEVELOPER\\FlappyBird\\assets\\audios\\hit.wav')

# Colores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)

# Configuración de reloj
clock = pygame.time.Clock()

# Velocidad de actualización de la pantalla
FPS = 60

# Mejor resultado
best_score = 0

# Distancia fija entre los tubos
PIPE_GAP = 150

class Bird(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.frames = bird_frames
        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect(center=(100, BACKGROUND_HEIGHT // 2))
        self.gravity = 0

    def update(self):
        self.gravity += 0.5
        self.rect.y += self.gravity

        if self.rect.bottom >= BACKGROUND_HEIGHT:
            self.kill()

        # Animación del pájaro
        self.frame_index += 0.1
        if self.frame_index >= len(self.frames):
            self.frame_index = 0
        self.image = self.frames[int(self.frame_index)]

    def flap(self):
        self.gravity = -10
        wing_sound.play()  # Reproducir el sonido de las alas

class Pipe(pygame.sprite.Sprite):
    def __init__(self, x, y, is_top=False, speed=5):
        super().__init__()
        self.image = pipe_img
        if is_top:
            self.image = pygame.transform.flip(self.image, False, True)  # Voltear la imagen si es el tubo superior
            self.rect = self.image.get_rect(midbottom=(x, y))
        else:
            self.rect = self.image.get_rect(midtop=(x, y))
        self.speed = speed
        self.passed = False

    def update(self):
        self.rect.x -= self.speed
        if self.rect.right < 0:
            self.kill()

def reset_game():
    bird = Bird()
    all_sprites = pygame.sprite.Group()
    pipes = pygame.sprite.Group()
    all_sprites.add(bird)
    return bird, all_sprites, pipes

def draw_score(score, screen):
    score_str = str(score)
    total_width = sum(number_images[int(digit)].get_width() for digit in score_str)
    x_offset = (SCREEN_WIDTH - total_width) // 2

    for digit in score_str:
        screen.blit(number_images[int(digit)], (x_offset, 50))  # Ajustar la altura según sea necesario
        x_offset += number_images[int(digit)].get_width()

def main():
    global best_score

    pygame.display.set_caption("Flappy Bird")

    bird, all_sprites, pipes = reset_game()

    SPAWNPIPE = pygame.USEREVENT
    pygame.time.set_timer(SPAWNPIPE, 1200)  # Reducir el tiempo entre la aparición de tubos

    running = True
    game_active = False
    game_over = False
    score = 0
    pipe_speed = 5

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if game_over:
                        game_over = False
                        game_active = True
                        bird, all_sprites, pipes = reset_game()
                        score = 0
                        pipe_speed = 5  # Resetear la velocidad del tubo
                    elif not game_active:
                        game_active = True
                        bird, all_sprites, pipes = reset_game()
                        score = 0
                        pipe_speed = 5  # Resetear la velocidad del tubo
                    else:
                        bird.flap()
            if event.type == SPAWNPIPE and game_active:
                pipe_height = random.randint(100, BACKGROUND_HEIGHT - PIPE_GAP - 100)
                top_pipe = Pipe(SCREEN_WIDTH, pipe_height, is_top=True, speed=pipe_speed)
                bottom_pipe = Pipe(SCREEN_WIDTH, pipe_height + PIPE_GAP, is_top=False, speed=pipe_speed)
                all_sprites.add(top_pipe)
                all_sprites.add(bottom_pipe)
                pipes.add(top_pipe)
                pipes.add(bottom_pipe)

        if game_active:
            all_sprites.update()

            if pygame.sprite.spritecollideany(bird, pipes) or bird.rect.bottom >= BACKGROUND_HEIGHT:
                hit_sound.play()  # Reproducir el sonido de choque
                game_active = False
                game_over = True
                best_score = max(best_score, score // 2)

            for pipe in pipes:
                if not pipe.passed and pipe.rect.right < bird.rect.left:
                    pipe.passed = True
                    score += 1
                    point_sound.play()  # Reproducir el sonido de punto

            # Incrementar la velocidad del tubo basado en el puntaje
            pipe_speed = 5 + (score // 2) * 0.1

            SCREEN.blit(background_img, (0, 0))
            all_sprites.draw(SCREEN)
            SCREEN.blit(floor_img, (0, BACKGROUND_HEIGHT))

            draw_score(score // 2, SCREEN)

        else:
            SCREEN.blit(background_img, (0, 0))
            SCREEN.blit(floor_img, (0, BACKGROUND_HEIGHT))
            
            if game_over:
                gameover_rect = gameover_img.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
                SCREEN.blit(gameover_img, gameover_rect)
                draw_score(score // 2, SCREEN)
            else:
                message_rect = message_img.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
                SCREEN.blit(message_img, message_rect)

        pygame.display.update()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
