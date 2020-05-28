import sys
from pynput.keyboard import Listener
from pynput import keyboard
import time
from myApp import *
import random
import resource


# class for objects that represents one field of the grid
class Element:
    def __init__(self, scene, idx_x, idx_y, size, even, border, empty, myApp):
        self.size = size
        self.idx_x = idx_x
        self.idx_y = idx_y
        self.even = even
        self.treat = False
        self.snake = False
        self.empty = empty
        self.border = border
        self.pix_treat = QPixmap(":treat2.png")
        self.pix_border = QPixmap(":border.png")
        self.pix_snake = QPixmap(":snake2.png")
        self.item = QGraphicsPixmapItem()
        scene.addItem(self.item)
        if even:
            self.item.setPos(self.idx_x*size, self.idx_y*size)
        elif not even:
            self.item.setPos((self.idx_x * size)+15, self.idx_y * size)


# grid that is made of objects Element
class Grid(QGraphicsScene):
    def __init__(self, width, height, size):
        super().__init__()
        self.size = size
        self.width = width
        self.height = height
        self.grid = []

    # creating grid
    def add_itmes(self, myApp):
        for w in range(self.width):
            for h in range(self.height):
                # adding elements and checking whether they are border or not
                if h % 2 == 0:
                    if w == 0 or w == self.width-1 or h == 0 or h == self.height-1:
                        self.grid.append(Element(self, w, h, self.size, True, True, False, myApp))
                    else:
                        self.grid.append(Element(self, w, h, self.size, True, False, True, myApp))
                else:
                    if w == 0 or w == self.width-1 or h == 0 or h == self.height-1:
                        self.grid.append(Element(self, w, h, self.size, False, True, False, myApp))
                    else:
                        self.grid.append(Element(self, w, h, self.size, False, False, True, myApp))


# class that represents snake
class Snake:
    def __init__(self, body):
        self.score = 0
        self.body = body  # list of all body parts coordinates
        self.head = []  # head coordinates
        self.tail = []  # tail coordinates
        self.even = False
        self.ate = False


class Window(QMainWindow):
    def __init__(self, app):
        QMainWindow.__init__(self)
        self.app = app
        self.grid = []
        self.width = 18
        self.play = False

    # showing grid depending on type of element
    def printuj(self):
        for el in self.grid.grid:
            if el.empty:
                el.item.setPixmap(el.pix_border)
            elif el.treat:
                el.item.setPixmap(el.pix_treat)
            elif el.snake:
                el.item.setPixmap(el.pix_snake)
            el.item.show()

    # initiating the game
    def start(self):
        self.snake1 = Snake([])  # adding two snakes
        self.snake2 = Snake([])
        self.key = keyboard.KeyCode(char='d')  # in what direction will those snakes move
        self.key2 = keyboard.KeyCode(char='k')
        self.grid.grid = []
        self.grid.add_itmes(myApp)  # creating new grid
        self.add_treat()  # adding first treat
        self.add_snake(int(self.grid.width / 2), (int)(self.grid.height / 2), self.snake1)
        self.add_snake(int(self.grid.width / 2), (int)(self.grid.height / 2) + 5, self.snake2)
        self.snake1.tail = self.snake1.head
        self.snake2.tail = self.snake2.head
        self.playing()

    # finding empty element for new treat
    def add_treat(self):
        located = False
        idx = 0
        while not located:
            idx = random.randint(0, len(self.grid.grid) - 1)
            located = self.grid.grid[idx].empty
        self.grid.grid[idx].treat = True
        self.grid.grid[idx].empty = False

    def add_snake(self, x, y, snake):
        snake.head = [x, y]  # new coordiantes of snake's head
        snake.body.insert(0, [x, y])
        for el in self.grid.grid:
            if el.idx_x == x and el.idx_y == y:
                if el.snake or el.border:  # checking if snake bit himself or another snake/ bumped the border
                    self.collision()
                el.snake = True
                el.empty = False
                snake.even = el.even
                if el.treat:  # checking if snake ate the treat
                    snake.ate = True
                    el.treat = False
                break

    # if snake didn't eat a treat - delete last element of his body
    def cut_tail(self, snake):
        for el in self.grid.grid:
            if el.idx_x == snake.tail[0] and el.idx_y == snake.tail[1]:
                el.snake = False
                el.empty = True
        snake.body.pop()
        snake.tail = snake.body[-1]

    def collision(self):
        myApp.game_over.setText("GAME OVER!")
        self.play = False

    # if New game button was pressed - delete all elements in grid
    def new_game(self):
        myApp.game_over.setText(" ")
        self.play = False
        for item in self.grid.items():
            self.grid.removeItem(item)

    def game(self, myApp):
        self.grid = Grid(18, 18, 30)
        self.grid.setSceneRect(0, 0, myApp.graphicsView.width(), myApp.graphicsView.height())
        myApp.graphicsView.setScene(self.grid)
        myApp.start.clicked.connect(self.start)
        myApp.new_game.clicked.connect(self.new_game)
        myApp.exit.clicked.connect(exit)
        listener = Listener(on_press=self.on_press)
        listener.start()

    def playing(self):
        self.play = True
        while self.play:
            self.key_handler(self.snake1, self.key, keyboard.KeyCode(char='w'), keyboard.KeyCode(char='e'), keyboard.KeyCode(char='z'), keyboard.KeyCode(char='x'), keyboard.KeyCode(char='a'), keyboard.KeyCode(char='d'))
            self.key_handler(self.snake2, self.key2, keyboard.KeyCode(char='u'), keyboard.KeyCode(char='i'),
                             keyboard.KeyCode(char='n'), keyboard.KeyCode(char='m'), keyboard.KeyCode(char='h'),
                             keyboard.KeyCode(char='k'))

            # snake 1
            if not self.snake1.ate:
                self.cut_tail(self.snake1)
            else:
                self.snake1.score += 1
                myApp.score1.setText('Score 1: '+str(self.snake1.score))
                self.snake1.ate = False
                self.add_treat()

            # snake 2
            if not self.snake2.ate:
                self.cut_tail(self.snake2)
            else:
                self.snake2.score += 1
                myApp.score2.setText('Score 2: ' + str(self.snake2.score))
                self.snake2.ate = False
                self.add_treat()
            self.printuj()  # updating the window

            self.app.processEvents()
            time.sleep(0.9)
            self.show()

    # checking which key was pressed
    def on_press(self, key):
        if key in [keyboard.KeyCode(char='w'), keyboard.KeyCode(char='e'), keyboard.KeyCode(char='a'), keyboard.KeyCode(char='d'), keyboard.KeyCode(char='z'), keyboard.KeyCode(char='x')]:
            self.key = key
        elif key in [keyboard.KeyCode(char='u'), keyboard.KeyCode(char='i'), keyboard.KeyCode(char='h'), keyboard.KeyCode(char='k'), keyboard.KeyCode(char='m'), keyboard.KeyCode(char='n')]:
            self.key2 = key

    # updating snake's head coordinates depending which key was pressed
    def key_handler(self, snake, main_key, upl, upr, downl, downr, left, right):
        if main_key == right:
            self.add_snake(snake.head[0] + 1, snake.head[1], snake)
        elif main_key == left:
            self.add_snake(snake.head[0] - 1, snake.head[1], snake)
        elif main_key == upl:
            if snake.even:
                self.add_snake(snake.head[0] - 1, snake.head[1] - 1, snake)
            else:
                self.add_snake(snake.head[0], snake.head[1] - 1, snake)
        elif main_key == upr:
            if snake.even:
                self.add_snake(snake.head[0], snake.head[1] - 1, snake)
            else:
                self.add_snake(snake.head[0] + 1, snake.head[1] - 1, snake)
        elif main_key == downl:
            if snake.even:
                self.add_snake(snake.head[0] - 1, snake.head[1] + 1, snake)
            else:
                self.add_snake(snake.head[0], snake.head[1] + 1, snake)
        elif main_key == downr:
            if snake.even:
                self.add_snake(snake.head[0], snake.head[1] + 1, snake)
            else:
                self.add_snake(snake.head[0] + 1, snake.head[1] + 1, snake)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = Window(app)
    myApp = Ui_MainWindow()
    myApp.setupUi(mainWindow)
    mainWindow.game(myApp)
    mainWindow.show()

    app.exec_()
