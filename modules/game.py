import pygame
from pygame.locals import *
import pygame.surfarray

import random
import math
import array
import zlib

import track
import menu
import misc

import sys
import os
import datetime

class Game:
  '''Class representing a game: Tournament or Single Race'''

  def __init__(self, gameType, listTrackName=None, listPlayer=None, maxLapNb=-1):
    '''Constructor'''

    self.gameType = gameType
    self.listTrackName = listTrackName
    self.listPlayer = listPlayer
    self.maxLapNb = maxLapNb

  def play(self):

    if self.gameType == None or self.listTrackName == None or self.listPlayer == None or self.maxLapNb == -1:
      print("Incomplete game")
      return

    # For each track
    for currentTrackName in self.listTrackName:
      try:
        currentTrack = track.Track(currentTrackName[0], currentTrackName[1])
      except:
        print("Cannot load track : ")
        sys.exit(1)

      # Play music
      misc.startRandomMusic()

      # Put players on the rank
      # If it's the first time do Randomly
      if currentTrackName == self.listTrackName[0]:
        listRank = []
        for play in self.listPlayer:
          rank = -1
          while rank in listRank or rank == -1:
            rank = random.randint(1, len(self.listPlayer))
          listRank.append(rank)
          play.play(currentTrack, rank)
      # Else do the inv of the last Race
      else:
        for play in self.listPlayer:
          play.play(currentTrack, len(self.listPlayer) - play.rank + 1)

      # Initialise clock
      clock = pygame.time.Clock()


      # Display player names and cars blinking...
      for i in range(0, 4):

        # Display the track
        misc.screen.blit(currentTrack.track, (0, 0))

        # Display the player names
        for play in self.listPlayer:
          text = misc.popUpFont.render(play.name, 1, misc.lightColor, (0, 0, 0))
          textRect = text.get_rect()
          textRect.centerx = play.car.x
          textRect.centery = play.car.y
          misc.screen.blit(text, textRect)

        pygame.display.flip() 
        pygame.time.delay(400)

        # Display the track
        misc.screen.blit(currentTrack.track, (0, 0))

        # Display the cars
        for play in self.listPlayer:
          play.car.image=play.car.cars[int((256.0*play.car.angle/2.0/math.pi)%256)]
          play.car.sprite.draw(misc.screen)

        pygame.display.flip() 
        pygame.time.delay(400)

      i = 0

      l = []

      popUp = misc.PopUp(currentTrack)

      raceFinish = 0

      masterChrono = 0

      replayArray = array.array("h")

      # bestRank is an array indexed by the lap number
      # It's used to indicate the Position of each player at each track Finish
      bestRank = [None]
      for r in range(1, self.maxLapNb+1):
        bestRank.append(1)

      # Display Fires
      imgFireG = pygame.transform.rotozoom(pygame.image.load(os.path.join("sprites", "grey.png")).convert_alpha(), 0, misc.zoom)
      misc.screen.blit(imgFireG, (10*misc.zoom,10*misc.zoom))
      misc.screen.blit(imgFireG, (90*misc.zoom,10*misc.zoom))
      misc.screen.blit(imgFireG, (170*misc.zoom,10*misc.zoom))
      pygame.display.flip()
      pygame.time.delay(1000)
      imgFire = pygame.transform.rotozoom(pygame.image.load(os.path.join("sprites", "red.png")).convert_alpha(), 0, misc.zoom)
      misc.screen.blit(imgFire, (10*misc.zoom,10*misc.zoom))
      #misc.screen.blit(imgFire, (90*misc.zoom,10*misc.zoom))
      #misc.screen.blit(imgFire, (170*misc.zoom,10*misc.zoom))
      pygame.display.flip()
      pygame.time.delay(1000)
      imgFire = pygame.transform.rotozoom(pygame.image.load(os.path.join("sprites", "red.png")).convert_alpha(), 0, misc.zoom)
      #misc.screen.blit(imgFire, (10*misc.zoom,10*misc.zoom))
      misc.screen.blit(imgFire, (90*misc.zoom,10*misc.zoom))
      #misc.screen.blit(imgFire, (170*misc.zoom,10*misc.zoom))
      pygame.display.flip()
      pygame.time.delay(1000)
      imgFire = pygame.transform.rotozoom(pygame.image.load(os.path.join("sprites", "red.png")).convert_alpha(), 0, misc.zoom)
      #misc.screen.blit(imgFireG, (10*misc.zoom,10*misc.zoom))
      #misc.screen.blit(imgFireG, (90*misc.zoom,10*misc.zoom))
      misc.screen.blit(imgFire, (170*misc.zoom,10*misc.zoom))
      pygame.display.flip()
      pygame.time.delay(990)

      # Clear event queue
      pygame.event.clear()

      # Display the track
      misc.screen.blit(currentTrack.track, (0, 0))

      pygame.display.flip()  

      sec = datetime.datetime.now().second
      nbFrame = 0

      # Event loop
      while raceFinish == 0:

        # Get the event keys
        for event in pygame.event.get():

          if event.type == QUIT:
            # Stop music
            misc.stopMusic()
            sys.exit(0)
          elif event.type == KEYDOWN:
            if event.key == K_ESCAPE:
              # Stop music
              misc.stopMusic()
              return -1
            for play in self.listPlayer:
              if play.__class__.__name__ == "HumanPlayer":
                if event.key == play.keyAccel:
                  play.keyAccelPressed = 1
                if event.key == play.keyBrake:
                  play.keyBrakePressed = 1
                if event.key == play.keyLeft:
                  play.keyLeftPressed = 1
                if event.key == play.keyRight:
                  play.keyRightPressed = 1
          elif event.type == KEYUP:
            for play in self.listPlayer:
              if play.__class__.__name__ == "HumanPlayer":
                if event.key == play.keyAccel:
                  play.keyAccelPressed = 0
                if event.key == play.keyBrake:
                  play.keyBrakePressed = 0
                if event.key == play.keyLeft:
                  play.keyLeftPressed = 0
                if event.key == play.keyRight:
                  play.keyRightPressed = 0

        # Make some modifications on the car commands
        for play in self.listPlayer:

          # Bot players need to compute
          if play.__class__.__name__ == "RobotPlayer":
            play.compute()

          if play.__class__.__name__ == "HumanPlayer" or play.__class__.__name__ == "RobotPlayer":
            if play.keyAccelPressed == 1:
              play.car.doAccel()
            else:
              play.car.noAccel()
            if play.keyBrakePressed == 1:
              play.car.doBrake()
            else:
              play.car.noBrake()
            if play.keyLeftPressed == 1:
              play.car.doLeft()
            if play.keyRightPressed == 1:
              play.car.doRight()
            if play.keyLeftPressed == 0 and play.keyRightPressed == 0:
              play.car.noWheel()

        # TODO ? Manage Rect.union (oldRect and newRect of a car) to optimize !!!!
        # Append the old rect to the dirty Rects
        for play in self.listPlayer:
          oldRect = play.car.rect
          l.append(oldRect.__copy__())
          misc.screen.blit(currentTrack.track, play.car.rect, play.car.rect)

        # For each player, update positions and check checkpoints
        for play in self.listPlayer:
          play.car.update()

          play.chrono = play.chrono + 1

          # Get infos on trackFunction
          color=currentTrack.trackF.get_at((int(play.car.x), int(play.car.y)))
          r=color[0]
          #b=color[2]

          # Manage the checkpoints to count the nb of laps
          if currentTrack.reverse == 0 and play.raceFinish == 0:
            if r == play.lastCheckpoint + 16:
              play.lastCheckpoint = r

            # We finish a lap
            elif r == 16:
              # OK
              if play.lastCheckpoint == 16 * currentTrack.nbCheckpoint:
                play.lastCheckpoint = r
                play.nbLap = play.nbLap +1

                # Get the current rank (position)
                play.rank = bestRank[play.nbLap]
                bestRank[play.nbLap] = bestRank[play.nbLap] + 1

                # Get the best chrono   
                if play.chrono < play.bestChrono:
                  play.bestChrono = play.chrono
                  popUp.addElement(play.car, play.name + " L" + str(play.nbLap) + " P" + str(play.rank) + " " + misc.chrono2Str(play.chrono) + "B")
                else:
                  popUp.addElement(play.car, play.name + " L" + str(play.nbLap) + " P" + str(play.rank) + " " + misc.chrono2Str(play.chrono))

                play.chrono = 0

              # NOK
              elif play.lastCheckpoint > 16:
                play.lastCheckpoint = r
                popUp.addElement(play.car, play.name + " L" + str(play.nbLap+1) + " MISSED")
                play.chrono = 0

          elif currentTrack.reverse == 1 and play.raceFinish == 0:
            if r != 0 and r == play.lastCheckpoint - 16:
              play.lastCheckpoint = r
              #print "Checkpoint OK"
            # We finish a lap
            elif r == 16 * currentTrack.nbCheckpoint:
              # OK
              if play.lastCheckpoint == 16:
                play.lastCheckpoint = r
                play.nbLap = play.nbLap +1

                # Get the current rank (position)
                play.rank = bestRank[play.nbLap]
                bestRank[play.nbLap] = bestRank[play.nbLap] + 1

                # Get the best chrono   
                if play.chrono < play.bestChrono:
                  play.bestChrono = play.chrono
                  popUp.addElement(play.car, play.name + " L" + str(play.nbLap) + " P" + str(play.rank) + " " + misc.chrono2Str(play.chrono) + "B")
                else:
                  popUp.addElement(play.car, play.name + " L" + str(play.nbLap) + " P" + str(play.rank) + " " + misc.chrono2Str(play.chrono))

                play.chrono = 0

              # NOK
              elif play.lastCheckpoint < 16 * currentTrack.nbCheckpoint:
                play.lastCheckpoint = r
                popUp.addElement(play.car, play.name + " L" + str(play.nbLap+1) + " MISSED")
                play.chrono = 0

        # Manage Collisions
        for play in self.listPlayer:
         for play2 in self.listPlayer:
           if play == play2:
             continue
           playCollisionRects = []
           play2CollisionRects = []
           listIndex = pygame.Rect(play.car.listCarRect[0]).collidelistall(play2.car.listCarRect)
           if listIndex != []:
             playCollisionRects.append(0)
             for idx in listIndex:
               if idx not in play2CollisionRects:
                 play2CollisionRects.append(idx)
           listIndex = pygame.Rect(play.car.listCarRect[1]).collidelistall(play2.car.listCarRect)
           if listIndex != []:
             playCollisionRects.append(1)
             for idx in listIndex:
               if idx not in play2CollisionRects:
                 play2CollisionRects.append(idx)
           listIndex = pygame.Rect(play.car.listCarRect[2]).collidelistall(play2.car.listCarRect)
           if listIndex != []:
             playCollisionRects.append(2)
             for idx in listIndex:
               if idx not in play2CollisionRects:
                 play2CollisionRects.append(idx)
           listIndex = pygame.Rect(play.car.listCarRect[3]).collidelistall(play2.car.listCarRect)
           if listIndex != []:
             playCollisionRects.append(3)
             for idx in listIndex:
               if idx not in play2CollisionRects:
                 play2CollisionRects.append(idx)

           playCollisionRects.sort()
           play2CollisionRects.sort()
           if playCollisionRects == [0]:
             play.car.newSpeed = play.car.speed/2 - abs(play2.car.speed/2)
           elif playCollisionRects == [1]:
             play.car.newSpeed = play.car.speed/2 + abs(play2.car.speed/2)
           elif playCollisionRects == [2] or playCollisionRects == [0,1,2] or playCollisionRects == [0,2] or playCollisionRects == [1,2]:
             play.car.speedL = play.car.speedL + abs(play2.car.speed/2)*10
             play.car.newSpeed = 0
           elif playCollisionRects == [3] or playCollisionRects == [0,1,3] or playCollisionRects == [0,3] or playCollisionRects == [1,3]:
             play.car.speedL = play.car.speedL - abs(play2.car.speed/2)*10
             play.car.newSpeed = 0
           elif playCollisionRects != [] :
             #TODO
             #print "Strange Collision !!!"
             #print playCollisionRects
             play.car.newSpeed = 0
        
        for play in self.listPlayer:
          if play.car.newSpeed != 0:
            play.car.speed = play.car.newSpeed
            play.car.newSpeed = 0

        # Display PopUp
        popUp.display()
        l.append(popUp.rect.__copy__())

        raceFinish = 1

        currentTrack.track.lock()
        # Display and manage finished game
        for play in self.listPlayer:

          # Change the car sprite
          if play.car.brake == 0:
            play.car.image=play.car.cars[int((256.0*play.car.angle/2.0/math.pi)%256)].copy()
          else:
            play.car.image=play.car.cars2[int((256.0*play.car.angle/2.0/math.pi)%256)].copy()

          # If there's something on the car (the car is in a tunnel), manage mask to hide the car
          part=pygame.Surface((play.car.sizeRect,play.car.sizeRect), HWSURFACE, 24).convert()
          part.blit(currentTrack.trackF, (0,0), (play.car.x-play.car.sizeRect/2, play.car.y-play.car.sizeRect/2, play.car.sizeRect, play.car.sizeRect))
          partArray = pygame.surfarray.array2d(part)
          aX = 0
          for arrayX in partArray:
            aY = 0
            for col in arrayX:
              if col % 256 != 0:
                play.car.image.set_at((aX, aY), (255, 255, 255, 0))
              aY = aY + 1
            aX = aX + 1

          # Display tires slide
          if play.car.slide == 1 or play.car.slide == 2:
            coordN = (play.car.x - math.cos(play.car.angle)*play.car.height*0.4, play.car.y - math.sin(play.car.angle)*play.car.height*0.4)
            coordS = (play.car.x + math.cos(play.car.angle)*play.car.height*0.4, play.car.y + math.sin(play.car.angle)*play.car.height*0.4)
            coord0 = (int(coordN[0] - math.sin(play.car.angle)*play.car.width*0.3), int(coordN[1] + math.cos(play.car.angle)*play.car.width*0.3))
            coord1 = (int(coordN[0] + math.sin(play.car.angle)*play.car.width*0.3), int(coordN[1] - math.cos(play.car.angle)*play.car.width*0.3))
            coord2 = (int(coordS[0] - math.sin(play.car.angle)*play.car.width*0.3), int(coordS[1] + math.cos(play.car.angle)*play.car.width*0.3))
            coord3 = (int(coordS[0] + math.sin(play.car.angle)*play.car.width*0.3), int(coordS[1] - math.cos(play.car.angle)*play.car.width*0.3))
            oldCoordN = (play.car.ox - math.cos(play.car.oldAngle)*play.car.height*0.4, play.car.oy - math.sin(play.car.oldAngle)*play.car.height*0.4)
            oldCoordS = (play.car.ox + math.cos(play.car.oldAngle)*play.car.height*0.4, play.car.oy + math.sin(play.car.oldAngle)*play.car.height*0.4)
            oldCoord0 = (int(oldCoordN[0] - math.sin(play.car.oldAngle)*play.car.width*0.3), int(oldCoordN[1] + math.cos(play.car.oldAngle)*play.car.width*0.3))
            oldCoord1 = (int(oldCoordN[0] + math.sin(play.car.oldAngle)*play.car.width*0.3), int(oldCoordN[1] - math.cos(play.car.oldAngle)*play.car.width*0.3))
            oldCoord2 = (int(oldCoordS[0] - math.sin(play.car.oldAngle)*play.car.width*0.3), int(oldCoordS[1] + math.cos(play.car.oldAngle)*play.car.width*0.3))
            oldCoord3 = (int(oldCoordS[0] + math.sin(play.car.oldAngle)*play.car.width*0.3), int(oldCoordS[1] - math.cos(play.car.oldAngle)*play.car.width*0.3))

            # Back tires
            if currentTrack.trackF.get_at(coord2)[2] != 255 and currentTrack.trackF.get_at(oldCoord2)[2] != 255:
              pygame.draw.line(currentTrack.track, (0,0,0), coord2, oldCoord2)
            if currentTrack.trackF.get_at(coord3)[2] != 255 and currentTrack.trackF.get_at(oldCoord3)[2] != 255:
              pygame.draw.line(currentTrack.track, (0,0,0), coord3, oldCoord3)

            # Also Front tires if it's a braking slide
            if play.car.slide == 2:
              if currentTrack.trackF.get_at(coord0)[2] != 255 and currentTrack.trackF.get_at(oldCoord0)[2] != 255:
                pygame.draw.line(currentTrack.track, (0,0,0), coord0, oldCoord0)
              if currentTrack.trackF.get_at(coord1)[2] != 255 and currentTrack.trackF.get_at(oldCoord1)[2] != 255:
                pygame.draw.line(currentTrack.track, (0,0,0), coord1, oldCoord1)


          # Test if the player has finished
          if play.nbLap == self.maxLapNb and play.raceFinish != 1:
            play.raceFinish = 1
            play.car.blink = 1

          # Test is somebody has not finished
          if play.nbLap != self.maxLapNb:
            raceFinish = 0

          # Blink = 0, no blink
          if play.car.blink == 0:
            newRect = play.car.rect
            l.append(newRect.__copy__())
            play.car.sprite.draw(misc.screen)

          # Blink = 1, fast blink indicating the end of the race
          if play.car.blink == 1 and play.car.blinkCount < 10:
            play.car.blinkCount = play.car.blinkCount + 1
            newRect = play.car.rect
            l.append(newRect.__copy__())

            # Display the car
            play.car.sprite.draw(misc.screen)

          elif play.car.blink == 1 and play.car.blinkCount >= 10:
            play.car.blinkCount = play.car.blinkCount +1

          if play.car.blink == 1 and play.car.blinkCount == 20:
            play.car.blinkCount = 0

        currentTrack.track.unlock()

        if i == 1:
          # Compute the FPS
          sec2 = datetime.datetime.now().second
          if sec2 > sec or (sec == 59 and sec2 > 0):
            fps = nbFrame
            nbFrame = 1
            sec = sec2
            text = misc.popUpFont.render(str(fps), 1, misc.lightColor, (0, 0, 0))
            textRect = text.get_rect()
            textRect.x = 0
            textRect.y = 0
            misc.screen.blit(text, textRect)
            l.append(textRect.__copy__())
          else:
            nbFrame = nbFrame + 1

          pygame.display.update(l)
          i=0
          l = []
        else:
          i=i+1

        masterChrono = masterChrono + 1


        # Make sure game doesn't run at more than 100 frames per second
        clock.tick(100)

      # Display the last PopUp
      popUp.display()
      l.append(popUp.rect.__copy__())
      
      text = pygame.transform.rotozoom(misc.bigFont.render("Race finish, press a key to continue", 1, misc.lightColor), 20, 1)
      textRect = text.get_rect()
      textRect.centerx = misc.screen.get_rect().centerx
      textRect.centery = misc.screen.get_rect().centery
      misc.screen.blit(text, textRect)

      pygame.display.flip()

      misc.wait4Key()

      self.computeScores(currentTrack)

      # Stop music
      misc.stopMusic()

    if self.gameType == "tournament":
      self.displayFinalScores()

    # If it's a challenge there's only 1 player, and return bestChrono
    if self.gameType == "challenge":
      return self.listPlayer[0].bestChrono


  def computeScores(self, track):

    titleMenu = menu.SimpleTitleOnlyMenu(misc.titleFont, "raceResult")

    y = titleMenu.startY
    for play in self.listPlayer:

      # If it's a tournament, compute points
      if self.gameType == "tournament":
        # Give points
        if play.rank == 1:
          morePoint = 10
        elif play.rank == 2:
          morePoint = 6
        elif play.rank == 3:
          morePoint = 4
        elif play.rank == 4:
          morePoint = 3
        elif play.rank == 5:
          morePoint = 2
        elif play.rank == 6:
          morePoint = 1
        else:
          morePoint = 0

      # Test if the current player has the best chrono
      bestChrono = 1
      for play2 in self.listPlayer:
        if play.bestChrono > play2.bestChrono:
          bestChrono = 0
          break

      playCar = pygame.transform.rotozoom(pygame.image.load(os.path.join("sprites", "cars", "car" + str(play.car.color) + ".png")).convert_alpha(), 270, 1.2*misc.zoom)

      # If it's a tournament, compute points
      if self.gameType == "tournament":
        if bestChrono == 1:
          if misc.addHiScore(track, play) == 1:
            text = misc.titleFont.render(str(play.rank) + "' " + play.name + " :  " + str(play.point) + " + " + str(morePoint) + " + 2 = " + str(play.point+morePoint+2) + "  >> " + misc.chrono2Str(play.bestChrono) + " << HiScore !", 1, misc.lightColor)
          else:
            text = misc.titleFont.render(str(play.rank) + "' " + play.name + " :  " + str(play.point) + " + " + str(morePoint) + " + 2 = " + str(play.point+morePoint+2) + "  >> " + misc.chrono2Str(play.bestChrono) + " <<", 1, misc.lightColor)
          play.point = play.point + morePoint + 2

        else:
          text = misc.titleFont.render(str(play.rank) + "' " + play.name + " :  " + str(play.point) + " + " + str(morePoint) + " = " + str(play.point+morePoint) + "     " + misc.chrono2Str(play.bestChrono), 1, misc.darkColor)
          play.point = play.point + morePoint

      else:

        if bestChrono == 1:
          if misc.addHiScore(track, play) == 1:
            text = misc.titleFont.render(str(play.rank) + "' " + play.name + " : >> " + misc.chrono2Str(play.bestChrono) + " << HiScore !", 1, misc.lightColor)
          else:
            text = misc.titleFont.render(str(play.rank) + "' " + play.name + " : >> " + misc.chrono2Str(play.bestChrono) + " <<", 1, misc.lightColor)
        else:
          text = misc.titleFont.render(str(play.rank) + "' " + play.name + " :    " + misc.chrono2Str(play.bestChrono), 1, misc.darkColor)

      # Display the car with statistics
      playCarRect = playCar.get_rect()
      textRect = text.get_rect()
      textRect.centerx = misc.screen.get_rect().centerx + (playCarRect.width + 20*misc.zoom) /2
      textRect.y = y + 80*misc.zoom*play.rank
      playCarRect.x = textRect.x - (playCarRect.width + 20*misc.zoom)
      playCarRect.centery = textRect.centery
      misc.screen.blit(playCar, playCarRect)
      misc.screen.blit(text, textRect)

    pygame.display.flip()
    
    misc.wait4Key()

  def displayFinalScores(self):

    titleMenu = menu.SimpleTitleOnlyMenu(misc.titleFont, "finalResult")

    y = titleMenu.startY
    for play in self.listPlayer:

      # Get the final rank
      self.rank = 1
      for play2 in self.listPlayer:
        if play.point < play2.point:
          self.rank = self.rank + 1

      playCar = pygame.transform.rotozoom(pygame.image.load(os.path.join("sprites", "cars", "car" + str(play.car.color) + ".png")).convert_alpha(), 270, 1.2*misc.zoom)

      if self.rank == 1:
        text = misc.titleFont.render(str(play.rank) + "' " + play.name + " :  >> " + str(play.point) + " <<", 1, misc.lightColor)
      else:
        text = misc.titleFont.render(str(play.rank) + "' " + play.name + " : " + str(play.point), 1, misc.darkColor)

      # Display the car with statistics
      playCarRect = playCar.get_rect()
      textRect = text.get_rect()
      textRect.centerx = misc.screen.get_rect().centerx + (playCarRect.width + 20*misc.zoom) /2
      textRect.y = y + 80*misc.zoom*play.rank
      playCarRect.x = textRect.x - (playCarRect.width + 20*misc.zoom)
      playCarRect.centery = textRect.centery
      misc.screen.blit(playCar, playCarRect)
      misc.screen.blit(text, textRect)

    pygame.display.flip()
    
    misc.wait4Key()
