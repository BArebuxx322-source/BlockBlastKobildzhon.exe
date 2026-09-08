import pygame
import random
import sys
import os

# Инициализация
pygame.init()
pygame.mixer.init()

# Константы
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 1000
CELL_SIZE = 44
GRID_COLS = 8
GRID_ROWS = 8
SIDEBAR_WIDTH = 220
BOARD_OFFSET_X = 40
BOARD_OFFSET_Y = 120
BOARD_WIDTH = GRID_COLS * CELL_SIZE
BOARD_HEIGHT = GRID_ROWS * CELL_SIZE

# Цвета
BG_COLOR = (18, 18, 28)
BG_COLOR2 = (30, 30, 45)
GRID_BG = (40, 40, 58)
GRID_LINE = (60, 60, 82)
SIDEBAR_BG = (25, 25, 38)
TEXT_COLOR = (240, 240, 255)
HIGHLIGHT_COLOR = (255, 220, 80)
ACCENT_COLOR = (120, 180, 255)
DANGER_COLOR = (255, 80, 80)

# Шрифты
font_main = pygame.font.Font(None, 56)
font_small = pygame.font.Font(None, 30)
font_score = pygame.font.Font(None, 40)
font_title = pygame.font.Font(None, 24)

# Путь к изображениям
IMAGE_DIR = "kobildzhon_images"

# Фигуры (каждая фигура — список координат клеток)
SHAPES = [
    # 1x1
    [(0, 0)],
    # 1x2
    [(0, 0), (0, 1)],
    # 2x1
    [(0, 0), (1, 0)],
    # 2x2
    [(0, 0), (0, 1), (1, 0), (1, 1)],
    # 1x3
    [(0, 0), (0, 1), (0, 2)],
    # 3x1
    [(0, 0), (1, 0), (2, 0)],
    # L-образная (4 клетки)
    [(0, 0), (0, 1), (1, 1), (2, 1)],
    [(0, 0), (1, 0), (1, 1), (1, 2)],
    [(0, 1), (1, 1), (2, 1), (2, 0)],
    [(0, 0), (1, 0), (2, 0), (2, 1)],
    # T-образная
    [(0, 0), (0, 1), (0, 2), (1, 1)],
    [(0, 0), (1, 0), (2, 0), (1, 1)],
    [(0, 1), (1, 0), (1, 1), (1, 2)],
    [(0, 0), (1, 0), (2, 0), (1, -1)],
    # S-образная
    [(0, 0), (0, 1), (1, 1), (1, 2)],
    [(0, 1), (1, 0), (1, 1), (2, 0)],
    # Z-образная
    [(0, 1), (0, 2), (1, 0), (1, 1)],
    [(0, 0), (1, 0), (1, 1), (2, 1)],
    # 2x3
    [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2)],
    # 3x2
    [(0, 0), (0, 1), (1, 0), (1, 1), (2, 0), (2, 1)],
    # 4x1
    [(0, 0), (1, 0), (2, 0), (3, 0)],
    # 1x4
    [(0, 0), (0, 1), (0, 2), (0, 3)],
]

class KobildzhonBlock:
    """Класс блока с изображением Кобильджона (или заглушки)"""
    def __init__(self, image_path=None):
        self.image = None
        self.load_image(image_path)

    def load_image(self, image_path):
        try:
            if image_path and os.path.exists(image_path):
                self.image = pygame.image.load(image_path).convert_alpha()
                base_size = CELL_SIZE - 4
                self.image = pygame.transform.smoothscale(self.image, (base_size, base_size))
                mask = pygame.Surface((base_size, base_size), pygame.SRCALPHA)
                pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, base_size, base_size), border_radius=12)
                self.image = self.image.copy()
                self.image.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
            else:
                self.image = pygame.Surface((CELL_SIZE - 4, CELL_SIZE - 4), pygame.SRCALPHA)
                for i in range(CELL_SIZE - 4):
                    color = (150 + i, 80, 80)
                    pygame.draw.line(self.image, color, (0, i), (CELL_SIZE - 4, i))
                pygame.draw.rect(self.image, (200, 60, 60), (0, 0, CELL_SIZE - 4, CELL_SIZE - 4), border_radius=12)
                font = pygame.font.Font(None, 18)
                text = font.render("K", True, (255, 255, 255))
                text_rect = text.get_rect(center=(CELL_SIZE // 2, CELL_SIZE // 2))
                self.image.blit(text, text_rect)
        except Exception as e:
            print(f"Ошибка загрузки изображения: {e}")
            self.image = None

    def draw(self, screen, x, y):
        if self.image:
            screen.blit(self.image, (x + 2, y + 2))

class BlockBlastKobildzhon:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Block Blast: Kobildzhon Edition")
        self.clock = pygame.time.Clock()
        self.running = True
        
        self.grid = [[None for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]
        self.score = 0
        self.current_shapes = []
        self.selected_shape_index = None
        self.dragging = False
        self.drag_offset = (0, 0)
        self.hover_cell = None
        self.is_valid_placement = False
        self.game_over = False
        
        self.images = {}
        self.load_images()
        self.spawn_shapes()

    def load_images(self):
        """Загрузка всех изображений с правильным путём"""
        if getattr(sys, 'frozen', False):
            base_path = os.path.dirname(sys.executable)
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))
        
        image_dir = os.path.join(base_path, "kobildzhon_images")
        
        if not os.path.exists(image_dir):
            os.makedirs(image_dir)
            print(f"Создана папка {image_dir}. Положите туда изображения.")
        
        available_images = []
        for filename in os.listdir(image_dir):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
                filepath = os.path.join(image_dir, filename)
                try:
                    test_img = pygame.image.load(filepath)
                    available_images.append(filepath)
                except:
                    print(f"Не удалось загрузить файл: {filename}")
        
        if not available_images:
            print(f"Нет изображений в {image_dir}. Использую заглушки.")
            available_images = [None]
        
        num_images = min(8, len(available_images))
        for i in range(num_images):
            self.images[i] = KobildzhonBlock(available_images[i % len(available_images)])

    def spawn_shapes(self):
        self.current_shapes = []
        for _ in range(3):
            shape = random.choice(SHAPES)
            block_id = random.choice(list(self.images.keys())) if self.images else 0
            self.current_shapes.append({
                'cells': shape,
                'block_id': block_id
            })

    def draw_background(self):
        for y in range(SCREEN_HEIGHT):
            ratio = y / SCREEN_HEIGHT
            r = int(BG_COLOR[0] * (1 - ratio) + BG_COLOR2[0] * ratio)
            g = int(BG_COLOR[1] * (1 - ratio) + BG_COLOR2[1] * ratio)
            b = int(BG_COLOR[2] * (1 - ratio) + BG_COLOR2[2] * ratio)
            pygame.draw.line(self.screen, (r, g, b), (0, y), (SCREEN_WIDTH, y))

    def draw_grid(self):
        pygame.draw.rect(self.screen, GRID_BG, 
                        (BOARD_OFFSET_X - 8, BOARD_OFFSET_Y - 8, 
                         BOARD_WIDTH + 16, BOARD_HEIGHT + 16),
                        border_radius=16)
        
        for row in range(GRID_ROWS):
            for col in range(GRID_COLS):
                x = BOARD_OFFSET_X + col * CELL_SIZE
                y = BOARD_OFFSET_Y + row * CELL_SIZE
                pygame.draw.rect(self.screen, GRID_BG, (x, y, CELL_SIZE, CELL_SIZE), border_radius=8)
        
        for row in range(GRID_ROWS + 1):
            y = BOARD_OFFSET_Y + row * CELL_SIZE
            pygame.draw.line(self.screen, GRID_LINE, (BOARD_OFFSET_X, y), (BOARD_OFFSET_X + BOARD_WIDTH, y), 1)
        for col in range(GRID_COLS + 1):
            x = BOARD_OFFSET_X + col * CELL_SIZE
            pygame.draw.line(self.screen, GRID_LINE, (x, BOARD_OFFSET_Y), (x, BOARD_OFFSET_Y + BOARD_HEIGHT), 1)
        
        for row in range(GRID_ROWS):
            for col in range(GRID_COLS):
                if self.grid[row][col] is not None:
                    block = self.grid[row][col]
                    block.draw(self.screen, BOARD_OFFSET_X + col * CELL_SIZE, BOARD_OFFSET_Y + row * CELL_SIZE)

    def draw_shapes(self):
        panel_x = BOARD_OFFSET_X + BOARD_WIDTH + 20
        panel_width = SIDEBAR_WIDTH - 30
        panel_y = 20
        panel_height = SCREEN_HEIGHT - 40
        
        pygame.draw.rect(self.screen, SIDEBAR_BG, (panel_x, panel_y, panel_width, panel_height), border_radius=16)
        
        title_text = font_title.render("ФИГУРЫ", True, ACCENT_COLOR)
        title_rect = title_text.get_rect(center=(panel_x + panel_width // 2, panel_y + 30))
        self.screen.blit(title_text, title_rect)
        
        score_text = font_score.render(f"Счёт: {self.score}", True, TEXT_COLOR)
        score_rect = score_text.get_rect(center=(panel_x + panel_width // 2, panel_y + 70))
        self.screen.blit(score_text, score_rect)
        
        shape_start_y = panel_y + 130
        for i, shape_data in enumerate(self.current_shapes):
            cells = shape_data['cells']
            block_id = shape_data['block_id']
            
            min_x = min(cell[0] for cell in cells)
            max_x = max(cell[0] for cell in cells)
            min_y = min(cell[1] for cell in cells)
            max_y = max(cell[1] for cell in cells)
            
            shape_width = (max_x - min_x + 1) * CELL_SIZE
            shape_height = (max_y - min_y + 1) * CELL_SIZE
            shape_x = panel_x + (panel_width - shape_width) // 2
            shape_y = shape_start_y + i * 130 + (100 - shape_height) // 2
            
            if self.selected_shape_index == i:
                pygame.draw.rect(self.screen, HIGHLIGHT_COLOR, 
                               (shape_x - 8, shape_y - 8, shape_width + 16, shape_height + 16), 
                               3, border_radius=12)
            
            for cell in cells:
                cell_x = shape_x + (cell[0] - min_x) * CELL_SIZE
                cell_y = shape_y + (cell[1] - min_y) * CELL_SIZE
                if block_id in self.images:
                    self.images[block_id].draw(self.screen, cell_x, cell_y)
                else:
                    pygame.draw.rect(self.screen, (255, 100, 100), (cell_x + 2, cell_y + 2, CELL_SIZE - 4, CELL_SIZE - 4), border_radius=10)

    def draw_score(self):
        score_text = font_main.render(f"{self.score}", True, TEXT_COLOR)
        score_rect = score_text.get_rect(center=(BOARD_OFFSET_X + BOARD_WIDTH // 2, BOARD_OFFSET_Y - 40))
        self.screen.blit(score_text, score_rect)

    def draw_game_over(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))
        
        box_width = 400
        box_height = 250
        box_x = (SCREEN_WIDTH - box_width) // 2
        box_y = (SCREEN_HEIGHT - box_height) // 2
        pygame.draw.rect(self.screen, (40, 40, 60), (box_x, box_y, box_width, box_height), border_radius=20)
        
        game_over_text = font_main.render("ИГРА ОКОНЧЕНА", True, DANGER_COLOR)
        game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, box_y + 60))
        self.screen.blit(game_over_text, game_over_rect)
        
        score_text = font_score.render(f"Ваш счёт: {self.score}", True, TEXT_COLOR)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, box_y + 120))
        self.screen.blit(score_text, score_rect)
        
        restart_text = font_small.render("Нажмите R для рестарта", True, ACCENT_COLOR)
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, box_y + 190))
        self.screen.blit(restart_text, restart_rect)

    def can_place_shape(self, shape_cells, row, col):
        for cell in shape_cells:
            r = row + cell[1]
            c = col + cell[0]
            if r < 0 or r >= GRID_ROWS or c < 0 or c >= GRID_COLS:
                return False
            if self.grid[r][c] is not None:
                return False
        return True

    def place_shape(self, shape_data, row, col):
        cells = shape_data['cells']
        block_id = shape_data['block_id']
        
        for cell in cells:
            r = row + cell[1]
            c = col + cell[0]
            self.grid[r][c] = self.images[block_id] if block_id in self.images else KobildzhonBlock()
        
        self.clear_lines()
        self.current_shapes.pop(self.selected_shape_index)
        self.selected_shape_index = None
        
        if not self.current_shapes:
            self.spawn_shapes()

    def clear_lines(self):
        lines_to_clear = []
        
        for row in range(GRID_ROWS):
            if all(self.grid[row][col] is not None for col in range(GRID_COLS)):
                lines_to_clear.append(('row', row))
        
        for col in range(GRID_COLS):
            if all(self.grid[row][col] is not None for row in range(GRID_ROWS)):
                lines_to_clear.append(('col', col))
        
        for line_type, index in lines_to_clear:
            if line_type == 'row':
                for col in range(GRID_COLS):
                    self.grid[index][col] = None
            elif line_type == 'col':
                for row in range(GRID_ROWS):
                    self.grid[row][index] = None
        
        self.score += len(lines_to_clear) * 150

    def check_game_over(self):
        for shape_data in self.current_shapes:
            cells = shape_data['cells']
            found_placement = False
            for row in range(GRID_ROWS):
                for col in range(GRID_COLS):
                    if self.can_place_shape(cells, row, col):
                        found_placement = True
                        break
                if found_placement:
                    break
            if not found_placement:
                return True
        return False

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and self.game_over:
                    self.reset_game()
            
            if not self.game_over:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        mouse_x, mouse_y = pygame.mouse.get_pos()
                        
                        panel_x = BOARD_OFFSET_X + BOARD_WIDTH + 20
                        panel_width = SIDEBAR_WIDTH - 30
                        shape_start_y = 130
                        
                        for i, shape_data in enumerate(self.current_shapes):
                            cells = shape_data['cells']
                            min_x = min(cell[0] for cell in cells)
                            max_x = max(cell[0] for cell in cells)
                            min_y = min(cell[1] for cell in cells)
                            max_y = max(cell[1] for cell in cells)
                            
                            shape_width = (max_x - min_x + 1) * CELL_SIZE
                            shape_height = (max_y - min_y + 1) * CELL_SIZE
                            shape_x = panel_x + (panel_width - shape_width) // 2
                            shape_y = shape_start_y + i * 130 + (100 - shape_height) // 2
                            
                            if (shape_x <= mouse_x <= shape_x + shape_width and 
                                shape_y <= mouse_y <= shape_y + shape_height):
                                self.selected_shape_index = i
                                self.dragging = True
                                self.drag_offset = (mouse_x - shape_x, mouse_y - shape_y)
                                break
                
                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1 and self.dragging:
                        self.dragging = False
                        
                        if self.selected_shape_index is not None:
                            shape_data = self.current_shapes[self.selected_shape_index]
                            cells = shape_data['cells']
                            
                            mouse_x, mouse_y = pygame.mouse.get_pos()
                            hover_col = (mouse_x - BOARD_OFFSET_X) // CELL_SIZE
                            hover_row = (mouse_y - BOARD_OFFSET_Y) // CELL_SIZE
                            
                            if 0 <= hover_col < GRID_COLS and 0 <= hover_row < GRID_ROWS:
                                min_x = min(cell[0] for cell in cells)
                                min_y = min(cell[1] for cell in cells)
                                
                                place_row = hover_row - min_y
                                place_col = hover_col - min_x
                                
                                if self.can_place_shape(cells, place_row, place_col):
                                    self.place_shape(shape_data, place_row, place_col)
                                    self.selected_shape_index = None
                                else:
                                    self.selected_shape_index = None
                            else:
                                self.selected_shape_index = None
                
                if event.type == pygame.MOUSEMOTION:
                    if self.dragging and self.selected_shape_index is not None:
                        mouse_x, mouse_y = pygame.mouse.get_pos()
                        hover_col = (mouse_x - BOARD_OFFSET_X) // CELL_SIZE
                        hover_row = (mouse_y - BOARD_OFFSET_Y) // CELL_SIZE
                        
                        if 0 <= hover_col < GRID_COLS and 0 <= hover_row < GRID_ROWS:
                            shape_data = self.current_shapes[self.selected_shape_index]
                            cells = shape_data['cells']
                            min_x = min(cell[0] for cell in cells)
                            min_y = min(cell[1] for cell in cells)
                            
                            place_row = hover_row - min_y
                            place_col = hover_col - min_x
                            
                            self.hover_cell = (place_row, place_col)
                            self.is_valid_placement = self.can_place_shape(cells, place_row, place_col)
                        else:
                            self.hover_cell = None
                            self.is_valid_placement = False

    def update(self):
        if not self.game_over:
            self.game_over = self.check_game_over()

    def draw(self):
        self.draw_background()
        self.draw_grid()
        self.draw_shapes()
        self.draw_score()
        
        if self.dragging and self.selected_shape_index is not None:
            shape_data = self.current_shapes[self.selected_shape_index]
            cells = shape_data['cells']
            min_x = min(cell[0] for cell in cells)
            min_y = min(cell[1] for cell in cells)
            
            mouse_x, mouse_y = pygame.mouse.get_pos()
            draw_x = mouse_x - self.drag_offset[0]
            draw_y = mouse_y - self.drag_offset[1]
            
            for cell in cells:
                cell_x = draw_x + (cell[0] - min_x) * CELL_SIZE
                cell_y = draw_y + (cell[1] - min_y) * CELL_SIZE
                
                if self.hover_cell is not None and self.is_valid_placement:
                    hover_row, hover_col = self.hover_cell
                    if 0 <= hover_row < GRID_ROWS and 0 <= hover_col < GRID_COLS:
                        pygame.draw.rect(self.screen, (100, 255, 100, 100), 
                                       (BOARD_OFFSET_X + hover_col * CELL_SIZE, 
                                        BOARD_OFFSET_Y + hover_row * CELL_SIZE,
                                        CELL_SIZE, CELL_SIZE), 3, border_radius=8)
                
                block_id = shape_data['block_id']
                if block_id in self.images:
                    self.images[block_id].draw(self.screen, cell_x, cell_y)
                else:
                    pygame.draw.rect(self.screen, (255, 100, 100), (cell_x + 2, cell_y + 2, CELL_SIZE - 4, CELL_SIZE - 4), border_radius=10)
        
        if self.game_over:
            self.draw_game_over()
        
        pygame.display.flip()

    def reset_game(self):
        self.grid = [[None for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]
        self.score = 0
        self.current_shapes = []
        self.selected_shape_index = None
        self.dragging = False
        self.hover_cell = None
        self.game_over = False
        self.spawn_shapes()

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = BlockBlastKobildzhon()
    game.run()