import pygame
import random
import requests
from io import BytesIO

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 500, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bird Jumper")

# Game variables
FPS = 60
GRAVITY = 0.5
JUMP_STRENGTH = -19
BOOST_JUMP_STRENGTH = -36
PLAYER_WIDTH, PLAYER_HEIGHT = 40, 40 
PLATFORM_WIDTH, PLATFORM_HEIGHT = 80, 10
PLATFORM_SPEED = 4
VERTICAL_SPACING = 60
HORIZONTAL_PADDING = 20

# Fonts
font = pygame.font.Font(None, 36)

# Load an image from a URL
def load_image_from_url(url, size=None):
    """Fetch and load an image from a URL into a Pygame surface."""
    response = requests.get(url)
    response.raise_for_status()  # Ensure the request succeeded
    image = pygame.image.load(BytesIO(response.content))
    if size:
        image = pygame.transform.scale(image, size)
    return image

# Load images
background_image = load_image_from_url(
    "https://i.postimg.cc/4x1zFtvb/game-background.png", (WIDTH, HEIGHT)
)
platform_image = load_image_from_url(
    "https://i.postimg.cc/C10pM3nV/Screenshot-2024-11-24-120817.png", 
    (PLATFORM_WIDTH, PLATFORM_HEIGHT)
)
player_image = load_image_from_url(
    "https://i.postimg.cc/QMGd5nKf/Screenshot-2024-11-24-121159.png", 
    (PLAYER_WIDTH, PLAYER_HEIGHT)
)

# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self, start_platform):
        super().__init__()
        self.image = player_image
        self.rect = self.image.get_rect()
        self.rect.midbottom = start_platform.rect.midtop
        self.velocity_y = 0
        self.score = 0

    def update(self):
        self.velocity_y += GRAVITY
        self.rect.y += self.velocity_y

        # Horizontal movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.x -= 5
        if keys[pygame.K_RIGHT]:
            self.rect.x += 5

        # Screen wrap
        if self.rect.right > WIDTH:
            self.rect.left = 0
        if self.rect.left < 0:
            self.rect.right = WIDTH

# Platform class
class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, temporary=False, boost=False):
        super().__init__()
        self.image = platform_image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.temporary = temporary
        self.boost = boost
        self.direction = 1

    def update(self):
        global PLATFORM_SPEED
        self.rect.x += self.direction * PLATFORM_SPEED
        if self.rect.right >= WIDTH or self.rect.left <= 0:
            self.direction *= -1

# Main game function
def main():
    clock = pygame.time.Clock()
    running = True

    # Groups
    all_sprites = pygame.sprite.Group()
    platforms = pygame.sprite.Group()

    # Initial platform
    initial_platform = Platform(WIDTH // 2 - PLATFORM_WIDTH // 2, HEIGHT - 150)
    all_sprites.add(initial_platform)
    platforms.add(initial_platform)

    # Player
    player = Player(initial_platform)
    all_sprites.add(player)

    def generate_platforms(last_y):
        """Generate a new platform at a fixed vertical distance from the last one."""
        x = random.randint(HORIZONTAL_PADDING, WIDTH - PLATFORM_WIDTH - HORIZONTAL_PADDING)
        y = last_y - VERTICAL_SPACING
        return Platform(x, y)

    # Generate initial platforms
    last_platform_y = HEIGHT - 120
    for _ in range(10):
        platform = generate_platforms(last_platform_y)
        last_platform_y = platform.rect.y
        all_sprites.add(platform)
        platforms.add(platform)

    while running:
        clock.tick(FPS)
        screen.blit(background_image, (0, 0))  # Draw background

        # Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Update
        all_sprites.update()

        # Increase platform speed based on score
        global PLATFORM_SPEED
        if player.score > 10:
            PLATFORM_SPEED = 5
        if player.score > 20:
            PLATFORM_SPEED = 6

        # Check for collision with platforms
        if player.velocity_y > 0:
            platform_hit = pygame.sprite.spritecollide(player, platforms, False)
            if platform_hit:
                platform = platform_hit[0]
                if platform.boost:
                    player.velocity_y = BOOST_JUMP_STRENGTH
                else:
                    player.velocity_y = JUMP_STRENGTH
                if platform.temporary:
                    platform.kill()

        # Scroll screen upwards when player is high
        if player.rect.top < HEIGHT // 4:
            scroll = abs(player.velocity_y)
            player.rect.y += scroll
            for platform in platforms:
                platform.rect.y += scroll
                if platform.rect.top > HEIGHT:
                    platform.kill()
                    new_platform = generate_platforms(last_platform_y)
                    last_platform_y = new_platform.rect.y
                    all_sprites.add(new_platform)
                    platforms.add(new_platform)
                    player.score += 1

        # Check if player falls
        if player.rect.top > HEIGHT:
            running = False

        # Draw everything
        all_sprites.draw(screen)

        # Display score
        score_text = font.render(f"Score: {player.score}", True, (0, 0, 0))
        screen.blit(score_text, (10, 10))

        pygame.display.flip()

    pygame.quit()

# Run the game
if __name__ == "__main__":
    main()
