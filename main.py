#  Module Imports
import pygame
import random


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
        """switch ship between vertical and horizontal"""
        if self.active or doRotation == True:
            if self.rotation == False:
                self.rotation = True
            else:
                self.rotation = False
            self.switchImageAndRect()


    def switchImageAndRect(self):
        """Switches from Horizontal to Vertical and vice versa"""
        if self.rotation == True:
            self.image = self.hImage
            self.rect = self.hImageRect
        else:
            self.image = self.vImage
            self.rect = self.vImageRect
        self.hImageRect.center = self.vImageRect.center = self.rect.center


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
        """Check to make sure the ship is not going to collide with any other ship before rotating"""
        slist = shiplist.copy()
        slist.remove(self)
        # Предполагаемое новое положение после поворота
        new_rect = self.hImageRect if not self.rotation else self.vImageRect
        for ship in slist:
            # Проверка прямого столкновения
            if new_rect.colliderect(ship.rect):
                return True
            
            # Проверка буферной зоны (расстояние 1 клетка)
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
            if self.rect.left > gridCoords[0][-1][0] + 50 or \
                self.rect.right < gridCoords[0][0][0] or \
                self.rect.top > gridCoords[-1][0][1] + 50 or \
                self.rect.bottom < gridCoords[0][0][1]:
                self.returnToDefaultPosition()

            elif self.rect.right > gridCoords[0][-1][0]+50:
                self.rect.right = gridCoords[0][-1][0] + 50
            elif self.rect.left < gridCoords[0][0][0]:
                self.rect.left = gridCoords[0][0][0]
            elif self.rect.top < gridCoords[0][0][1]:
                self.rect.top = gridCoords[0][0][1]
            elif self.rect.bottom > gridCoords[-1][0][1] + 50:
                self.rect.bottom = gridCoords[-1][0][1] + 50
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
        self.radarUsed = 0
        self.active = False

        self.msg = self.addText(msg)
        self.msgRect = self.msg.get_rect(center=self.rect.center)


    def addText(self, msg):
        """Add font to the button image"""
        font = pygame.font.SysFont('Stencil', 22)
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
            if self.name == 'Randomize':
                self.randomizeShipPositions(pFleet, pGameGrid)
                self.randomizeShipPositions(cFleet, cGameGrid)
            elif self.name == 'Reset':
                self.resetShips(pFleet)
            elif self.name == 'Deploy':
                self.deploymentPhase()
            elif self.name == 'Quit':
                pass
            elif self.name == 'Redeploy':
                self.restartTheGame()


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
        if self.name == 'Deploy' and gameStatus == False:
            self.name = 'Redeploy'
        elif self.name == 'Redeploy' and gameStatus == True:
            self.name = 'Deploy'
        if self.name == 'Reset' and gameStatus == False:
            self.name = 'Radar Scan'
        elif self.name == 'Radar Scan' and gameStatus == True:
            self.name = 'Reset'
        if self.name == 'Randomize' and gameStatus == False:
            self.name = 'Quit'
        elif self.name == 'Quit' and gameStatus == True:
            self.name = 'Randomize'
        self.msg = self.addText(self.name)
        self.msgRect = self.msg.get_rect(center=self.rect.center)


    def draw(self, window):
        self.updateButtons(DEPLOYMENT)
        self.focusOnButton(window)
        window.blit(self.msg, self.msgRect)


class Player:
    def __init__(self):
        self.turn = True

    def makeAttack(self, grid, logicgrid):
        """When its the player's turn, the player must make an attacking selection within the computer grid."""
        posX, posY = pygame.mouse.get_pos()
        if posX >= grid[0][0][0] and posX <= grid[0][-1][0] + 50 and posY >= grid[0][0][1] and posY <= grid[-1][0][1] + 50:
            for i, rowX in enumerate(grid):
                for j, colX in enumerate(rowX):
                    if posX >= colX[0] and posX < colX[0] + 50 and posY >= colX[1] and posY <= colX[1] + 50:
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
    print('Player Grid'.center(50, '#'))
    for _ in pGameLogic:
        print(_)
    print('Computer Grid'.center(50, '#'))
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


def pick_random_ship_location(gameLogic):
    validChoice = False
    while not validChoice:
        posX = random.randint(0, 9)
        posY = random.randint(0, 9)
        if gameLogic[posX][posY] == 'O':
            validChoice = True

    return (posX, posY)


def displayRadarScanner(imagelist, indnum, SCANNER):
    if SCANNER == True and indnum <= 359:
        image = increaseAnimationImage(imagelist, indnum)
        return image
    else:
        return False


def displayRadarBlip(num, position):
    if SCANNER:
        image = None
        if position[0] >= 5 and position[1] >= 5:
            if num >= 0 and num <= 90:
                image = increaseAnimationImage(RADARBLIPIMAGES, num // 10)
        elif position[0] < 5 and position[1] >= 5:
            if num > 270 and num <= 360:
                image = increaseAnimationImage(RADARBLIPIMAGES, (num // 4) // 10)
        elif position[0] < 5 and position[1] < 5:
            if num > 180 and num <= 270:
                image = increaseAnimationImage(RADARBLIPIMAGES, (num // 3) // 10)
        elif position[0] >= 5 and position[1] < 5:
            if num > 90 and num <= 180:
                image = increaseAnimationImage(RADARBLIPIMAGES, (num // 2) // 10)
        return image


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
    # window.blit(BACKGROUND, (0, 0))
    window.blit(PGAMEGRIDIMG, (0, 0))
    window.blit(CGAMEGRIDIMG, (cGameGrid[0][0][0] - 50, cGameGrid[0][0][1] - 50))

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
        if button.name in ['Randomize', 'Reset', 'Deploy', 'Quit', 'Radar Scan', 'Redeploy']:
            button.active = True
            button.draw(window)
        else:
            button.active = False

    computer.draw(window)

    radarScan = displayRadarScanner(RADARGRIDIMAGES, INDNUM, SCANNER)
    if not radarScan:
        pass
    else:
        window.blit(radarScan, (cGameGrid[0][0][0], cGameGrid[0][-1][1]))
        window.blit(RADARGRID, (cGameGrid[0][0][0], cGameGrid[0][-1][1]))

    RBlip = displayRadarBlip(INDNUM, BLIPPOSITION)
    if RBlip:
        window.blit(RBlip, (cGameGrid[BLIPPOSITION[0]][BLIPPOSITION[1]][0],
                            cGameGrid[BLIPPOSITION[0]][BLIPPOSITION[1]][1]))

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
SCREENWIDTH = 1260
SCREENHEIGHT = 800
ROWS = 10
COLS = 10
CELLSIZE = 50
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
    'four': ['four', 'assets/images/ships/four.png', (50, 570), (50, 200)],
    'three1': ['three1', 'assets/images/ships/three.png', (150, 570), (50, 150)],
    'three2': ['three2', 'assets/images/ships/three.png', (150, 570), (50, 150)],
    'two1': ['two1', 'assets/images/ships/two.png', (250, 570), (50, 100)],
    'two2': ['two2', 'assets/images/ships/two.png', (250, 570), (50, 100)],
    'two3': ['two3', 'assets/images/ships/two.png', (250, 570), (50, 100)],
    'one1': ['one1', 'assets/images/ships/one.png', (350, 570), (50, 50)],
    'one2': ['one2', 'assets/images/ships/one.png', (350, 570), (50, 50)],
    'one3': ['one3', 'assets/images/ships/one.png', (350, 570), (50, 50)],
    'one4': ['one4', 'assets/images/ships/one.png', (350, 570), (50, 50)],
}
STAGE = ['Main Menu', 'Deployment', 'Game Over']

#  Loading Game Variables
pGameGrid = createGameGrid(ROWS, COLS, CELLSIZE, (50, 50))
pGameLogic = createGameLogic(ROWS, COLS)
pFleet = createFleet()

cGameGrid = createGameGrid(ROWS, COLS, CELLSIZE, (SCREENWIDTH - (ROWS * CELLSIZE), 50))
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
BUTTONIMAGE = loadImage('assets/images/buttons/button.png', (150, 50))
BUTTONIMAGE1 = loadImage('assets/images/buttons/button.png', (250, 100))
BUTTONS = [
    Button(BUTTONIMAGE, (150, 50), (725, 700), 'Randomize'),
    Button(BUTTONIMAGE, (150, 50), (900, 700), 'Reset'),
    Button(BUTTONIMAGE, (150, 50), (1075, 700), 'Deploy'),
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
RADARGRIDIMAGES = loadAnimationImages('assets/images/radar_base/radar_anim', 360, (ROWS * CELLSIZE, COLS * CELLSIZE))
RADARBLIPIMAGES = loadAnimationImages('assets/images/radar_blip/Blip_', 11, (50, 50))
RADARGRID = loadImage('assets/images/grids/grid_faint.png', ((ROWS) * CELLSIZE, (COLS) * CELLSIZE))
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
                        if button.name == 'Deploy' and button.active == True:
                            status = deploymentPhase(DEPLOYMENT)
                            DEPLOYMENT = status
                        elif button.name == 'Redeploy' and button.active == True:
                            status = deploymentPhase(DEPLOYMENT)
                            DEPLOYMENT = status
                        elif button.name == 'Quit' and button.active == True:
                            RUNGAME = False
                        elif button.name == 'Radar Scan' and button.active == True:
                            SCANNER = True
                            INDNUM = 0
                            BLIPPOSITION = pick_random_ship_location(cGameLogic)
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
