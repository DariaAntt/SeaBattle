#  Module Imports
import pygame
import random
import json
from tkinter import Tk, filedialog


#  Module Initialization
pygame.init()


#  Game Assets and Objects
class Ship:
    def __init__(self, name, img, pos, size):
        self.name = name
        self.pos = pos
        #  Load the Vertical image
        self.vImage = loadImage(img, size)
        self.vImageWidth = self.vImage.get_width()
        self.vImageHeight = self.vImage.get_height()
        self.vImageRect = self.vImage.get_rect()
        self.vImageRect.topleft = pos
        #  Load the Horizontal image
        self.hImage = pygame.transform.rotate(self.vImage, -90)
        self.hImageWidth = self.hImage.get_width()
        self.hImageHeight = self.hImage.get_height()
        self.hImageRect = self.hImage.get_rect()
        self.hImageRect.topleft = pos
        #  Image and Rectangle
        self.image = self.vImage
        self.rect = self.vImageRect
        self.rotation = False
        #  Ship is current selection
        self.active = False


    def selectShipAndMove(self):
        """Selects the ship and moves it according to the mouse position"""
        while self.active == True:
            self.rect.center = pygame.mouse.get_pos()
            updateGameScreen(GAMESCREEN, GAMESTATE)
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if not self.checkForCollisions(pFleet):
                        if event.button == 1:
                            self.hImageRect.center = self.vImageRect.center = self.rect.center
                            self.active = False

                    if event.button == 3:
                        self.rotateShip()


    def rotateShip(self, doRotation=False):       
        """Поворачивает корабль между вертикальным и горизонтальным положением."""
        if self.active or doRotation:
            # Переключаем флаг ориентации
            self.rotation = not self.rotation

            # Переключаем изображение и прямоугольник
            self.switchImageAndRect()

            # Перемещаем текущий прямоугольник в его положение
            self.rect.topleft = self.rect.topleft

            # Синхронизируем прямоугольники с новым положением
            self.hImageRect.topleft = self.rect.topleft
            self.vImageRect.topleft = self.rect.topleft

            # Отладка
            print(f"Корабль '{self.name}' повернут. Новая ориентация: {'горизонтальная' if self.rotation else 'вертикальная'}.")
        # """switch ship between vertical and horizontal"""
        # if self.active or doRotation == True:
        #     if self.rotation == False:
        #         self.rotation = True
        #     else:
        #         self.rotation = False
        #     self.switchImageAndRect()


    def switchImageAndRect(self):
        """Переключает изображения и прямоугольники между горизонтальным и вертикальным положением."""
        if self.rotation:  # Горизонтальная ориентация
            self.image = self.hImage
            self.rect = self.hImageRect
        else:  # Вертикальная ориентация
            self.image = self.vImage
            self.rect = self.vImageRect

        # Обновляем центр прямоугольников
        self.hImageRect.center = self.rect.center
        self.vImageRect.center = self.rect.center

        # Отладка
        print(f"Синхронизация изображения и прямоугольников завершена для '{self.name}'.")

        # """Switches from Horizontal to Vertical and vice versa"""
        # if self.rotation == True:
        #     self.image = self.hImage
        #     self.rect = self.hImageRect
        # else:
        #     self.image = self.vImage
        #     self.rect = self.vImageRect
        # self.hImageRect.center = self.vImageRect.center = self.rect.center


    def checkForCollisions(self, shiplist):
        """Check to make sure the ship is not colliding with any of the other ships"""
        slist = shiplist.copy()
        slist.remove(self)
        for ship in slist:
        # Проверка прямого столкновения
            if self.rect.colliderect(ship.rect):
                return True        
        # Проверка на расстояние в одну клетку
            buffer_zone = pygame.Rect(
                ship.rect.left - CELLSIZE,
                ship.rect.top - CELLSIZE,
                ship.rect.width + 2 * CELLSIZE,
                ship.rect.height + 2 * CELLSIZE
            )
            if buffer_zone.colliderect(self.rect):
                return True
        return False


    def checkForRotateCollisions(self, shiplist):
        """Проверяет, не будет ли столкновений при повороте корабля."""
        # Список всех кораблей, кроме текущего
        slist = shiplist.copy()
        slist.remove(self)

        # Предполагаемый новый прямоугольник после поворота
        new_rect = self.hImageRect if not self.rotation else self.vImageRect

        for ship in slist:
            # Проверка прямого столкновения
            if new_rect.colliderect(ship.rect):
                return True

            # Проверка буферной зоны (расстояние в одну клетку)
            buffer_zone = pygame.Rect(
                ship.rect.left - CELLSIZE,
                ship.rect.top - CELLSIZE,
                ship.rect.width + 2 * CELLSIZE,
                ship.rect.height + 2 * CELLSIZE
            )
            if buffer_zone.colliderect(new_rect):
                return True

        return False
        # """Check to make sure the ship is not going to collide with any other ship before rotating"""
        # slist = shiplist.copy()
        # slist.remove(self)
        # # Предполагаемое новое положение после поворота
        # new_rect = self.hImageRect if not self.rotation else self.vImageRect
        # for ship in slist:
        #     # Проверка прямого столкновения
        #     if new_rect.colliderect(ship.rect):
        #         return True
            
        #     # Проверка буферной зоны (расстояние 1 клетка)
        #     buffer_zone = pygame.Rect(
        #         ship.rect.left - CELLSIZE,
        #         ship.rect.top - CELLSIZE,
        #         ship.rect.width + 2 * CELLSIZE,
        #         ship.rect.height + 2 * CELLSIZE
        #     )
        #     if buffer_zone.colliderect(new_rect):
        #         return True
        # return False


    def returnToDefaultPosition(self):
        """Returns the ship to its default position"""
        if self.rotation == True:
            self.rotateShip(True)

        self.rect.topleft = self.pos
        self.hImageRect.center = self.vImageRect.center = self.rect.center


    def snapToGridEdge(self, gridCoords):
        if self.rect.topleft != self.pos:

            #  Check to see if the ships position is outside of the grid:
            if self.rect.left > gridCoords[0][-1][0] + CELLSIZE or \
                self.rect.right < gridCoords[0][0][0] or \
                self.rect.top > gridCoords[-1][0][1] + CELLSIZE or \
                self.rect.bottom < gridCoords[0][0][1]:
                self.returnToDefaultPosition()

            elif self.rect.right > gridCoords[0][-1][0]+CELLSIZE:
                self.rect.right = gridCoords[0][-1][0] + CELLSIZE
            elif self.rect.left < gridCoords[0][0][0]:
                self.rect.left = gridCoords[0][0][0]
            elif self.rect.top < gridCoords[0][0][1]:
                self.rect.top = gridCoords[0][0][1]
            elif self.rect.bottom > gridCoords[-1][0][1] + CELLSIZE:
                self.rect.bottom = gridCoords[-1][0][1] + CELLSIZE
            self.vImageRect.center = self.hImageRect.center = self.rect.center


    def snapToGrid(self, gridCoords):
        for rowX in gridCoords:
            for cell in rowX:
                if self.rect.left >= cell[0] and self.rect.left < cell[0] + CELLSIZE \
                    and self.rect.top >= cell[1] and self.rect.top < cell[1] + CELLSIZE:
                    if self.rotation == False:
                        self.rect.topleft = (cell[0] + (CELLSIZE - self.image.get_width())//2, cell[1])
                    else:
                        self.rect.topleft = (cell[0], cell[1] + (CELLSIZE - self.image.get_height())//2)

        self.hImageRect.center = self.vImageRect.center = self.rect.center


    def draw(self, window):
        """Draw the ship to the screen"""
        window.blit(self.image, self.rect)
        #pygame.draw.rect(window, (255, 0, 0), self.rect, 1)

class Button:
    def __init__(self, image, size, pos, msg):
        self.name = msg
        self.image = image
        self.imageLarger = self.image
        self.imageLarger = pygame.transform.scale(self.imageLarger, (size[0] + 10, size[1] + 10))
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        self.active = False

        self.msg = self.addText(msg)
        self.msgRect = self.msg.get_rect(center=self.rect.center)


    def addText(self, msg):
        """Add font to the button image"""
        font = pygame.font.SysFont('Arial', 16)
        message = font.render(msg, 1, (255,255,255))
        return message


    def focusOnButton(self, window):
        """Brings attention to which button is being focussed on"""
        if self.active:
            if self.rect.collidepoint(pygame.mouse.get_pos()):
                window.blit(self.imageLarger, (self.rect[0] - 5, self.rect[1] - 5, self.rect[2], self.rect[3]))
            else:
                window.blit(self.image, self.rect)


    def actionOnPress(self):
        """Which actions to take according to button selected"""
        if self.active:
            if self.name == 'Случайная':
                self.randomizeShipPositions(pFleet, pGameGrid)
                self.randomizeShipPositions(cFleet, cGameGrid)
            elif self.name == 'Сбросить':
                self.resetShips(pFleet)
            elif self.name == 'Играть':
                self.deploymentPhase()
            elif self.name == 'Сохранить':
                save_fleet_to_file(pFleet)
            elif self.name == 'Загрузить':
                load_fleet_from_file(pFleet)
            elif self.name == 'Выйти':
                pass



    def randomizeShipPositions(self, shiplist, gameGrid):
        """Calls the randomize ships function"""
        if DEPLOYMENT == True:
            randomizeShipPositions(shiplist, gameGrid)


    def resetShips(self, shiplist):
        """Resets the ships to their default positions"""
        if DEPLOYMENT == True:
            for ship in shiplist:
                ship.returnToDefaultPosition()


    def deploymentPhase(self):
        pass


    def restartTheGame(self):
        TOKENS.clear()
        self.resetShips(pFleet)
        self.randomizeShipPositions(cFleet, cGameGrid)
        updateGameLogic(cGameGrid, cFleet, cGameLogic)
        updateGameLogic(pGameGrid, pFleet, pGameLogic)


    def updateButtons(self, gameStatus):
        """update the buttons as per the game stage"""
        if self.name == 'Играть' and gameStatus == False:
            self.name = ''
        # elif self.name == 'Redeploy' and gameStatus == True:
        #     self.name = 'Играть'
        # if self.name == 'Сбросить' and gameStatus == False:
        #     self.name = 'Radar Scan'
        if self.name == 'Случайная' and gameStatus == False:
            self.name = 'Выйти'
        elif self.name == 'Выйти' and gameStatus == True:
            self.name = 'Случайная'
        self.msg = self.addText(self.name)
        self.msgRect = self.msg.get_rect(center=self.rect.center)


    def draw(self, window):
        self.updateButtons(DEPLOYMENT)
        self.focusOnButton(window)
        window.blit(self.msg, self.msgRect)


# ------------------------------------------------------------------------------------------------------
# ------------------------------------- СОХРАНЕНИЕ РАССТАНОВКИ В ФАЙЛ ----------------------------------
# ------------------------------------------------------------------------------------------------------
def save_fleet_to_file(fleet):
    """Открывает окно сохранения файла и сохраняет текущую расстановку кораблей."""
    root = Tk()
    root.withdraw()  # Скрыть главное окно Tkinter
    filename = filedialog.asksaveasfilename(
        defaultextension=".sb",
        filetypes=[("Ship Battle files", "*.sb"), ("All files", "*.*")],
        title="Сохранить расстановку кораблей"
    )
    if filename:
        data = {}
        for ship in fleet:
            data[ship.name] = {
                "position": ship.rect.topleft,
                "rotation": ship.rotation
            }
        with open(filename, 'w') as f:
            json.dump(data, f)


def load_fleet_from_file(fleet):
    """Открывает окно выбора файла и загружает расстановку кораблей."""
    root = Tk()
    root.withdraw()  # Скрыть главное окно Tkinter
    filename = filedialog.askopenfilename(
        filetypes=[("Ship Battle files", "*.sb"), ("All files", "*.*")],
        title="Загрузить расстановку кораблей"
    )
    if filename:
        with open(filename, 'r') as f:
            data = json.load(f)

        for ship in fleet:
            if ship.name in data:
                # Устанавливаем позицию
                ship.rect.topleft = tuple(data[ship.name]["position"])

                # Устанавливаем ориентацию
                if data[ship.name]["rotation"] != ship.rotation:
                    ship.rotation = data[ship.name]["rotation"]
                    ship.switchImageAndRect()

                # Синхронизация прямоугольников
                ship.hImageRect.topleft = ship.rect.topleft
                ship.vImageRect.topleft = ship.rect.topleft

                # Перемещаем изображение в правильное положение
                ship.rect = ship.hImageRect if ship.rotation else ship.vImageRect
                ship.rect.topleft = tuple(data[ship.name]["position"])

                # Отладка
                print(f"Корабль '{ship.name}' загружен: позиция={ship.rect.topleft}, ориентация={'горизонтальная' if ship.rotation else 'вертикальная'}.")
            else:
                # Если данные отсутствуют, возвращаем корабль в начальное положение
                print(f"Корабль '{ship.name}' отсутствует в данных. Возвращён в начальное положение.")
                ship.returnToDefaultPosition()
    # root = Tk()
    # root.withdraw()  # Скрыть главное окно Tkinter
    # filename = filedialog.askopenfilename(
    #     filetypes=[("Ship Battle files", "*.sb"), ("All files", "*.*")],
    #     title="Загрузить расстановку кораблей"
    # )
    # if filename:
    #     with open(filename, 'r') as f:
    #         data = json.load(f)

    #     for ship in fleet:
    #         if ship.name in data:
    #             # Загружаем позицию
    #             ship.rect.topleft = tuple(data[ship.name]["position"])

    #             # Устанавливаем ориентацию, если она не совпадает
    #             if data[ship.name]["rotation"] != ship.rotation:
    #                 ship.rotateShip(doRotation=True)

    #             # Обновляем прямоугольники
    #             ship.switchImageAndRect()
    #             ship.hImageRect.topleft = ship.rect.topleft
    #             ship.vImageRect.topleft = ship.rect.topleft
    #         else:
    #             # Если корабля нет в файле, возвращаем его в исходное положение
    #             print(f"Корабль '{ship.name}' отсутствует в файле. Возвращен в исходное положение.")
    #             ship.returnToDefaultPosition()

# ------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------

class Player:
    def __init__(self):
        self.turn = True

    def makeAttack(self, grid, logicgrid):
        """When its the player's turn, the player must make an attacking selection within the computer grid."""
        posX, posY = pygame.mouse.get_pos()
        if posX >= grid[0][0][0] and posX <= grid[0][-1][0] + CELLSIZE and posY >= grid[0][0][1] and posY <= grid[-1][0][1] + CELLSIZE:
            for i, rowX in enumerate(grid):
                for j, colX in enumerate(rowX):
                    if posX >= colX[0] and posX < colX[0] + CELLSIZE and posY >= colX[1] and posY <= colX[1] + CELLSIZE:
                        if logicgrid[i][j] != ' ':
                            if logicgrid[i][j] == 'O':
                                TOKENS.append(Tokens(REDTOKEN, grid[i][j], 'Hit', None, None, None))
                                logicgrid[i][j] = 'T'
                                self.turn = True
                                # self.turn = False
                        else:
                            logicgrid[i][j] = 'X'
                            TOKENS.append(Tokens(GREENTOKEN, grid[i][j], 'Miss', None, None, None))
                            self.turn = False
        return self.turn


class EasyComputer:
    def __init__(self):
        self.turn = False
        self.status = self.computerStatus('Thinking')
        self.name = 'Easy Computer'


    def computerStatus(self, msg):
        image = pygame.font.SysFont('Stencil', 22)
        message = image.render(msg, 1, (0, 0, 0))
        return message


    def makeAttack(self, gamelogic):
        COMPTURNTIMER = pygame.time.get_ticks()
        if COMPTURNTIMER - TURNTIMER >= 3000:
            validChoice = False
            while not validChoice:
                rowX = random.randint(0, 9)
                colX = random.randint(0, 9)

                if gamelogic[rowX][colX] == ' ' or gamelogic[rowX][colX] == 'O':
                    validChoice = True

            if gamelogic[rowX][colX] == 'O':
                TOKENS.append(Tokens(REDTOKEN, pGameGrid[rowX][colX], 'Hit', FIRETOKENIMAGELIST, EXPLOSIONIMAGELIST, None))
                gamelogic[rowX][colX] = 'T'
                self.turn = True
                COMPTURNTIMER = pygame.time.get_ticks()
                # self.turn = False
            else:
                gamelogic[rowX][colX] = 'X'
                TOKENS.append(Tokens(BLUETOKEN, pGameGrid[rowX][colX], 'Miss', None, None, None))
                self.turn = False
        return self.turn


    def draw(self, window):
        if self.turn:
            window.blit(self.status, (cGameGrid[0][0][0] - CELLSIZE, cGameGrid[-1][-1][1] + CELLSIZE))


class HardComputer(EasyComputer):
    def __init__(self):
        super().__init__()
        self.moves = []


    def makeAttack(self, gamelogic):
        if len(self.moves) == 0:
            COMPTURNTIMER = pygame.time.get_ticks()
            if COMPTURNTIMER - TURNTIMER >= 3000:
                validChoice = False
                while not validChoice:
                    rowX = random.randint(0, 9)
                    rowY = random.randint(0, 9)

                    if gamelogic[rowX][rowY] == ' ' or gamelogic[rowX][rowY] == 'O':
                        validChoice = True

                if gamelogic[rowX][rowY] == 'O':
                    TOKENS.append(
                        Tokens(REDTOKEN, pGameGrid[rowX][rowY], 'Hit', FIRETOKENIMAGELIST, EXPLOSIONIMAGELIST, None))
                    gamelogic[rowX][rowY] = 'T'
                    SHOTSOUND.play()
                    HITSOUND.play()
                    self.generateMoves((rowX, rowY), gamelogic)
                    # self.turn = False
                else:
                    gamelogic[rowX][rowY] = 'X'
                    TOKENS.append(Tokens(BLUETOKEN, pGameGrid[rowX][rowY], 'Miss', None, None, None))
                    SHOTSOUND.play()
                    MISSSOUND.play()
                    self.turn = False

        elif len(self.moves) > 0:
            COMPTURNTIMER = pygame.time.get_ticks()
            if COMPTURNTIMER - TURNTIMER >= 2000:
                rowX, rowY = self.moves[0]
                TOKENS.append(Tokens(REDTOKEN, pGameGrid[rowX][rowY], 'Hit', FIRETOKENIMAGELIST, EXPLOSIONIMAGELIST, None))
                gamelogic[rowX][rowY] = 'T'
                SHOTSOUND.play()
                HITSOUND.play()
                self.moves.remove((rowX, rowY))
                self.turn = False
        return self.turn


    def generateMoves(self, coords, grid, lstDir=None):
        x, y = coords
        nx, ny = 0, 0
        for direction in ['North', 'South', 'East', 'West']:
            if direction == 'North' and lstDir != 'North':
                nx = x - 1
                ny = y
                if not (nx > 9 or ny > 9 or nx < 0 or ny < 0):
                    if (nx, ny) not in self.moves and grid[nx][ny] == 'O':
                        self.moves.append((nx, ny))
                        self.generateMoves((nx, ny), grid, 'South')

            if direction == 'South' and lstDir != 'South':
                nx = x + 1
                ny = y
                if not (nx > 9 or ny > 9 or nx < 0 or ny < 0):
                    if (nx, ny) not in self.moves and grid[nx][ny] == 'O':
                        self.moves.append((nx, ny))
                        self.generateMoves((nx, ny), grid, 'North')

            if direction == 'East' and lstDir != 'East':
                nx = x
                ny = y + 1
                if not (nx > 9 or ny > 9 or nx < 0 or ny < 0):
                    if (nx, ny) not in self.moves and grid[nx][ny] == 'O':
                        self.moves.append((nx, ny))
                        self.generateMoves((nx, ny), grid, 'West')

            if direction == 'West' and lstDir != 'West':
                nx = x
                ny = y - 1
                if not (nx > 9 or ny > 9 or nx < 0 or ny < 0):
                    if (nx, ny) not in self.moves and grid[nx][ny] == 'O':
                        self.moves.append((nx, ny))
                        self.generateMoves((nx, ny), grid, 'East')

        return


class Tokens:
    def __init__(self, image, pos, action, imageList=None, explosionList=None, soundFile=None):
        self.image = image
        self.rect = self.image.get_rect()
        self.pos = pos
        self.rect.topleft = self.pos
        self.imageList = imageList
        self.explosionList = explosionList
        self.action = action
        self.soundFile = soundFile
        self.timer = pygame.time.get_ticks()
        self.imageIndex = 0
        self.explosionIndex = 0
        self.explosion = False


    def animate_Explosion(self):
        """Animating the Explosion sequence"""
        self.explosionIndex += 1
        if self.explosionIndex < len(self.explosionList):
            return self.explosionList[self.explosionIndex]
        else:
            return self.animate_fire()


    def animate_fire(self):
        """Animate the Fire sequence"""
        if pygame.time.get_ticks() - self.timer >= 100:
            self.timer = pygame.time.get_ticks()
            self.imageIndex += 1
        if self.imageIndex < len(self.imageList):
            return self.imageList[self.imageIndex]
        else:
            self.imageIndex = 0
            return self.imageList[self.imageIndex]


    def draw(self, window):
        """Draws the tokens to the screen"""
        if not self.imageList:
            window.blit(self.image, self.rect)
        else:
            self.image = self.animate_Explosion()
            self.rect = self.image.get_rect(topleft=self.pos)
            self.rect[1] = self.pos[1] - 10
            window.blit(self.image, self.rect)


#  Game Utility Functions
def createGameGrid(rows, cols, cellsize, pos):
    """Creates a game grid with coordinates for each cell"""
    startX = pos[0]
    startY = pos[1]
    coordGrid = []
    for row in range(rows):
        rowX = []
        for col in range(cols):
            rowX.append((startX, startY))
            startX += cellsize
        coordGrid.append(rowX)
        startX = pos[0]
        startY += cellsize
    return coordGrid


def createGameLogic(rows, cols):
    """Updates the game grid with logic, ie - spaces and X for ships"""
    gamelogic = []
    for row in range(rows):
        rowX = []
        for col in range(cols):
            rowX.append(' ')
        gamelogic.append(rowX)
    return gamelogic


def updateGameLogic(coordGrid, shiplist, gamelogic):
    """Updates the game grid with the position of the ships"""
    for i, rowX in enumerate(coordGrid):
        for j, colX in enumerate(rowX):
            if gamelogic[i][j] == 'T' or gamelogic[i][j] == 'X':
                continue
            else:
                gamelogic[i][j] = ' '
                for ship in shiplist:
                    if pygame.rect.Rect(colX[0], colX[1], CELLSIZE, CELLSIZE).colliderect(ship.rect):
                        gamelogic[i][j] = 'O'


def showGridOnScreen(window, cellsize, playerGrid, computerGrid):
    """Draws the player and computer grids to the screen"""
    gamegrids = [playerGrid, computerGrid]
    for grid in gamegrids:
        for row in grid:
            for col in row:
                pygame.draw.rect(window, (255, 255, 255), (col[0], col[1], cellsize, cellsize), 1)


def printGameLogic():
    """prints to the terminal the game logic"""
    print('Player Grid'.center(CELLSIZE, '#'))
    for _ in pGameLogic:
        print(_)
    print('Computer Grid'.center(CELLSIZE, '#'))
    for _ in cGameLogic:
        print(_)


def loadImage(path, size, rotate=False):
    """A function to import the images into memory"""
    img = pygame.image.load(path).convert_alpha()
    img = pygame.transform.scale(img, size)
    if rotate == True:
        img = pygame.transform.rotate(img, -90)
    return img


def loadAnimationImages(path, aniNum,  size):
    """Load in stipulated number of images to memory"""
    imageList = []
    for num in range(aniNum):
        if num < 10:
            imageList.append(loadImage(f'{path}00{num}.png', size))
        elif num < 100:
            imageList.append(loadImage(f'{path}0{num}.png', size))
        else:
            imageList.append(loadImage(f'{path}{num}.png', size))
    return imageList


def loadSpriteSheetImages(spriteSheet, rows, cols, newSize, size):
    image = pygame.Surface((128, 128))
    image.blit(spriteSheet, (0, 0), (rows * size[0], cols * size[1], size[0], size[1]))
    image = pygame.transform.scale(image, (newSize[0], newSize[1]))
    image.set_colorkey((0, 0, 0))
    return image


def increaseAnimationImage(imageList, ind):
    return imageList[ind]


def createFleet():
    """Creates the fleet of ships"""
    fleet = []
    for name in FLEET.keys():
        fleet.append(
            Ship(name,
                 FLEET[name][1],
                 FLEET[name][2],
                 FLEET[name][3])
        )
    return fleet


def sortFleet(ship, shiplist):
    """Rearranges the list of ships"""
    shiplist.remove(ship)
    shiplist.append(ship)


def randomizeShipPositions(shiplist, gamegrid):
    """Select random locations on the game grid for the battleships ensuring no ships are adjacent."""
    placedShips = []
    for ship in shiplist:
        validPosition = False
        while not validPosition:
            # Сброс корабля в начальное положение
            ship.returnToDefaultPosition()            
            # Случайный выбор ориентации и позиции
            rotateShip = random.choice([True, False])
            if rotateShip:
                yAxis = random.randint(0, len(gamegrid) - 1)
                xAxis = random.randint(0, len(gamegrid[0]) - (ship.hImage.get_width() // CELLSIZE))
                ship.rotateShip(True)
                ship.rect.topleft = gamegrid[yAxis][xAxis]
            else:
                yAxis = random.randint(0, len(gamegrid) - (ship.vImage.get_height() // CELLSIZE))
                xAxis = random.randint(0, len(gamegrid[0]) - 1)
                ship.rect.topleft = gamegrid[yAxis][xAxis]

            # Проверка столкновений и минимального расстояния
            if not checkBufferZoneCollisions(ship, placedShips):
                validPosition = True
        placedShips.append(ship)

def checkBufferZoneCollisions(ship, shiplist):
    """Check if a ship is too close to any other ships, including adjacent cells."""
    for other_ship in shiplist:
        # Создаем буферную зону вокруг другого корабля
        buffer_zone = pygame.Rect(
            other_ship.rect.left - CELLSIZE,
            other_ship.rect.top - CELLSIZE,
            other_ship.rect.width + 2 * CELLSIZE,
            other_ship.rect.height + 2 * CELLSIZE
        )
        # Проверяем пересечение с буферной зоной
        if buffer_zone.colliderect(ship.rect):
            return True
    return False


def deploymentPhase(deployment):
    if deployment == True:
        return False
    else:
        return True


def takeTurns(p1, p2):
    if p1.turn == True:
        p2.turn = False
    else:
        p2.turn = True
        if not p2.makeAttack(pGameLogic):
            p1.turn = True


def checkForWinners(grid):
    validGame = True
    for row in grid:
        if 'O' in row:
            validGame = False
    return validGame


def shipLabelMaker(msg):
    """Makes the ship labels to display on the screen"""
    textMessage = pygame.font.SysFont('Stencil', 22)
    textMessage = textMessage.render(msg, 1, (0, 17, 167))
    textMessage = pygame.transform.rotate(textMessage, 90)
    return textMessage


def mainMenuScreen(window):
    window.fill((0, 0, 0))
    window.blit(MAINMENUIMAGE, (0, 0))

    for button in BUTTONS:
        if button.name in ['Easy Computer', 'Hard Computer']:
            button.active = True
            button.draw(window)
        else:
            button.active = False


def deploymentScreen(window):
    window.fill((255, 255, 255))
    window.blit(PGAMEGRIDIMG, (CELLSIZE*3, 110))
    window.blit(CGAMEGRIDIMG, (SCREENWIDTH - (ROWS * CELLSIZE) - CELLSIZE*4, 110))

    #  Draws the player and computer grids to the screen
    # showGridOnScreen(window, CELLSIZE, pGameGrid, cGameGrid)

    #  Draw ships to screen
    for ship in pFleet:
        ship.draw(window)
        ship.snapToGridEdge(pGameGrid)
        ship.snapToGrid(pGameGrid)

    for ship in cFleet:
        # ship.draw(window)
        ship.snapToGridEdge(cGameGrid)
        ship.snapToGrid(cGameGrid)

    for button in BUTTONS:
        if button.name in ['Случайная', 'Сбросить', 'Играть', 'Выйти', 'Сохранить', 'Загрузить']:
            button.active = True
            button.draw(window)
        else:
            button.active = False

    computer.draw(window)

    for token in TOKENS:
        token.draw(window)

    updateGameLogic(pGameGrid, pFleet, pGameLogic)
    updateGameLogic(cGameGrid, cFleet, cGameLogic)


def endScreen(window):
    window.fill((0, 0, 0))

    window.blit(ENDSCREENIMAGE, (0, 0))

    for button in BUTTONS:
        if button.name in ['Easy Computer', 'Hard Computer', 'Quit']:
            button.active = True
            button.draw(window)
        else:
            button.active = False


def updateGameScreen(window, GAMESTATE):
    if GAMESTATE == 'Main Menu':
        mainMenuScreen(window)
    elif GAMESTATE == 'Deployment':
        deploymentScreen(window)
    elif GAMESTATE == 'Game Over':
        endScreen(window)

    pygame.display.update()


#  Game Settings and Variables
SCREENWIDTH = 1000
SCREENHEIGHT = 650
ROWS = 10
COLS = 10
CELLSIZE = 30
DEPLOYMENT = True
SCANNER = False
INDNUM = 0
BLIPPOSITION = None
TURNTIMER = pygame.time.get_ticks()
GAMESTATE = 'Main Menu'


#  Colors


#  Pygame Display Initialization
GAMESCREEN = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))
pygame.display.set_caption('Battle Ship')


#  Game Lists/Dictionaries
FLEET = {
    'four': ['four', 'assets/images/ships/four.png', (CELLSIZE*4, 470), (CELLSIZE, CELLSIZE*4)],
    'three1': ['three1', 'assets/images/ships/three.png', (CELLSIZE*6, 470), (CELLSIZE, CELLSIZE*3)],
    'three2': ['three2', 'assets/images/ships/three.png', (CELLSIZE*6, 470), (CELLSIZE, CELLSIZE*3)],
    'two1': ['two1', 'assets/images/ships/two.png', (CELLSIZE*8, 470), (CELLSIZE, CELLSIZE*2)],
    'two2': ['two2', 'assets/images/ships/two.png', (CELLSIZE*8, 470), (CELLSIZE, CELLSIZE*2)],
    'two3': ['two3', 'assets/images/ships/two.png', (CELLSIZE*8, 470), (CELLSIZE, CELLSIZE*2)],
    'one1': ['one1', 'assets/images/ships/one.png', (CELLSIZE*10, 470), (CELLSIZE, CELLSIZE)],
    'one2': ['one2', 'assets/images/ships/one.png', (CELLSIZE*10, 470), (CELLSIZE, CELLSIZE)],
    'one3': ['one3', 'assets/images/ships/one.png', (CELLSIZE*10, 470), (CELLSIZE, CELLSIZE)],
    'one4': ['one4', 'assets/images/ships/one.png', (CELLSIZE*10, 470), (CELLSIZE, CELLSIZE)],
}
STAGE = ['Main Menu', 'Deployment', 'Game Over']

#  Loading Game Variables
pGameGrid = createGameGrid(ROWS, COLS, CELLSIZE, (CELLSIZE*4, 110 + CELLSIZE))
# pGameGrid = createGameGrid(ROWS, COLS, CELLSIZE, (CELLSIZE, CELLSIZE))
pGameLogic = createGameLogic(ROWS, COLS)
pFleet = createFleet()

cGameGrid = createGameGrid(ROWS, COLS, CELLSIZE, (SCREENWIDTH - (ROWS * CELLSIZE) - CELLSIZE*3, 110 + CELLSIZE))
# cGameGrid = createGameGrid(ROWS, COLS, CELLSIZE, (SCREENWIDTH - (ROWS * CELLSIZE), CELLSIZE))
cGameLogic = createGameLogic(ROWS, COLS)
cFleet = createFleet()
randomizeShipPositions(cFleet, cGameGrid)

printGameLogic()


#  Loading Game Sounds and Images
MAINMENUIMAGE = loadImage('assets/images/background/Battleship.jpg', (SCREENWIDTH // 3 * 2, SCREENHEIGHT))
ENDSCREENIMAGE = loadImage('assets/images/background/Carrier.jpg', (SCREENWIDTH, SCREENHEIGHT))
# BACKGROUND = loadImage('assets/images/background/gamebg.png', (SCREENWIDTH, SCREENHEIGHT))
PGAMEGRIDIMG = loadImage('assets/images/grids/grid.png', ((ROWS + 1) * CELLSIZE, (COLS + 1) * CELLSIZE))
CGAMEGRIDIMG = loadImage('assets/images/grids/grid.png', ((ROWS + 1) * CELLSIZE, (COLS + 1) * CELLSIZE))
BUTTONIMAGE = loadImage('assets/images/buttons/button.png', (90, 30))
BUTTONIMAGE1 = loadImage('assets/images/buttons/button.png', (200, 60))
BUTTONS = [
    Button(BUTTONIMAGE, (90, 30), (500, 500), 'Случайная'),
    Button(BUTTONIMAGE, (90, 30), (600, 500), 'Сбросить'),
    Button(BUTTONIMAGE, (90, 30), (700, 500), 'Играть'),
    Button(BUTTONIMAGE, (90, 30), (500, 550), 'Сохранить'),
    Button(BUTTONIMAGE, (90, 30), (600, 550), 'Загрузить'),
    Button(BUTTONIMAGE1, (250, 100), (700, SCREENHEIGHT // 2 - 150), 'Easy Computer'),
    Button(BUTTONIMAGE1, (250, 100), (700, SCREENHEIGHT // 2 + 150), 'Hard Computer')
]
REDTOKEN = loadImage('assets/images/tokens/redtoken.png', (CELLSIZE, CELLSIZE))
GREENTOKEN = loadImage('assets/images/tokens/greentoken.png', (CELLSIZE, CELLSIZE))
BLUETOKEN = loadImage('assets/images/tokens/bluetoken.png', (CELLSIZE, CELLSIZE))
FIRETOKENIMAGELIST = loadAnimationImages('assets/images/tokens/fireloop/fire1_ ', 13, (CELLSIZE, CELLSIZE))
EXPLOSIONSPRITESHEET = pygame.image.load('assets/images/tokens/explosion/explosion.png').convert_alpha()
EXPLOSIONIMAGELIST = []
for row in range(8):
    for col in range(8):
        EXPLOSIONIMAGELIST.append(loadSpriteSheetImages(EXPLOSIONSPRITESHEET, col, row, (CELLSIZE, CELLSIZE), (128, 128)))
TOKENS = []
HITSOUND = pygame.mixer.Sound('assets/sounds/explosion.wav')
HITSOUND.set_volume(0.05)
SHOTSOUND = pygame.mixer.Sound('assets/sounds/gunshot.wav')
SHOTSOUND.set_volume(0.05)
MISSSOUND = pygame.mixer.Sound('assets/sounds/splash.wav')
MISSSOUND.set_volume(0.05)



#  Initialise Players
player1 = Player()
computer = EasyComputer()

# #  Main Game Loop
RUNGAME = True
while RUNGAME:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            RUNGAME = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if DEPLOYMENT == True:
                    # Обработка расстановки кораблей
                    for ship in pFleet:
                        if ship.rect.collidepoint(pygame.mouse.get_pos()):
                            ship.active = True
                            sortFleet(ship, pFleet)
                            ship.selectShipAndMove()
                else:
                    if  player1.turn:
                        # Игрок атакует до промаха
                        hit = player1.makeAttack(cGameGrid, cGameLogic)
                        if not hit:  # Промах
                            player1.turn = False
                            TURNTIMER = pygame.time.get_ticks()
                            computer.turn = True

                for button in BUTTONS:
                    if button.rect.collidepoint(pygame.mouse.get_pos()):
                        if button.name == 'Играть' and button.active == True:
                            status = deploymentPhase(DEPLOYMENT)
                            DEPLOYMENT = status
                        # elif button.name == 'Redeploy' and button.active == True:
                        #     status = deploymentPhase(DEPLOYMENT)
                        #     DEPLOYMENT = status
                        elif button.name == 'Выйти' and button.active == True:
                            RUNGAME = False
                        elif (button.name == 'Easy Computer' or button.name == 'Hard Computer') and button.active == True:
                            if button.name == 'Easy Computer':
                                computer = EasyComputer()

                            elif button.name == 'Hard Computer':
                                computer = HardComputer()
                            if GAMESTATE == 'Game Over':
                                TOKENS.clear()
                                for ship in pFleet:
                                    ship.returnToDefaultPosition()
                                randomizeShipPositions(cFleet, cGameGrid)
                                pGameLogic = createGameLogic(ROWS, COLS)
                                updateGameLogic(pGameGrid, pFleet, pGameLogic)
                                cGameLogic = createGameLogic(ROWS, COLS)
                                updateGameLogic(cGameGrid, cFleet, cGameLogic)
                                status = deploymentPhase(DEPLOYMENT)
                                DEPLOYMENT = status
                            GAMESTATE = STAGE[1]
                        button.actionOnPress()


            elif event.button == 2:
                printGameLogic()


            elif event.button == 3:
                if DEPLOYMENT == True:
                    for ship in pFleet:
                        if ship.rect.collidepoint(pygame.mouse.get_pos()) and not ship.checkForRotateCollisions(pFleet):
                            ship.rotateShip(True)

    if computer.turn and not player1.turn:
        hit = computer.makeAttack(pGameLogic)
        if not hit:  # Промах
            computer.turn = False
            player1.turn = True
    

    updateGameScreen(GAMESCREEN, GAMESTATE)
    if SCANNER == True:
        INDNUM += 1

    if GAMESTATE == 'Deployment' and DEPLOYMENT != True:
        player1Wins = checkForWinners(cGameLogic)
        computerWins = checkForWinners(pGameLogic)
        if player1Wins == True or computerWins == True:
            GAMESTATE = STAGE[2]



    takeTurns(player1, computer)

pygame.quit()
