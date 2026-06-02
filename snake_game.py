#cmd
#pip install pygame

import pygame
import random
import sys

WINDOW_WIDTH = 640
WINDOW_HEIGHT = 480
CELL_SIZE = 20
FRAME_RATE = 12
FOOD_COUNT = 5

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 200, 0)
BLUE = (0, 0, 200)
RED = (200, 0, 0)
YELLOW = (240, 200, 0)

DIRECTIONS = {
    pygame.K_UP: (0, -1),
    pygame.K_DOWN: (0, 1),
    pygame.K_LEFT: (-1, 0),
    pygame.K_RIGHT: (1, 0),
}

class Snake:
    def __init__(self, body, direction, color, name):
        self.body = body
        self.direction = direction
        self.color = color
        self.name = name
        self.score = 0
        self.alive = True

    @property
    def head(self):
        return self.body[0]

    def change_direction(self, key):
        if key not in DIRECTIONS:
            return
        new_dir = DIRECTIONS[key]
        current_dir = DIRECTIONS[self.direction]
        if (new_dir[0] == -current_dir[0] and new_dir[1] == -current_dir[1]):
            return
        self.direction = key

    def next_head(self):
        dx, dy = DIRECTIONS[self.direction]
        grid_width = WINDOW_WIDTH // CELL_SIZE
        grid_height = WINDOW_HEIGHT // CELL_SIZE
        return ((self.head[0] + dx) % grid_width, (self.head[1] + dy) % grid_height)

    def move(self, grow=False):
        self.body.insert(0, self.next_head())
        if not grow:
            self.body.pop()

    def collides_with(self, position, include_head=True):
        if include_head:
            return position in self.body
        return position in self.body[1:]

    def kill(self):
        self.alive = False

class SnakeGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Snake vs AI")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 28)
        self.reset()

    def reset(self):
        self.player = Snake([(5, 5), (4, 5), (3, 5)], pygame.K_RIGHT, GREEN, "Player")
        self.enemy = Snake([(15, 10), (16, 10), (17, 10)], pygame.K_LEFT, BLUE, "AI")
        self.foods = []
        self.spawn_foods()
        self.game_over = False
        self.winner = None

    def spawn_food(self):
        grid_width = WINDOW_WIDTH // CELL_SIZE
        grid_height = WINDOW_HEIGHT // CELL_SIZE
        while True:
            pos = (random.randint(0, grid_width - 1), random.randint(0, grid_height - 1))
            if pos not in self.player.body and pos not in self.enemy.body and pos not in self.foods:
                self.foods.append(pos)
                return

    def spawn_foods(self):
        while len(self.foods) < FOOD_COUNT:
            self.spawn_food()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and self.game_over:
                    self.reset()
                else:
                    self.player.change_direction(event.key)

        self.handle_keyboard_hold()

    def handle_keyboard_hold(self):
        if self.game_over:
            return
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            self.player.change_direction(pygame.K_UP)
        elif keys[pygame.K_DOWN]:
            self.player.change_direction(pygame.K_DOWN)
        elif keys[pygame.K_LEFT]:
            self.player.change_direction(pygame.K_LEFT)
        elif keys[pygame.K_RIGHT]:
            self.player.change_direction(pygame.K_RIGHT)

    def update(self):
        if self.game_over:
            return

        self.update_ai_direction()

        player_next = self.player.next_head() if self.player.alive else None
        enemy_next = self.enemy.next_head() if self.enemy.alive else None

        if self.player.alive:
            self.player.alive = not self.is_collision(player_next, self.player)
        if self.enemy.alive:
            self.enemy.alive = not self.is_collision(enemy_next, self.enemy)

        if self.player.alive and self.enemy.alive and player_next == enemy_next:
            self.player.kill()
            self.enemy.kill()

        if self.player.alive:
            grow = player_next in self.foods
            self.player.move(grow=grow)
            if grow:
                self.player.score += 10
                self.foods.remove(player_next)
                self.spawn_food()
        if self.enemy.alive:
            grow = enemy_next in self.foods
            self.enemy.move(grow=grow)
            if grow:
                self.enemy.score += 10
                if enemy_next in self.foods:
                    self.foods.remove(enemy_next)
                self.spawn_food()

        if self.player.alive and self.enemy.alive and self.player.head == self.enemy.head:
            self.player.kill()
            self.enemy.kill()

        self.check_game_over()

    def update_ai_direction(self):
        if not self.enemy.alive:
            return

        next_dir = self.choose_ai_direction()
        if next_dir:
            self.enemy.direction = next_dir

    def choose_ai_direction(self):
        best_dir = None
        best_distance = float('inf')
        if not self.foods:
            return self.enemy.direction
        for key, delta in DIRECTIONS.items():
            if self.is_reverse_direction(self.enemy.direction, key):
                continue
            next_pos = (self.enemy.head[0] + delta[0], self.enemy.head[1] + delta[1])
            if self.is_collision(next_pos, self.enemy):
                continue
            distance = min(abs(next_pos[0] - food[0]) + abs(next_pos[1] - food[1]) for food in self.foods)
            if distance < best_distance:
                best_distance = distance
                best_dir = key

        if best_dir is None:
            for key, delta in DIRECTIONS.items():
                if self.is_reverse_direction(self.enemy.direction, key):
                    continue
                next_pos = (self.enemy.head[0] + delta[0], self.enemy.head[1] + delta[1])
                if not self.is_collision(next_pos, self.enemy):
                    return key
        return best_dir or self.enemy.direction

    def is_reverse_direction(self, current, new):
        if current not in DIRECTIONS or new not in DIRECTIONS:
            return False
        cur = DIRECTIONS[current]
        nxt = DIRECTIONS[new]
        return cur[0] == -nxt[0] and cur[1] == -nxt[1]

    def is_collision(self, position, snake):
        if position is None:
            return True
        if position in snake.body[:-1]:
            return True
        other = self.enemy if snake is self.player else self.player
        if position in other.body:
            return True
        return False

    def check_game_over(self):
        if not self.player.alive or not self.enemy.alive:
            self.game_over = True
            if self.player.alive and not self.enemy.alive:
                self.winner = self.player.name
            elif self.enemy.alive and not self.player.alive:
                self.winner = self.enemy.name
            elif not self.player.alive and not self.enemy.alive:
                self.winner = "Tie"

    def draw_grid(self):
        for x in range(0, WINDOW_WIDTH, CELL_SIZE):
            pygame.draw.line(self.screen, BLACK, (x, 0), (x, WINDOW_HEIGHT), 1)
        for y in range(0, WINDOW_HEIGHT, CELL_SIZE):
            pygame.draw.line(self.screen, BLACK, (0, y), (WINDOW_WIDTH, y), 1)

    def draw_snake(self, snake):
        for i, segment in enumerate(snake.body):
            x, y = segment
            rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            color = YELLOW if i == 0 else snake.color
            pygame.draw.rect(self.screen, color, rect)
            pygame.draw.rect(self.screen, BLACK, rect, 1)

    def draw(self):
        self.screen.fill(WHITE)
        self.draw_grid()
        self.draw_snake(self.player)
        self.draw_snake(self.enemy)
        for food in self.foods:
            food_rect = pygame.Rect(food[0] * CELL_SIZE, food[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(self.screen, RED, food_rect)
            pygame.draw.rect(self.screen, BLACK, food_rect, 1)

        player_text = self.font.render(f"Player: {self.player.score}", True, GREEN)
        enemy_text = self.font.render(f"AI: {self.enemy.score}", True, BLUE)
        self.screen.blit(player_text, (10, 10))
        self.screen.blit(enemy_text, (10, 40))

        if self.game_over:
            self.show_game_over()

        pygame.display.flip()

    def show_game_over(self):
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        result = "Draw!" if self.winner == "Tie" else f"Winner: {self.winner}"
        text1 = self.font.render(result, True, WHITE)
        text2 = self.font.render("Press R to restart", True, WHITE)
        self.screen.blit(text1, (WINDOW_WIDTH // 2 - text1.get_width() // 2, WINDOW_HEIGHT // 2 - 30))
        self.screen.blit(text2, (WINDOW_WIDTH // 2 - text2.get_width() // 2, WINDOW_HEIGHT // 2 + 10))

    def run(self):
        while True:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FRAME_RATE)


if __name__ == "__main__":
    SnakeGame().run()
