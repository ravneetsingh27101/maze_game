import pygame
import sys
import random

# Maze settings
WIDTH, HEIGHT = 21, 21  # Must be odd numbers for proper maze generation
CELL_SIZE = 20
SCREEN_WIDTH = WIDTH * CELL_SIZE
SCREEN_HEIGHT = HEIGHT * CELL_SIZE

# Colors
BACKGROUND_COLOR = (30, 30, 30)  # Dark background
WALL_COLOR = (50, 50, 50)  # Dark gray for walls
PATH_COLOR = (200, 200, 200)  # Light gray for paths
PLAYER_COLOR = (0, 128, 255)  # Blue for player
EXIT_COLOR = (255, 100, 100)  # Red for exit
TEXT_COLOR = (255, 255, 255)  # White for text
SHADOW_COLOR = (0, 0, 0)  # Black for shadow

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Maze Game")

# Fonts for messages
font_large = pygame.font.Font(None, 72)
font_small = pygame.font.Font(None, 28)


# Function to initialize the maze with walls ('#') and empty spaces (' ')
def initialize_maze(width, height):
    maze = [["#" for _ in range(width)] for _ in range(height)]
    maze[1][1] = " "
    return maze


# Function to generate a random maze using depth-first search
def generate_maze(maze, width, height):
    stack = [(1, 1)]
    directions = [(-2, 0), (2, 0), (0, -2), (0, 2)]

    while stack:
        x, y = stack[-1]
        random.shuffle(directions)
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 1 <= nx < height - 1 and 1 <= ny < width - 1 and maze[nx][ny] == "#":
                maze[x + dx // 2][y + dy // 2] = " "
                maze[nx][ny] = " "
                stack.append((nx, ny))
                break
        else:
            stack.pop()

    return maze


# Draw the maze with updated styles
def draw_maze(maze):
    for y, row in enumerate(maze):
        for x, cell in enumerate(row):
            color = PATH_COLOR if cell == " " else WALL_COLOR
            pygame.draw.rect(
                screen, color, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            )


# Draw the player with a slight glow
def draw_player(player_pos):
    pygame.draw.rect(
        screen,
        PLAYER_COLOR,
        (player_pos[1] * CELL_SIZE, player_pos[0] * CELL_SIZE, CELL_SIZE, CELL_SIZE),
        border_radius=6,
    )
    # Glow effect
    glow_rect = pygame.Rect(
        player_pos[1] * CELL_SIZE - 2,
        player_pos[0] * CELL_SIZE - 2,
        CELL_SIZE + 4,
        CELL_SIZE + 4,
    )
    pygame.draw.rect(screen, (0, 180, 255), glow_rect, 2, border_radius=8)


# Draw the exit with a glow effect
def draw_exit(exit_pos):
    pygame.draw.rect(
        screen,
        EXIT_COLOR,
        (exit_pos[1] * CELL_SIZE, exit_pos[0] * CELL_SIZE, CELL_SIZE, CELL_SIZE),
        border_radius=6,
    )
    # Glow effect
    glow_rect = pygame.Rect(
        exit_pos[1] * CELL_SIZE - 2,
        exit_pos[0] * CELL_SIZE - 2,
        CELL_SIZE + 4,
        CELL_SIZE + 4,
    )
    pygame.draw.rect(screen, (255, 150, 150), glow_rect, 2, border_radius=8)


# Display text with shadow effect in the center of the screen
def display_text_with_shadow(message, font, color, shadow_color, offset_y=0):
    text = font.render(message, True, color)
    shadow = font.render(message, True, shadow_color)

    text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + offset_y))
    shadow_rect = text_rect.copy()
    shadow_rect.move_ip(4, 4)  # Offset shadow slightly

    screen.blit(shadow, shadow_rect)
    screen.blit(text, text_rect)


# Display "You Win!" with background blur effect
def display_win_message():
    # Semi-transparent overlay for background blur effect
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.set_alpha(150)  # Set transparency
    overlay.fill((0, 0, 0))  # Black overlay

    screen.blit(overlay, (0, 0))
    display_text_with_shadow("You Win!", font_large, (0, 255, 0), SHADOW_COLOR)


# Initialize and generate the maze
maze = initialize_maze(WIDTH, HEIGHT)
maze = generate_maze(maze, WIDTH, HEIGHT)

# Set player starting position and exit position
player_pos = [1, 1]
exit_pos = [HEIGHT - 2, WIDTH - 2]
maze[exit_pos[0]][exit_pos[1]] = " "

# Movement delay and acceleration settings
initial_move_delay = 200  # Initial milliseconds between moves
min_move_delay = 50  # Minimum delay for max speed
acceleration_rate = 10  # Reduce delay by this amount each frame when key is held

# Variables to track movement timing and direction
move_delay = initial_move_delay
last_move_time = pygame.time.get_ticks()
movement_direction = None

# Main game loop
game_won = False
display_start_message = True

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if display_start_message and event.type == pygame.KEYDOWN:
            display_start_message = False

    if not game_won and not display_start_message:
        # Get the current time
        current_time = pygame.time.get_ticks()

        # Detect which key is being held and set the movement direction
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP] and maze[player_pos[0] - 1][player_pos[1]] == " ":
            movement_direction = "UP"
        elif keys[pygame.K_DOWN] and maze[player_pos[0] + 1][player_pos[1]] == " ":
            movement_direction = "DOWN"
        elif keys[pygame.K_LEFT] and maze[player_pos[0]][player_pos[1] - 1] == " ":
            movement_direction = "LEFT"
        elif keys[pygame.K_RIGHT] and maze[player_pos[0]][player_pos[1] + 1] == " ":
            movement_direction = "RIGHT"
        else:
            movement_direction = None
            move_delay = (
                initial_move_delay  # Reset move delay when no direction is held
            )

        # Move if enough time has passed and there's a direction to move in
        if movement_direction and current_time - last_move_time > move_delay:
            # Move the player based on the current direction
            if movement_direction == "UP":
                player_pos[0] -= 1
            elif movement_direction == "DOWN":
                player_pos[0] += 1
            elif movement_direction == "LEFT":
                player_pos[1] -= 1
            elif movement_direction == "RIGHT":
                player_pos[1] += 1

            # Update last move time and reduce delay for acceleration
            last_move_time = current_time
            move_delay = max(min_move_delay, move_delay - acceleration_rate)

        # Check if player has reached the exit
        if player_pos == exit_pos:
            game_won = True

    # Render the maze, player, and exit
    screen.fill(BACKGROUND_COLOR)
    draw_maze(maze)
    draw_exit(exit_pos)
    draw_player(player_pos)

    # Display start message or win message
    if display_start_message:
        display_text_with_shadow(
            "Press any key to start", font_small, TEXT_COLOR, SHADOW_COLOR, offset_y=-40
        )
        display_text_with_shadow(
            "Navigate to the red square to win",
            font_small,
            TEXT_COLOR,
            SHADOW_COLOR,
            offset_y=0,
        )
    elif game_won:
        display_win_message()
        pygame.display.flip()
        pygame.time.wait(2000)
        pygame.quit()
        sys.exit()

    pygame.display.flip()
