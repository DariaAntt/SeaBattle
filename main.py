#  Module Imports
import os
import sys
import webbrowser
import pygame
import random
import json
from tkinter import Tk, filedialog
from pygame.locals import *


#  Module Initialization
pygame.init()



# ------------------------------------------------------------------------------------------------------
# ------------------------------------- Корабль ----------------------------------
# ------------------------------------------------------------------------------------------------------
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
        # Indicates whether the ship is placed on the grid
        self.placed = False


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
                            self.placed = True  # Mark the ship as placed
                    if event.button == 3:
                        self.rotateShip()
    def isPlaced(self):
        """Check if the ship has been placed on the grid"""
        return self.placed

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
        #pygame.draw.rect(window, ERROR_COLOR, self.rect, 1)



# ------------------------------------------------------------------------------------------------------
# ------------------------------------- Кнопки ----------------------------------
# ------------------------------------------------------------------------------------------------------
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
        font = pygame.font.SysFont('Arial', 18, bold=True)
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
            elif self.name == 'Берега':                
                self.resetShips(pFleet)
                updateGameLogic(pGameGrid, pFleet, pGameLogic)
                
                self.shoresShipPositions(pFleet, pGameGrid)
                self.randomizeShipPositions(cFleet, cGameGrid)
            elif self.name == 'Сбросить':
                self.resetShips(pFleet)
            elif self.name == 'Играть':
                self.deploymentPhase()
            elif self.name == 'Сохранить в файл':
                save_fleet_to_file(pFleet)
            elif self.name == 'Загрузить из файла':
                load_fleet_from_file(pFleet)
            elif self.name == 'Выйти':
                pass


    def randomizeShipPositions(self, shiplist, gameGrid):
        """Calls the randomize ships function"""
        if DEPLOYMENT == True:
            randomizeShipPositions(shiplist, gameGrid)

    def shoresShipPositions(self, shiplist, gameGrid):
        """Calls the randomize ships function"""
        if DEPLOYMENT == True:
            shoresShipPositions(shiplist, gameGrid)

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
        if self.name == 'Случайная' and gameStatus == False:
            self.name = ''
        if self.name == 'Берега' and gameStatus == False:
            self.name = ''
        if self.name == 'Сохранить в файл' and gameStatus == False:
            self.name = ''
        if self.name == 'Загрузить из файла' and gameStatus == False:
            self.name = ''
        # if self.name == 'Выйти' and gameStatus == True:
        #     self.name = 'Сбросить'
        self.msg = self.addText(self.name)
        self.msgRect = self.msg.get_rect(center=self.rect.center)


    def draw(self, window):
        self.updateButtons(DEPLOYMENT)
        self.focusOnButton(window)
        if self.name.find('null'):
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
    from tkinter.messagebox import showerror, askyesno
    from tkinter import Tk, filedialog
    """Открывает окно выбора файла и загружает расстановку кораблей."""
    root = Tk()
    root.withdraw()  # Скрыть главное окно Tkinter

    while True:
        filename = filedialog.askopenfilename(
            filetypes=[("Ship Battle files", "*.sb")],
            title="Загрузить расстановку кораблей"
        )

        if not filename:  # Если файл не выбран, выходим из функции
            print("Загрузка файла отменена.")
            return

        try:
            with open(filename, 'r') as f:
                data = json.load(f)  # Попытка загрузки JSON

            # Проверка структуры данных
            if not isinstance(data, dict):
                raise ValueError("Некорректный формат данных. Ожидался объект JSON с данными кораблей.")

            for ship in fleet:
                if ship.name in data:
                    ship_data = data[ship.name]
                    
                    # Проверка наличия обязательных полей
                    if "position" not in ship_data or "rotation" not in ship_data:
                        raise KeyError(f"У корабля '{ship.name}' отсутствуют обязательные данные: 'position' или 'rotation'.")

                    # Устанавливаем позицию
                    ship.rect.topleft = tuple(ship_data["position"])

                    # Устанавливаем ориентацию
                    if ship_data["rotation"] != ship.rotation:
                        ship.rotation = ship_data["rotation"]
                        ship.switchImageAndRect()

                    # Синхронизация прямоугольников
                    ship.hImageRect.topleft = ship.rect.topleft
                    ship.vImageRect.topleft = ship.rect.topleft

                    # Перемещаем изображение в правильное положение
                    ship.rect = ship.hImageRect if ship.rotation else ship.vImageRect
                    ship.rect.topleft = tuple(ship_data["position"])

                    # Отладка
                    print(f"Корабль '{ship.name}' загружен: позиция={ship.rect.topleft}, ориентация={'горизонтальная' if ship.rotation else 'вертикальная'}.")
                else:
                    # Если данные отсутствуют, возвращаем корабль в начальное положение
                    print(f"Корабль '{ship.name}' отсутствует в данных. Возвращён в начальное положение.")
                    ship.returnToDefaultPosition()
            
            # Если всё прошло успешно, выходим из цикла
            print("Данные успешно загружены.")
            return

        except FileNotFoundError:
            showerror("Ошибка", "Файл не найден.")            
            data = None
        except json.JSONDecodeError as e:
            showerror("Ошибка", f"Ошибка чтения JSON: {e}")       
            data = None
        except (KeyError, ValueError) as e:
            showerror("Ошибка", f"Ошибка в данных файла: {e}")       
            data = None
        except Exception as e:
            showerror("Ошибка", f"Произошла неизвестная ошибка: {e}")       
            data = None
        return

    # if filename:
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


# ------------------------------------------------------------------------------
# ---------------------------------- Игрок -------------------------------------
# ------------------------------------------------------------------------------
class Player:
    def __init__(self):
        self.turn = True
        self.login = ''
        self.avatar = ''

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


# ------------------------------------------------------------------------------------------------------
# ------------------------------------- Противник без добивания ----------------------------------
# ------------------------------------------------------------------------------------------------------
class EasyComputer:
    def __init__(self):
        self.turn = False
        self.status = self.computerStatus('Ход противника. Думает...')
        self.name = 'Легкий'


    def computerStatus(self, msg):
        image = pygame.font.SysFont('Arial', 24)
        message = image.render(msg, 1, (65, 105, 225))
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



# ------------------------------------------------------------------------------------------------------
# ------------------------------------- Противник с добиванием ----------------------------------
# ------------------------------------------------------------------------------------------------------
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
                    cur_Y = random.randint(0, 9)

                    if gamelogic[rowX][cur_Y] == ' ' or gamelogic[rowX][cur_Y] == 'O':
                        validChoice = True

                if gamelogic[rowX][cur_Y] == 'O':
                    TOKENS.append(
                        Tokens(REDTOKEN, pGameGrid[rowX][cur_Y], 'Hit', FIRETOKENIMAGELIST, EXPLOSIONIMAGELIST, None))
                    gamelogic[rowX][cur_Y] = 'T'
                    SHOTSOUND.play()
                    HITSOUND.play()
                    self.generateMoves((rowX, cur_Y), gamelogic)
                    # self.turn = False
                else:
                    gamelogic[rowX][cur_Y] = 'X'
                    TOKENS.append(Tokens(BLUETOKEN, pGameGrid[rowX][cur_Y], 'Miss', None, None, None))
                    SHOTSOUND.play()
                    MISSSOUND.play()
                    self.turn = False

        elif len(self.moves) > 0:
            COMPTURNTIMER = pygame.time.get_ticks()
            if COMPTURNTIMER - TURNTIMER >= 2000:
                rowX, cur_Y = self.moves[0]
                TOKENS.append(Tokens(REDTOKEN, pGameGrid[rowX][cur_Y], 'Hit', FIRETOKENIMAGELIST, EXPLOSIONIMAGELIST, None))
                gamelogic[rowX][cur_Y] = 'T'
                SHOTSOUND.play()
                HITSOUND.play()
                self.moves.remove((rowX, cur_Y))
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



# ------------------------------------------------------------------------------------------------------
# ------------------------------------- Противник с диагональной атакой ----------------------------------
# ------------------------------------------------------------------------------------------------------

class DiagonalComputer(EasyComputer): 
    def __init__(self):
        super().__init__()
        self.moves = []
        self.start_attack = True
        self.start_X = 0
        self.start_Y = 0

        self.cur_X = 0
        self.cur_Y = 0   

        self.free_X = [0,1,2,3,4,5,6,7,8,9]       
        self.free_Y = [0,1,2,3,4,5,6,7,8,9] 
        self.start_seria_X = 0
        self.start_seria_Y = 0
        self.step = random.randint(2, 4)
        self.step_back = False


    def makeAttack(self, gamelogic):
        if len(self.moves) == 0:
            COMPTURNTIMER = pygame.time.get_ticks()
            if COMPTURNTIMER - TURNTIMER >= 300:
                validChoice = False
                count = 0 
                while not validChoice: 
                    count += 1
                    if count > 5:
                        pygame.quit()
                        sys.exit()
                    
                    if self.start_attack:
                        self.start_X = random.randint(0, 9)
                        self.start_X = 3
                        self.step = 3

                        self.cur_X = self.start_X
                        self.start_seria_X = self.cur_X

                        self.cur_Y = 0
                        self.start_Y = self.cur_Y
                        self.start_seria_Y = self.cur_Y

                        self.start_attack = False

                    else:
                        self.cur_X += 1
                        if self.cur_X >= 10:
                            if not self.step_back:
                                self.start_X += self.step
                                if self.start_X >= 10:  
                                    self.start_X = self.start_seria_X
                                    self.start_Y = 0
                                    print('\n\tfor i in range(self.step):')
                                    for i in range(self.step):
                                        if self.start_X > 0: 
                                            self.start_X -= 1
                                            print(' self.start_X -= 1 = ' + str( self.start_X))
                                        else: 
                                            self.start_Y += 1
                                            print(' self.start_Y -= 1 = ' + str( self.start_Y))
                                        print('--------')
                                    self.cur_X = self.start_X
                                    self.cur_Y = self.start_Y                                  
                                    self.step_back = True
                                    print(f'self.step_back = {self.step_back}')

                                    # self.start_X = 0
                                    # self.cur_X = 0
                                    # self.cur_Y = self.step
                                    # self.start_Y = self.step
                                else: 
                                    self.cur_X = self.start_X
                                    self.cur_Y = 0 
                            else:
                                if self.start_X - self.step <= 0:
                                    self.start_Y = 0
                                    for i in range(self.step):
                                        if self.start_X > 0: 
                                            self.start_X -= 1
                                        else: 
                                            self.start_Y += 1
                                            self.step_back = True
                                    self.cur_X = self.start_X
                                    self.cur_Y = self.start_Y
                                else: 
                                    self.start_X -= self.step 
                                    self.cur_X = self.start_X
                                    self.start_Y = 0
                                    self.cur_Y = self.start_Y

                        # если по x мы не выходим за границу поля, то проверяем границу y, y++ 
                        else:     
                            self.cur_Y += 1
                            if self.cur_Y >= 10:     
                                self.start_Y += self.step
                                if self.start_Y >= 10:      
                                    if len(self.free_X) != 0:                    
                                        self.start_X = random.choice(self.free_X)
                                        self.start_seria_X = self.start_X
                                        self.cur_X = self.start_X
                                        self.start_Y = 0
                                        self.cur_Y = 0
                                    else:
                                        self.start_Y = random.choice(self.free_Y)
                                        self.start_seria_Y = self.start_Y
                                        self.cur_Y = self.start_Y
                                        self.start_X = 0
                                        self.cur_X = 0
                                else:
                                    self.cur_Y = self.start_Y
                                    self.cur_X = 0

                    if gamelogic[self.cur_Y][self.cur_X] == ' ' or gamelogic[self.cur_Y][self.cur_X] == 'O':
                        validChoice = True
                        if self.cur_Y == 0: self.free_X.remove(self.cur_X)
                        if self.cur_X == 0: self.free_Y.remove(self.cur_Y)

                if gamelogic[self.cur_Y][self.cur_X] == 'O':
                    TOKENS.append(
                        Tokens(REDTOKEN, pGameGrid[self.cur_Y][self.cur_X], 'Hit', FIRETOKENIMAGELIST, EXPLOSIONIMAGELIST, None))
                    gamelogic[self.cur_Y][self.cur_X] = 'T'
                    SHOTSOUND.play()
                    HITSOUND.play()
                    # self.generateMoves((self.cur_X, self.cur_Y), gamelogic)
                    # self.turn = False
                else:
                    gamelogic[self.cur_Y][self.cur_X] = 'X'
                    TOKENS.append(Tokens(BLUETOKEN, pGameGrid[self.cur_Y][self.cur_X], 'Miss', None, None, None))
                    SHOTSOUND.play()
                    MISSSOUND.play()
                    self.turn = False

        elif len(self.moves) > 0:
            print(f'self.moves  {self.moves}')
            COMPTURNTIMER = pygame.time.get_ticks()
            if COMPTURNTIMER - TURNTIMER >= 2000:
                self.cur_X, self.cur_Y = self.moves[0]
                TOKENS.append(Tokens(REDTOKEN, pGameGrid[self.cur_Y][self.cur_X], 'Hit', FIRETOKENIMAGELIST, EXPLOSIONIMAGELIST, None))
                gamelogic[self.cur_Y][self.cur_X] = 'T'
                SHOTSOUND.play()
                HITSOUND.play()
                self.moves.remove((self.cur_X, self.cur_Y))
                self.turn = False
        return self.turn


    def generateMoves(self, coords, grid, lstDir = None):
        x, y = coords
        nx, ny = 0, 0
        for direction in ['North', 'South', 'East', 'West']:
            if direction == 'North' and lstDir != 'North':
                nx = x
                ny = y + 1
                if not (nx > 9 or ny > 9 or nx < 0 or ny < 0):
                    if (nx, ny) not in self.moves and grid[nx][ny] == ' ':
                        self.moves.append((nx, ny))
                        self.generateMoves((nx, ny), grid, 'East')

            if direction == 'East' and lstDir != 'East':
                nx = x
                ny = y + 1
                if not (nx > 9 or ny > 9 or nx < 0 or ny < 0):
                    if (nx, ny) not in self.moves and grid[nx][ny] == ' ':
                        self.moves.append((nx, ny))
                        self.generateMoves((nx, ny), grid, 'South')

            if direction == 'South' and lstDir != 'South':
                nx = x + 1
                ny = y
                if not (nx > 9 or ny > 9 or nx < 0 or ny < 0):
                    if (nx, ny) not in self.moves and grid[nx][ny] == ' ':
                        self.moves.append((nx, ny))
                        self.generateMoves((nx, ny), grid, 'West')

            if direction == 'West' and lstDir != 'West':
                nx = x
                ny = y - 1
                if not (nx > 9 or ny > 9 or nx < 0 or ny < 0):
                    if (nx, ny) not in self.moves and grid[nx][ny] == ' ':
                        self.moves.append((nx, ny))
        return



# ------------------------------------------------------------------------------------------------------
# ------------------------------------- Анимации ----------------------------------
# ------------------------------------------------------------------------------------------------------
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


# ------------------------------------------------------------------------------------------------------
# ------------------------------------- Случайная расстановка ----------------------------------
# ------------------------------------------------------------------------------------------------------
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


# ------------------------------------------------------------------------------------------------------
# ------------------------------------- Расстановка Берега ----------------------------------
# ------------------------------------------------------------------------------------------------------
def shoresShipPositions(shiplist, gamegrid):
    placedShips = []

    # Создаём список всех клеток вдоль краёв игрового поля
    rows, cols = len(gamegrid), len(gamegrid[0])

    # Определяем клетки вдоль границ
    top_edge = [(0, col) for col in range(cols)]
    bottom_edge = [(rows - 1, col) for col in range(cols)]
    left_edge = [(row, 0) for row in range(1, rows - 1)]
    right_edge = [(row, cols - 1) for row in range(1, rows - 1)]

    # Все клетки на "берегу"
    coast_cells = top_edge + bottom_edge + left_edge + right_edge

    # Перемешиваем клетки для случайности
    random.shuffle(coast_cells)

    # Сортируем корабли по длине в убывающем порядке
    sorted_ships = sorted(
        [ship for ship in shiplist if max(ship.hImage.get_width(), ship.vImage.get_height()) > CELLSIZE],
        key=lambda s: max(s.hImage.get_width(), s.vImage.get_height()),
        reverse=True,
    )

    while True:  # Основной цикл расстановки (перезапускается при ошибке)
        success = True  # Флаг успешной расстановки

        random.shuffle(coast_cells)  # Перемешиваем клетки для случайности
        placedShips.clear()  # Сбрасываем список размещённых кораблей
        current_coast_cells = coast_cells[:]  # Копируем список клеток

        for ship in sorted_ships:
            ship.returnToDefaultPosition()
            validPosition = False
            i = 0  # Счётчик попыток для текущего корабля

            while not validPosition and i < 5:  # Пытаемся разместить корабль максимум 5 раз
                i += 1
                for cell in current_coast_cells:
                    row, col = cell
                    x, y = gamegrid[row][col]  # Получаем координаты из сетки

                    # Устанавливаем ориентацию корабля в зависимости от границы
                    if cell in top_edge:
                        ship.rotateShip(True)  # Горизонтальная ориентация
                    elif cell in bottom_edge:
                        ship.rotateShip(True)  # Горизонтальная ориентация
                    elif cell in left_edge:
                        ship.rotateShip(False)  # Вертикальная ориентация
                    elif cell in right_edge:
                        ship.rotateShip(False)  # Вертикальная ориентация

                    ship.rect.topleft = (x, y)

                    # Проверяем, вмещается ли корабль в этой ориентации
                    ship_width = ship.hImage.get_width() // CELLSIZE
                    ship_height = ship.vImage.get_height() // CELLSIZE
                    if ship.rotation:  # Горизонтальная ориентация
                        if col + ship_width > cols:
                            continue
                         # Проверяем все клетки корабля на границе
                        if not all((row, col + i) in coast_cells for i in range(ship_width)):
                            continue
                    else:  # Вертикальная ориентация
                        if row + ship_height > rows:
                            continue
                         # Проверяем все клетки корабля на границе
                        if not all((row + i, col) in coast_cells for i in range(ship_height)):
                            continue

                    # Проверяем на столкновения
                    if not checkBufferZoneCollisions(ship, placedShips):
                        placedShips.append(ship)
                        current_coast_cells = removeOccupiedCells(ship, current_coast_cells, gamegrid)
                        validPosition = True
                        break

                if validPosition:
                    break
                
            if not validPosition:  # Если корабль не удалось разместить
                success = False
                break
        if success:  # Если все многопалубные корабли размещены успешно
            break

    one_shiplist = list(filter(lambda x: not x.name.find('one'),shiplist))
    # Размещаем однопалубные корабли
    for ship in one_shiplist:
        validPosition = False
        while not validPosition:
            # Сброс корабля в начальное положение
            ship.returnToDefaultPosition()            
            # Случайный выбор ориентации и позиции
            yAxis = random.randint(0, len(gamegrid) - (ship.vImage.get_height() // CELLSIZE))
            xAxis = random.randint(0, len(gamegrid[0]) - 1)
            ship.rect.topleft = gamegrid[yAxis][xAxis]
            # Проверка столкновений и минимального расстояния
            if not checkBufferZoneCollisions(ship, placedShips):
                validPosition = True
        placedShips.append(ship)

def removeOccupiedCells(ship, coast_cells, gamegrid):
    """
    Удаляет клетки, занятые кораблем, и буферную зону вокруг него из списка доступных клеток "берега".
    """
    new_coast_cells = coast_cells[:]
    for cell in coast_cells:
        x, y = cell[1] * CELLSIZE, cell[0] * CELLSIZE
        cell_rect = pygame.Rect(x, y, CELLSIZE, CELLSIZE)
        buffer_zone = pygame.Rect(
            ship.rect.left - CELLSIZE, ship.rect.top - CELLSIZE,
            ship.rect.width + 2 * CELLSIZE, ship.rect.height + 2 * CELLSIZE
        )
        if buffer_zone.colliderect(cell_rect):
            new_coast_cells.remove(cell)

    return new_coast_cells


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


# -------------------------------------------------------------------------------------
# ------------------------------------- Экраны ----------------------------------------
# -------------------------------------------------------------------------------------

# ----------------------------------Начальный экран------------------------------
def startScreen(window):
    global GAMESTATE
    global PLAYER_WIN

    global PREV_GAMESTATE
    PREV_GAMESTATE = GAMESTATE
    
    PLAYER_WIN = False

    font = pygame.font.Font(None, 28)
    error_message = ""

    window.fill((255, 255, 255))
    window.blit(BACKGROUND, (0, 0))
    for button in BUTTONS:
        if button.name in ['Создать профиль', 'Начать игру', 'Руководство по приложению', 'Информация о разработчиках']:
            button.active = True
            button.draw(window)
        else:
            button.active = False
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEBUTTONDOWN:
                for button in BUTTONS:
                    if button.rect.collidepoint(pygame.mouse.get_pos()):
                        if button.name == 'Создать профиль' and button.active == True:
                            GAMESTATE = 'Registration'
                            return
                        elif button.name == 'Начать игру' and button.active == True:
                            if not player1.login or not player1.avatar:
                                error_message = "Чтобы начать игру, необходимо создать профиль."
                            else:
                                GAMESTATE = 'Main Menu'
                                return
                        elif button.name == 'Информация о разработчиках' and button.active == True:
                            GAMESTATE = 'Developers Info'
                            return
                        elif button.name == 'Руководство по приложению' and button.active == True:
                            # Получаем абсолютный путь к файлу system.html
                            file_path = os.path.abspath("system.html")
                            # Открываем файл в браузере
                            webbrowser.open(f"file://{file_path}")
        # Отображение сообщения об ошибке
        window.fill((255, 255, 255))  # Очистка экрана
        window.blit(BACKGROUND, (0, 0))
        for button in BUTTONS:
            if button.name in ['Создать профиль', 'Начать игру', 'Руководство по приложению', 'Информация о разработчиках']:
                button.draw(window)

        if error_message:
            error_surface = font.render(error_message, True, ERROR_COLOR)
            window.blit(error_surface, (SCREENWIDTH // 2 - error_surface.get_width() // 2, SCREENHEIGHT - 50))

        pygame.display.flip()
        pygame.time.Clock().tick(60)


# -----------------------------------Регистрация----------------------------------
def registrationScreen(window):
    window.fill((255, 255, 255))
    login = player1.login
    login_active = False
    error_message = ''  # Сообщение об ошибке
    create_error_message = ''
    error_font = pygame.font.Font(None, 24)

    radius = 100
    font = pygame.font.Font(None, 28)
    input_rect = pygame.Rect(SCREENWIDTH / 2 - 100, radius * 3 + 50, 200, 40)
    color_active = pygame.Color('#93BFCD')
    color_inactive = pygame.Color('black')
    color = color_inactive

    running = True
    while running:    
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEBUTTONDOWN:
                # Проверяем клик по полю ввода
                if input_rect.collidepoint(event.pos):
                    login_active = True
                    color = color_active
                else:
                    login_active = False
                    color = color_inactive

                for button in BUTTONS:
                    if button.rect.collidepoint(pygame.mouse.get_pos()):
                        if button.name == 'null_add' and button.active == True:
                            global GAMESTATE
                            GAMESTATE = STAGE[2]
                            return
                        if button.name == 'Сохранить профиль' and button.active == True:
                            if len(login) < 4 or len(login) > 10:
                                create_error_message = "Введите валидные данные"
                                print(create_error_message)
                            elif player1.avatar and player1.login:
                                create_error_message = ''
                                # global GAMESTATE
                                GAMESTATE = 'Start Menu'
                                print("Профиль создан")
                                return
                            elif (not player1.avatar) and (not player1.login):
                                create_error_message = "Выберите аватар и введите логин"
                                print(create_error_message)
                            elif not player1.avatar :
                                create_error_message = "Выберите аватар"
                                print(create_error_message)
                            elif not player1.login:
                                create_error_message = "Введите логин"
                                print(create_error_message)
                            # else:
                            #     create_error_message = ''
                            #     global GAMESTATE
                            #     GAMESTATE == 'Start Menu'
                            #     return

            elif event.type == pygame.KEYDOWN:
                if login_active:
                    if event.key == pygame.K_BACKSPACE:
                        login = login[:-1]
                    else:
                        if (len(login) < 10):
                            login += event.unicode
                    # Проверка длины логина и установка сообщения об ошибке
                if len(login) < 4:
                    error_message = "Логин слишком короткий (мин. 4 символа)"
                elif len(login) > 10:
                    error_message = "Логин слишком длинный (макс. 10 символов)"
                else:
                    error_message = ''

        player1.login = login

        # Отрисовка элементов
        window.fill((255, 255, 255))  # Очистка экрана
        pygame.draw.rect(window, color, input_rect, 2, 5)

        # Отрисовка аватара
        pygame.draw.circle(window, (214, 234, 240), (SCREENWIDTH // 2, radius * 2), radius)
        if player1.avatar:  # Если аватар выбран
            avatar_image = pygame.image.load(player1.avatar).convert_alpha()
            avatar_image = pygame.transform.scale(avatar_image, (radius * 2, radius * 2))

            # Создаем поверхность с маской круга
            avatar_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(avatar_surface, (255, 255, 255, 255), (radius, radius), radius)
            avatar_surface.blit(avatar_image, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

            # Рисуем результат на экране
            window.blit(avatar_surface, (SCREENWIDTH // 2 - radius, radius * 2 - radius))

        # Обновление текстовой поверхности
        text_surface = font.render(login, True, (0, 0, 0))
        window.blit(text_surface, (input_rect.x + 5, input_rect.y + 10))

        # Отображение сообщения об ошибке (если есть)
        if error_message:
            error_surface = error_font.render(error_message, True, ERROR_COLOR)
            window.blit(error_surface, (SCREENWIDTH/2 - error_surface.get_width()//2, input_rect.y + 50))
        if create_error_message:
            create_error_surface = error_font.render(create_error_message, True, ERROR_COLOR)
            window.blit(create_error_surface, (SCREENWIDTH/2 - create_error_surface.get_width()//2, SCREENHEIGHT - 50))


        for button in BUTTONS:
            if button.name in ['null_add', 'Сохранить профиль']:
                button.active = True
                button.draw(window)
            else:
                button.active = False
        pygame.display.flip()
        pygame.time.Clock().tick(60)


# -----------------------------------Выбор аватара--------------------------------
def selectAvatarScreen(window):
    global GAMESTATE  # Для изменения состояния игры и возвращения на экран регистрации

    # Настройки экрана
    window.fill((255, 255, 255))
    error_font = pygame.font.Font(None, 32)
    select_font = pygame.font.Font(None, 32)
    error = ''
    select_message = ''

    # Параметры аватаров
    size = 125
    avatar_size = (size, size)
    avatar_margin = 30
    row_count = 2
    avatar_folder = "assets/images/avatars"

    # Загрузка изображений аватаров
    avatar_paths = [f"{avatar_folder}/{img}" for img in sorted(os.listdir(avatar_folder))]
    avatars = [pygame.image.load(path).convert_alpha() for path in avatar_paths]
    avatars = [pygame.transform.scale(avatar, avatar_size) for avatar in avatars]

    # Расположение аватаров
    avatar_rects = []
    for i, avatar in enumerate(avatars):
        row = i // (len(avatars) // row_count)
        col = i % (len(avatars) // row_count)
        x = size + col * (avatar_size[0] + avatar_margin)
        y = size + row * (avatar_size[1] + avatar_margin)
        avatar_rects.append(pygame.Rect(x, y, *avatar_size))


    hovered_avatar_index = None
    selected_avatar_index = None
    running = True

    # Главный цикл
    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEMOTION:
                # Подсветка аватаров при наведении мыши
                hovered_avatar_index = None
                for i, rect in enumerate(avatar_rects):
                    if rect.collidepoint(event.pos):
                        hovered_avatar_index = i
                        break
                
            elif event.type == MOUSEBUTTONDOWN:
                # Проверка клика по аватару
                for i, rect in enumerate(avatar_rects):
                    if rect.collidepoint(event.pos):
                        selected_avatar_index = i
                        error = ''
                        select_message = 'Выбран аватар ' + str(i + 1)
                        break
                     
                for button in BUTTONS:
                    if button.rect.collidepoint(pygame.mouse.get_pos()):
                        if button.name == 'Выбрать' and button.active == True:
                            if selected_avatar_index is not None:
                                # Сохранение пути к аватару
                                player1.avatar = avatar_paths[selected_avatar_index]
                                global GAMESTATE
                                GAMESTATE = 'Registration'
                                return
                            else:
                                select_message = ''
                                error = 'Выберите аватар'

         # Отрисовка аватаров
        window.fill((255, 255, 255))  # Очистка экрана
        for i, avatar in enumerate(avatars):
            # Подсветка при наведении
            if hovered_avatar_index == i:
                pygame.draw.rect(window, MESSAGE_COLOR, avatar_rects[i], 5)  # Зеленая подсветка
            # Подсветка выбранного аватара
            elif selected_avatar_index == i:
                pygame.draw.rect(window, ERROR_COLOR, avatar_rects[i], 5)  # Красная рамка
            window.blit(avatar, avatar_rects[i].topleft)

        # Отображение сообщения об ошибке (если есть)
        if error:
            error_surface = error_font.render(error, True, ERROR_COLOR)
            window.blit(error_surface, (SCREENWIDTH/2 - error_surface.get_width()//2, 70))
        if select_message:
            select_surface = select_font.render( select_message, True, MESSAGE_COLOR)
            window.blit(select_surface, (SCREENWIDTH/2 - select_surface.get_width()//2, 70))


        # Отрисовка кнопки "Выбрать"
        for button in BUTTONS:
            if button.name in ['Выбрать']:
                button.active = True
                button.draw(window)
            else:
                button.active = False

        pygame.display.flip()
        pygame.time.Clock().tick(60)


# -----------------------------------Выбор уровня противника----------------------
def mainMenuScreen(window):
    window.fill((255, 255, 255))
    window.blit(BACKGROUND, (0, 0))

    font = pygame.font.Font(None, 38)
    message = "Выберите уровень противника:"
    message_surface = font.render(message, True, (0, 0, 0))
    window.blit(message_surface, (SCREENWIDTH // 2 - message_surface.get_width() // 2, 100))


    for button in BUTTONS:
        if button.name in ['Легкий', 'Средний', 'Сложный']:
            button.active = True
            button.draw(window)
        else:
            button.active = False


# -----------------------------------Игра-----------------------------------------
def deploymentScreen(window):
    window.fill((255, 255, 255))
    window.blit(PGAMEGRIDIMG, (CELLSIZE*3, 130))
    window.blit(CGAMEGRIDIMG, (SCREENWIDTH - (ROWS * CELLSIZE) - CELLSIZE*4, 130))

    # Отображаем аватар пользователя
    radius = 50
    avatar_image = pygame.image.load(player1.avatar).convert_alpha()
    avatar_image = pygame.transform.scale(avatar_image, (radius * 2, radius * 2))
    avatar_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
    pygame.draw.circle(avatar_surface, (255, 255, 255, 255), (radius, radius), radius)
    avatar_surface.blit(avatar_image, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    window.blit(avatar_surface, (CELLSIZE*7, 17))
    # Отображаем логин пользователя
    font = pygame.font.Font(None, 30)
    login_surface = font.render(player1.login, True, (70, 130, 180))
    window.blit(login_surface, (CELLSIZE*3, 130-login_surface.get_height()))

    # Отображаем компьютера
    radius = 50
    avatar_image = pygame.image.load('assets/images/avatar_comp.png').convert_alpha()
    avatar_image = pygame.transform.scale(avatar_image, (radius * 2, radius * 2))
    avatar_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
    pygame.draw.circle(avatar_surface, (255, 255, 255, 255), (radius, radius), radius)
    avatar_surface.blit(avatar_image, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    window.blit(avatar_surface, (SCREENWIDTH - CELLSIZE*10, 17))
    # Отображаем логин компьютера
    font = pygame.font.Font(None, 30)
    login_surface = font.render('computer', True, (70, 130, 180))
    window.blit(login_surface, (SCREENWIDTH - (ROWS * CELLSIZE) - CELLSIZE*4, 130-login_surface.get_height()))


    # # Функция проверки состояния расстановки кораблей
    # def checkFleetDeployment(fleet):
    #     if not fleet:
    #         return "расставьте корабли на игровом поле"
    #     for ship in fleet:
    #         if not ship.isPlaced():
    #             return "Завершите расстановку. Не все корабли расставлены."
    #     return None

    # # Проверяем состояние перед началом игры
    # error_message = checkFleetDeployment(pFleet)

    # # Отображаем сообщение об ошибке, если оно есть
    # if error_message:
    #     error_font = pygame.font.Font(None, 24)
    #     error_surface = error_font.render(error_message, True, (255, 0, 0))
    #     window.blit(error_surface, (CELLSIZE * 3, SCREENHEIGHT - error_surface.get_height() - 10))


    #  Draws the player and computer grids to the screen
    # showGridOnScreen(window, CELLSIZE, pGameGrid, cGameGrid)

    #  Draw ships to screen
    for ship in pFleet:
        ship.draw(window)
        ship.snapToGridEdge(pGameGrid)
        ship.snapToGrid(pGameGrid)

    for ship in cFleet:
        ship.draw(window)
        ship.snapToGridEdge(cGameGrid)
        ship.snapToGrid(cGameGrid)

    for button in BUTTONS:
        if DEPLOYMENT:
            if button.name in ['Случайная', 'Сбросить', 'Играть', 'Берега', 'Сохранить в файл', 'Загрузить из файла']:
                button.active = True
                # button.active = error_message is None and button.name == 'Играть' or button.name != 'Играть'
                button.draw(window)
            else:
                button.active = False
        else:
            if button.name == 'Выйти':
                button.active = True
                button.draw(window)
            else:
                button.active = False

    computer.draw(window)

    for token in TOKENS:
        token.draw(window)

    updateGameLogic(pGameGrid, pFleet, pGameLogic)
    updateGameLogic(cGameGrid, cFleet, cGameLogic)


# -----------------------------------Конец игры-----------------------------------
def endScreen(window):
    window.fill((255, 255, 255))
    error_font = pygame.font.Font(None, 84)
    error = 'Победил противник :('
    win_font = pygame.font.Font(None, 84)
    win = "Победа!"

    if PLAYER_WIN:
        window.blit(WIN_BACKGROUND, (0, 0))
        win_surface = win_font.render(win, True, MESSAGE_COLOR)
        window.blit(win_surface, (SCREENWIDTH/2 - win_surface.get_width()//2, 80))
    else:
        window.blit(LOSS_BACKGROUND, (0, 0))
        error_surface = error_font.render(error, True, ERROR_COLOR)
        window.blit(error_surface, (SCREENWIDTH/2 - error_surface.get_width()//2, 80))

    for button in BUTTONS:
        if button.name in ['Сыграть еще раз', ' Выйти ']:
            button.active = True
            button.draw(window)
        else:
            button.active = False


# -----------------------------------Сведения о разработчиках--------------------
def developersInfoScreen(window, game_stage):
    window.fill((255, 255, 255))  # Белый фон

    # Отображение заголовка
    title_font = pygame.font.SysFont('Arial', 28, bold=True)
    title = title_font.render("Информация о разработчиках", True, (0, 0, 0))
    window.blit(title, (SCREENWIDTH // 2 - title.get_width() // 2, 20))

    # Основной текст
    text_font = pygame.font.SysFont('Arial', 22)
    info = [
        "Самарский университет",
        "Кафедра программных систем",
        "",
        "Курсовой проект по дисциплине «Программная инженерия»",
        "Курсовой проект: «Игра «Морской бой»",
        "",
        "Разработчики обучающиеся группы 6402-020302D:",
        "                            Александрова Ольга Евгеньевна",
        "                                  Антипова Дарья Анатольевна",
        "                  Григорьева Анастасия Константиновна",
        "",
        "Руководитель:              Зеленко Лариса Сергеевна",
        "",
        "",
        "",
        "Самара, 2024"
    ]
    y_offset = 70
    for line in info:
        text = text_font.render(line, True, (0, 0, 0))
        window.blit(text, (SCREENWIDTH // 2 - text.get_width() // 2, y_offset))
        y_offset += 30

    # Обновление экрана
    pygame.display.flip()

    # Обработка событий
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                running = False
                global GAMESTATE
                GAMESTATE = game_stage
                return

                
# --------------------------------------------------------------------------------
# --------------------------------------------------------------------------------
# --------------------------------------------------------------------------------
               
def updateGameScreen(window, GAMESTATE):
    if GAMESTATE == 'Start Menu':
        startScreen(window)
    elif GAMESTATE == 'Registration':
        registrationScreen(window)
    elif GAMESTATE == 'Select Avatar':
        selectAvatarScreen(window)
    elif GAMESTATE == 'Main Menu':
        mainMenuScreen(window)
    elif GAMESTATE == 'Deployment':
        deploymentScreen(window)
    elif GAMESTATE == 'Game Over':
        endScreen(window)
    elif GAMESTATE == 'Developers Info':
        developersInfoScreen(window, PREV_GAMESTATE)
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
GAMESTATE = 'Start Menu'
PREV_GAMESTATE = ''
PLAYER_WIN = False

#  Colors
ERROR_COLOR = '#FF0000'
MESSAGE_COLOR = '#32CD32'


#  Pygame Display Initialization
GAMESCREEN = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))
pygame.display.set_caption('Battle Ship')


#  Game Lists/Dictionaries
FLEET = {
    'four': ['four', 'assets/images/ships/four.png', (CELLSIZE*4, 490), (CELLSIZE, CELLSIZE*4)],
    'three1': ['three1', 'assets/images/ships/three.png', (CELLSIZE*6, 490), (CELLSIZE, CELLSIZE*3)],
    'three2': ['three2', 'assets/images/ships/three.png', (CELLSIZE*6, 490), (CELLSIZE, CELLSIZE*3)],
    'two1': ['two1', 'assets/images/ships/two.png', (CELLSIZE*8, 490), (CELLSIZE, CELLSIZE*2)],
    'two2': ['two2', 'assets/images/ships/two.png', (CELLSIZE*8, 490), (CELLSIZE, CELLSIZE*2)],
    'two3': ['two3', 'assets/images/ships/two.png', (CELLSIZE*8, 490), (CELLSIZE, CELLSIZE*2)],
    'one1': ['one1', 'assets/images/ships/one.png', (CELLSIZE*10, 490), (CELLSIZE, CELLSIZE)],
    'one2': ['one2', 'assets/images/ships/one.png', (CELLSIZE*10, 490), (CELLSIZE, CELLSIZE)],
    'one3': ['one3', 'assets/images/ships/one.png', (CELLSIZE*10, 490), (CELLSIZE, CELLSIZE)],
    'one4': ['one4', 'assets/images/ships/one.png', (CELLSIZE*10, 490), (CELLSIZE, CELLSIZE)],
}
STAGE = ['Start Menu', 'Registration', 'Select Avatar','Main Menu', 'Deployment', 'Game Over', 'Developers Info']

#  Loading Game Variables
pGameGrid = createGameGrid(ROWS, COLS, CELLSIZE, (CELLSIZE*4, 130 + CELLSIZE))
pGameLogic = createGameLogic(ROWS, COLS)
pFleet = createFleet()

cGameGrid = createGameGrid(ROWS, COLS, CELLSIZE, (SCREENWIDTH - (ROWS * CELLSIZE) - CELLSIZE*3, 130 + CELLSIZE))
cGameLogic = createGameLogic(ROWS, COLS)
cFleet = createFleet()
randomizeShipPositions(cFleet, cGameGrid)

printGameLogic()


#  Loading Game Sounds and Images
MAINMENUIMAGE = loadImage('assets/images/background/Battleship.jpg', (SCREENWIDTH // 3 * 2, SCREENHEIGHT))
ENDSCREENIMAGE = loadImage('assets/images/background/Battleship.jpg', (SCREENWIDTH, SCREENHEIGHT))
BACKGROUND = loadImage('assets/images/background/bg1.png', (SCREENWIDTH, SCREENHEIGHT))
WIN_BACKGROUND = loadImage('assets/images/background/win_bg.png', (SCREENWIDTH, SCREENHEIGHT))
LOSS_BACKGROUND = loadImage('assets/images/background/loss_bg.png', (SCREENWIDTH, SCREENHEIGHT))


PGAMEGRIDIMG = loadImage('assets/images/grids/grid.png', ((ROWS + 1) * CELLSIZE, (COLS + 1) * CELLSIZE))
CGAMEGRIDIMG = loadImage('assets/images/grids/grid.png', ((ROWS + 1) * CELLSIZE, (COLS + 1) * CELLSIZE))
BUTTONIMAGE = loadImage('assets/images/buttons/button.png', (110, 40))
BUTTONIMAGE1 = loadImage('assets/images/buttons/button.png', (200, 50))
BUTTONIMAGEIINFO = loadImage('assets/images/buttons/button.png', (300, 50))
BUTTONADD = loadImage('assets/images/buttons/add_btn.png', (40, 40))
BUTTONPLAY = loadImage('assets/images/buttons/button_play.png', (110, 40))
BUTTONCLEAR = loadImage('assets/images/buttons/button_clear.png', (110, 40))
BUTTONFILE = loadImage('assets/images/buttons/button_file.png', (230, 40))



BUTTONS = [
    Button(BUTTONIMAGEIINFO, (300, 50), (20, 20), 'Руководство по приложению'),
    Button(BUTTONIMAGEIINFO, (300, 50), (SCREENWIDTH - 320, 20), 'Информация о разработчиках'),
    
    Button(BUTTONIMAGE1, (200, 50), (SCREENWIDTH/2 - 100, SCREENHEIGHT/2 - 80), 'Создать профиль'),
    Button(BUTTONIMAGE1, (200, 50), (SCREENWIDTH/2 - 100, SCREENHEIGHT/2 + 30), 'Начать игру'),

    
    Button(BUTTONIMAGE1, (200, 50), (SCREENWIDTH/2 - 100, SCREENHEIGHT - 150), 'Сохранить профиль'),
    Button(BUTTONADD, (40, 40), (SCREENWIDTH/2 + 50, 250), 'null_add'),
    Button(BUTTONIMAGE1, (200, 50), (SCREENWIDTH/2 - 100, SCREENHEIGHT - 150), 'Выбрать'),

    Button(BUTTONIMAGE, (110, 40), (570, 495), 'Случайная'),    
    Button(BUTTONIMAGE, (110, 40), (690, 495), 'Берега'),
    Button(BUTTONCLEAR, (110, 40), (810, 495), 'Сбросить'),
    Button(BUTTONFILE, (230, 40), (570, 545), 'Сохранить в файл'),
    Button(BUTTONFILE, (230, 40), (570, 595), 'Загрузить из файла'),
    Button(BUTTONPLAY, (110, 40), (810, 545), 'Играть'),
    Button(BUTTONIMAGE, (110, 40), (SCREENWIDTH/2 - 55, SCREENHEIGHT - 70), 'Выйти'),

    Button(BUTTONIMAGE1, (200, 50), (SCREENWIDTH/2 - 100, SCREENHEIGHT/2 - 80), 'Сыграть еще раз'),
    Button(BUTTONIMAGE1, (200, 50), (SCREENWIDTH/2 - 100, SCREENHEIGHT/2 + 30), ' Выйти '),

    Button(BUTTONIMAGE1, (200, 50), (SCREENWIDTH/2 - 100, SCREENHEIGHT/2 - 95), 'Легкий'),
    Button(BUTTONIMAGE1, (200, 50), (SCREENWIDTH/2 - 100, SCREENHEIGHT/2 - 25), 'Средний'),
    Button(BUTTONIMAGE1, (200, 50), (SCREENWIDTH/2 - 100, SCREENHEIGHT/2 + 45), 'Сложный')
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
computer.login = 'computer'

# #  Main Game Loop
login = ''
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
                        if button.name == 'Создать профиль' and button.active == True:
                            GAMESTATE = STAGE[1]
                        # elif button.name == 'null_add' and button.active == True:
                        #     GAMESTATE = STAGE[2]
                        elif button.name == 'Информация о разработчиках' and button.active == True:
                            GAMESTATE = 'Developers Info'
                        elif button.name == 'Начать игру' and button.active == True:
                            GAMESTATE = STAGE[3]
                        elif button.name == 'Играть' and button.active == True:
                            status = deploymentPhase(DEPLOYMENT)
                            DEPLOYMENT = status
                        elif button.name == 'Выйти' and button.active == True:
                            TOKENS.clear()
                            PLAYER_WIN = False
                            for ship in pFleet:
                                ship.returnToDefaultPosition()
                            randomizeShipPositions(cFleet, cGameGrid)
                            pGameLogic = createGameLogic(ROWS, COLS)
                            updateGameLogic(pGameGrid, pFleet, pGameLogic)
                            cGameLogic = createGameLogic(ROWS, COLS)
                            updateGameLogic(cGameGrid, cFleet, cGameLogic)
                            status = deploymentPhase(DEPLOYMENT)
                            DEPLOYMENT = status
                            GAMESTATE = STAGE[0]

                        elif button.name == 'Сыграть еще раз' and button.active == True:
                            TOKENS.clear()
                            PLAYER_WIN = False
                            for ship in pFleet:
                                ship.returnToDefaultPosition()
                            randomizeShipPositions(cFleet, cGameGrid)
                            pGameLogic = createGameLogic(ROWS, COLS)
                            updateGameLogic(pGameGrid, pFleet, pGameLogic)
                            cGameLogic = createGameLogic(ROWS, COLS)
                            updateGameLogic(cGameGrid, cFleet, cGameLogic)
                            status = deploymentPhase(DEPLOYMENT)
                            DEPLOYMENT = status
                            GAMESTATE = STAGE[0]

                        elif (button.name == 'Легкий' or button.name == 'Средний' or button.name == 'Сложный') and button.active == True:
                            if button.name == 'Легкий':
                                computer = EasyComputer()
                            elif button.name == 'Средний' and button.active:
                                square_size = 3     # Размер стороны квадрата (можно варьировать)
                                board_size = ROWS   # Предполагается, что поле квадратное
                                computer = DiagonalComputer()
                            elif button.name == 'Сложный':
                                computer = EasyComputer()

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
                            GAMESTATE = 'Deployment'

                        elif button.name == ' Выйти ' and button.active == True:
                            RUNGAME = False

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
            if player1Wins == True:
                PLAYER_WIN = True
            GAMESTATE = STAGE[5]



    takeTurns(player1, computer)

pygame.quit()
