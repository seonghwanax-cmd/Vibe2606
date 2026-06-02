import random
import tkinter as tk

COLS = 10
ROWS = 20
BLOCK_SIZE = 28
DROP_SPEEDS = [800, 650, 520, 400, 300, 220, 160, 120, 90, 70]

COLORS = {
    0: '#090b1d',
    1: '#ff4c4c',
    2: '#ff8f3d',
    3: '#ffd93d',
    4: '#4cff79',
    5: '#32b6ff',
    6: '#9c5dff',
    7: '#ff42c4',
}

SHAPES = {
    'I': [[1, 1, 1, 1]],
    'J': [[2, 0, 0], [2, 2, 2]],
    'L': [[0, 0, 3], [3, 3, 3]],
    'O': [[4, 4], [4, 4]],
    'S': [[0, 5, 5], [5, 5, 0]],
    'T': [[0, 6, 0], [6, 6, 6]],
    'Z': [[7, 7, 0], [0, 7, 7]],
}

KEY_BINDINGS = {
    'Left': 'left',
    'Right': 'right',
    'Down': 'down',
    'space': 'rotate',
    'p': 'pause',
    'P': 'pause',
    'Return': 'start',
}


class TetrisGame:
    def __init__(self, master):
        self.master = master
        master.title('파이썬 테트리스')
        master.configure(bg='#0d1024')

        self.board = self.create_matrix(COLS, ROWS)
        self.score = 0
        self.lines = 0
        self.level = 1
        self.drop_interval = DROP_SPEEDS[0]
        self.paused = False
        self.game_over = False
        self.current_piece = None
        self.current_x = 0
        self.current_y = 0
        self.next_piece = self.create_piece(self.random_piece())
        self.job_id = None

        self.build_ui()
        self.start_game()

    def build_ui(self):
        main_frame = tk.Frame(self.master, bg='#0d1024')
        main_frame.pack(padx=16, pady=16)

        left_frame = tk.Frame(main_frame, bg='#0d1024')
        left_frame.grid(row=0, column=0, sticky='n')

        title = tk.Label(
            left_frame,
            text='HTML5 ➜ Python 테트리스',
            fg='#f8f8f8',
            bg='#0d1024',
            font=('Segoe UI', 18, 'bold'),
        )
        title.pack(anchor='w', pady=(0, 8))

        description = tk.Label(
            left_frame,
            text='화살표로 이동, 아래로 빠르게 낙하, 스페이스로 회전합니다.',
            fg='#c8d1ff',
            bg='#0d1024',
            font=('Segoe UI', 11),
            justify='left',
            wraplength=280,
        )
        description.pack(anchor='w', pady=(0, 12))

        self.canvas = tk.Canvas(
            left_frame,
            width=COLS * BLOCK_SIZE,
            height=ROWS * BLOCK_SIZE,
            bg=COLORS[0],
            highlightthickness=0,
        )
        self.canvas.pack()

        right_frame = tk.Frame(main_frame, bg='#0d1024')
        right_frame.grid(row=0, column=1, padx=(18, 0), sticky='n')

        self.score_label = self.stat_label(right_frame, '점수', '0')
        self.lines_label = self.stat_label(right_frame, '라인', '0')
        self.level_label = self.stat_label(right_frame, '레벨', '1')

        button_frame = tk.Frame(right_frame, bg='#0d1024')
        button_frame.pack(fill='x', pady=(10, 10))

        self.start_button = tk.Button(
            button_frame,
            text='게임 시작',
            command=self.start_game,
            bg='#5e4bff',
            fg='#ffffff',
            activebackground='#4a6cff',
            relief='flat',
            font=('Segoe UI', 11, 'bold'),
            padx=8,
            pady=8,
        )
        self.start_button.pack(fill='x', pady=(0, 8))

        self.pause_button = tk.Button(
            button_frame,
            text='일시정지',
            command=self.toggle_pause,
            bg='#5e4bff',
            fg='#ffffff',
            activebackground='#4a6cff',
            relief='flat',
            font=('Segoe UI', 11, 'bold'),
            padx=8,
            pady=8,
        )
        self.pause_button.pack(fill='x')

        hint_frame = tk.LabelFrame(
            right_frame,
            text='조작',
            fg='#7c8aff',
            bg='#101533',
            bd=1,
            padx=10,
            pady=10,
            labelanchor='n',
            font=('Segoe UI', 10, 'bold'),
        )
        hint_frame.pack(fill='x', pady=(12, 8))

        hint_text = '←: 왼쪽 이동\n→: 오른쪽 이동\n↓: 빠르게 낙하\n스페이스: 회전\nP: 일시정지\nEnter: 새 게임'
        hint_label = tk.Label(
            hint_frame,
            text=hint_text,
            fg='#b8c2ff',
            bg='#101533',
            justify='left',
            font=('Segoe UI', 10),
        )
        hint_label.pack(anchor='w')

        next_frame = tk.LabelFrame(
            right_frame,
            text='다음 조각',
            fg='#7c8aff',
            bg='#101533',
            bd=1,
            padx=10,
            pady=10,
            labelanchor='n',
            font=('Segoe UI', 10, 'bold'),
        )
        next_frame.pack(fill='both', pady=(0, 10))

        self.next_canvas = tk.Canvas(
            next_frame,
            width=6 * BLOCK_SIZE,
            height=6 * BLOCK_SIZE,
            bg=COLORS[0],
            highlightthickness=0,
        )
        self.next_canvas.pack()

        footer = tk.Label(
            right_frame,
            text='Python Tkinter로 구현한 테트리스',
            fg='#8290e2',
            bg='#0d1024',
            font=('Segoe UI', 9),
        )
        footer.pack(anchor='center', pady=(12, 0))

        self.master.bind('<KeyPress>', self.on_key_press)

    def stat_label(self, parent, title, value):
        frame = tk.Frame(parent, bg='#101533')
        frame.pack(fill='x', pady=4)

        label_title = tk.Label(
            frame,
            text=title,
            fg='#aab7ff',
            bg='#101533',
            font=('Segoe UI', 10),
        )
        label_title.pack(side='left')

        label_value = tk.Label(
            frame,
            text=value,
            fg='#ffffff',
            bg='#101533',
            font=('Segoe UI', 12, 'bold'),
        )
        label_value.pack(side='right')

        return label_value

    @staticmethod
    def create_matrix(width, height):
        return [[0 for _ in range(width)] for _ in range(height)]

    @staticmethod
    def random_piece():
        return random.choice(list(SHAPES.keys()))

    @staticmethod
    def rotate(matrix, direction):
        rotated = list(zip(*matrix[::-1])) if direction > 0 else list(zip(*matrix))[::-1]
        return [list(row) for row in rotated]

    def create_piece(self, kind):
        return [row[:] for row in SHAPES[kind]]

    def collide(self, matrix, offset_x, offset_y):
        for y, row in enumerate(matrix):
            for x, value in enumerate(row):
                if value == 0:
                    continue
                board_y = y + offset_y
                board_x = x + offset_x
                if board_x < 0 or board_x >= COLS or board_y >= ROWS:
                    return True
                if board_y >= 0 and self.board[board_y][board_x] != 0:
                    return True
        return False

    def merge_piece(self):
        for y, row in enumerate(self.current_piece):
            for x, value in enumerate(row):
                if value != 0 and 0 <= y + self.current_y < ROWS:
                    self.board[self.current_y + y][self.current_x + x] = value

    def sweep_rows(self):
        row_count = 0
        new_board = [row for row in self.board if any(cell == 0 for cell in row)]
        row_count = ROWS - len(new_board)
        if row_count > 0:
            for _ in range(row_count):
                new_board.insert(0, [0] * COLS)
            self.board = new_board
            self.lines += row_count
            self.score += self.calculate_points(row_count)
            self.level = min(10, self.lines // 10 + 1)
            self.drop_interval = DROP_SPEEDS[self.level - 1]

    @staticmethod
    def calculate_points(rows):
        points = {1: 40, 2: 100, 3: 300, 4: 1200}
        return points.get(rows, 0)

    def drop_piece(self):
        self.current_y += 1
        if self.collide(self.current_piece, self.current_x, self.current_y):
            self.current_y -= 1
            self.merge_piece()
            self.sweep_rows()
            self.spawn_piece()
        self.drop_counter = 0

    def spawn_piece(self):
        if self.next_piece is None:
            self.next_piece = self.create_piece(self.random_piece())
        self.current_piece = self.next_piece
        self.next_piece = self.create_piece(self.random_piece())
        self.current_y = 0
        self.current_x = (COLS - len(self.current_piece[0])) // 2
        if self.collide(self.current_piece, self.current_x, self.current_y):
            self.game_over = True
            self.paused = True
            self.update_status()
            self.master.after_cancel(self.job_id) if self.job_id else None
            self.pause_button.config(text='일시정지')
            self.show_game_over()

    def show_game_over(self):
        self.canvas.create_text(
            COLS * BLOCK_SIZE // 2,
            ROWS * BLOCK_SIZE // 2,
            text='게임 오버',
            fill='#ffffff',
            font=('Segoe UI', 24, 'bold'),
            tags='game_over',
        )

    def clear_game_over_text(self):
        self.canvas.delete('game_over')

    def move_piece(self, direction):
        if direction == 'left':
            new_x = self.current_x - 1
            if not self.collide(self.current_piece, new_x, self.current_y):
                self.current_x = new_x
        elif direction == 'right':
            new_x = self.current_x + 1
            if not self.collide(self.current_piece, new_x, self.current_y):
                self.current_x = new_x
        elif direction == 'down':
            self.drop_piece()

    def rotate_piece(self):
        rotated = self.rotate(self.current_piece, 1)
        offset = 0
        while self.collide(rotated, self.current_x, self.current_y):
            offset += 1
            if offset > len(self.current_piece[0]):
                return
            self.current_x += offset if offset % 2 else -offset
        self.current_piece = rotated

    def on_key_press(self, event):
        action = KEY_BINDINGS.get(event.keysym)
        if action == 'left':
            self.move_piece('left')
        elif action == 'right':
            self.move_piece('right')
        elif action == 'down':
            self.move_piece('down')
        elif action == 'rotate':
            self.rotate_piece()
        elif action == 'pause':
            self.toggle_pause()
        elif action == 'start':
            self.start_game()
        self.redraw()

    def update_status(self):
        self.score_label.config(text=str(self.score))
        self.lines_label.config(text=str(self.lines))
        self.level_label.config(text=str(self.level))

    def redraw(self):
        self.canvas.delete('all')
        self.draw_background_grid()
        self.draw_matrix(self.board, 0, 0, self.canvas)
        self.draw_ghost_piece()
        self.draw_matrix(self.current_piece, self.current_x, self.current_y, self.canvas)
        self.draw_next_piece()

    def draw_background_grid(self):
        for y in range(ROWS):
            for x in range(COLS):
                x0 = x * BLOCK_SIZE
                y0 = y * BLOCK_SIZE
                x1 = x0 + BLOCK_SIZE
                y1 = y0 + BLOCK_SIZE
                self.canvas.create_rectangle(
                    x0,
                    y0,
                    x1,
                    y1,
                    fill='',
                    outline='#aaaaaa',
                    width=0.6,
                )

    def find_ghost_y(self):
        ghost_y = self.current_y
        while not self.collide(self.current_piece, self.current_x, ghost_y + 1):
            ghost_y += 1
        return ghost_y

    def draw_ghost_piece(self):
        ghost_y = self.find_ghost_y()
        if ghost_y == self.current_y:
            return
        for y, row in enumerate(self.current_piece):
            for x, value in enumerate(row):
                if value == 0:
                    continue
                x0 = (self.current_x + x) * BLOCK_SIZE
                y0 = (ghost_y + y) * BLOCK_SIZE
                x1 = x0 + BLOCK_SIZE
                y1 = y0 + BLOCK_SIZE
                self.canvas.create_rectangle(
                    x0,
                    y0,
                    x1,
                    y1,
                    fill=COLORS[value],
                    stipple='gray12',
                    outline='#ffffff',
                    width=1,
                )

    def draw_matrix(self, matrix, offset_x, offset_y, canvas):
        for y, row in enumerate(matrix):
            for x, value in enumerate(row):
                if value == 0:
                    continue
                x0 = (offset_x + x) * BLOCK_SIZE
                y0 = (offset_y + y) * BLOCK_SIZE
                x1 = x0 + BLOCK_SIZE
                y1 = y0 + BLOCK_SIZE
                canvas.create_rectangle(
                    x0,
                    y0,
                    x1,
                    y1,
                    fill=COLORS[value],
                    outline='#ffffff',
                    width=1,
                )

    def draw_next_piece(self):
        self.next_canvas.delete('all')
        self.next_canvas.create_rectangle(
            0,
            0,
            6 * BLOCK_SIZE,
            6 * BLOCK_SIZE,
            fill=COLORS[0],
            outline='',
        )
        if self.next_piece is None:
            return
        start_x = 1
        start_y = 1
        for y, row in enumerate(self.next_piece):
            for x, value in enumerate(row):
                if value == 0:
                    continue
                x0 = (start_x + x) * BLOCK_SIZE
                y0 = (start_y + y) * BLOCK_SIZE
                x1 = x0 + BLOCK_SIZE
                y1 = y0 + BLOCK_SIZE
                self.next_canvas.create_rectangle(
                    x0,
                    y0,
                    x1,
                    y1,
                    fill=COLORS[value],
                    outline='#ffffff',
                    width=1,
                )

    def game_tick(self):
        if not self.paused and not self.game_over:
            self.drop_piece()
            self.redraw()
            self.update_status()
        self.job_id = self.master.after(self.drop_interval, self.game_tick)

    def start_game(self):
        self.board = self.create_matrix(COLS, ROWS)
        self.score = 0
        self.lines = 0
        self.level = 1
        self.drop_interval = DROP_SPEEDS[0]
        self.paused = False
        self.game_over = False
        self.next_piece = self.create_piece(self.random_piece())
        self.spawn_piece()
        self.clear_game_over_text()
        self.update_status()
        self.pause_button.config(text='일시정지')
        if self.job_id:
            self.master.after_cancel(self.job_id)
        self.redraw()
        self.job_id = self.master.after(self.drop_interval, self.game_tick)

    def toggle_pause(self):
        if self.game_over:
            return
        self.paused = not self.paused
        self.pause_button.config(text='재개' if self.paused else '일시정지')
        if not self.paused and self.job_id is None:
            self.job_id = self.master.after(self.drop_interval, self.game_tick)


if __name__ == '__main__':
    root = tk.Tk()
    app = TetrisGame(root)
    root.mainloop()
