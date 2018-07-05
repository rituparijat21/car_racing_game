import pygame
from pygame.locals import *

import random
import os
import sys
import configparser
import hashlib

VERSION = "0.1"

lightColor = (230, 230, 255)
darkColor = (100, 101, 151)

background = None
screen = None

popUpFont = None
titleFont = None
itemFont = None
smallItemFont = None
bigFont = None

music = 1

zoom = 1

def init():
  global popUpFont
  global titleFont
  global itemFont
  global smallItemFont
  global bigFont
  global background

  try:
    popUpFont = pygame.font.Font(os.path.join("fonts", "batman", "batmfo__.TTF"), int(24*zoom))
    titleFont = pygame.font.Font(os.path.join("fonts", "batman", "batmfo__.TTF"), int(52*zoom))
    itemFont = pygame.font.Font(os.path.join("fonts", "transformers", "Transformers_Movie.TTF"), int(34*zoom))
    smallItemFont = pygame.font.Font(os.path.join("fonts", "transformers", "Transformers_Movie.TTF"), int(30*zoom))
    bigFont = pygame.font.Font(os.path.join("fonts", "transformers", "Transformers_Movie.TTF"), int(66*zoom))
  except:
    print("Cannot initialize fonts:")
    sys.exit(-1)

  background = pygame.transform.scale(pygame.image.load(os.path.join("sprites", "background.jpg")).convert(), (int(1024*zoom), int(768*zoom)))

def chrono2Str(chrono):
  return str(chrono/100.0).replace(".", "''")

def wait4Key():
  # Clear event queue
  pygame.event.clear()

  # Wait for key Input
  ok = 0
  while ok == 0:
    for event in pygame.event.get():
      if event.type == QUIT:
        sys.exit(0)
      if event.type == KEYDOWN:
        ok = 1
        break

  # Clear event queue
  pygame.event.clear()  

def startRandomMusic():
  global music

  stopMusic()

  if music == 1:
    # Randomly choose the Music among .ogg files
    musics = []
    listFiles = os.listdir("musics")
    for fileMusic in listFiles:
      if fileMusic.endswith(".ogg") or fileMusic.endswith(".OGG"):
        musics.append(fileMusic)

    if len(musics) > 0:
      rand = random.randint(0, len(musics)-1)
      try:
        pygame.mixer.music.load(os.path.join("musics", musics[rand]))
        pygame.mixer.music.play()
      except:
        print("Music: %s unable to play..." % musics[rand])


def stopMusic():
  pygame.mixer.music.fadeout(1000)

class PopUp:
  def __init__(self, track):
    self.track = track
    self.listElement = []
    self.rect = pygame.Rect(0, 688*zoom, 260*zoom, 80*zoom)

  def addElement(self, car, text):
    self.listElement.append([car, text, 0])

  def display(self):

    #Erase PopUp Area
    screen.blit(self.track.track, self.rect, self.rect)
        
    #If useful, display PopUp Area
    if self.listElement!= []:

      y = 750*zoom

      for elem in self.listElement:
        x = 0
        carMini = elem[0].miniCar
        carMiniRect = carMini.get_rect()
        carMiniRect.x = x
        x = x + carMiniRect.width

        text = popUpFont.render(elem[1], 1, lightColor, (0, 0, 0))
        textRect = text.get_rect()
        textRect.x = x
        textRect.y = y
        screen.blit(text, textRect)

        carMiniRect.centery = textRect.centery 
        screen.blit(carMini, carMiniRect)

        # Remove an old element
        if elem[2] == 400:
          self.listElement.remove(elem)
        else:
          elem[2] = elem[2] + 1
        y = y - textRect.height

def addHiScore(track, player):
  fileExist = 1

  confFile=configparser.ConfigParser()
  try:
    confFile.readfp(open(".Speedlust.conf", "r"))
  except Exception:
    fileExist = 0
  
  # If the track is not represented, create it
  if fileExist == 0 or not confFile.has_section("hi " + track.name):
    fwrite = open(".Speedlust.conf", "w+")
    confFile.add_section("hi " + track.name)
    confFile.write(fwrite)
    confFile.readfp(open(".Speedlust.conf", "r"))

  # For the Inverse
  if track.reverse == 0:
    level = player.level
  else:
    level = -player.level

  # If the Level is not represented create it and put the Hi-scores
  if not confFile.has_option("hi " + track.name, "level" + str(level)):
    h = hashlib.new(str(track.name))
    h.update(str("level" + str(level)))
    h.update(player.name)
    h.update(str(player.bestChrono))
    fwrite = open(".Speedlust.conf", "w+")
    confFile.set("hi " + track.name, "level" + str(level), player.name + " " + str(player.bestChrono) + " " + h.hexdigest())
    confFile.write(fwrite)
    return 1
  else:
    hi = confFile.get("hi " + track.name, "level" + str(level)).split()
    h = hashlib.new(str(track.name))
    h.update(str("level" + str(level)))
    h.update(hi[0])
    h.update(hi[1])
    if hi[2] == h.hexdigest():
      if int(hi[1]) > player.bestChrono:
        h = hashlib.new(str(track.name))
        h.update(str("level" + str(level)))
        h.update(player.name)
        h.update(str(player.bestChrono))
        fwrite = open(".Speedlust.conf", "w+")
        confFile.set("hi " + track.name, "level" + str(level), player.name + " " + str(player.bestChrono) + " " + h.hexdigest())
        confFile.write(fwrite)
        return 1
      else:
        return 0
    else:
      # If the HiScore is Corrupted, erase it
      h = hashlib.new(str(track.name))
      h.update(str("level" + str(level)))
      h.update(player.name)
      h.update(str(player.bestChrono))
      fwrite = open(".Speedlust.conf", "w+")
      confFile.set("hi " + track.name, "level" + str(level), player.name + " " + str(player.bestChrono) + " " + h.hexdigest())
      confFile.write(fwrite)
      return 1

def getUnlockLevel():

  confFile=configparser.ConfigParser()
  try:
    confFile.readfp(open(".Speedlust.conf", "r"))
  except:
    return 0

  if not confFile.has_section("unlockLevel"):
    return 0
  if not confFile.has_option("unlockLevel", "key"):
    return 0

  key = confFile.get("unlockLevel", "key").split()
  h = hashlib.new("Speedlust")
  h.update(str(key[0]))
  if h.hexdigest() == key[1]:
    return key[0]
  else:
    return 0

def setUnlockLevel(lck):

  # Only change the unlock level if it's better than the actual one
  if getUnlockLevel() >= lck:
    return

  fileExist = 1

  confFile=configparser.ConfigParser()
  try:
    confFile.readfp(open(".Speedlust.conf", "r"))
  except:
    fileExist = 0

  if fileExist == 0 or not confFile.has_section("unlockLevel"):
    fwrite = open(".Speedlust.conf", "w+")
    confFile.add_section("unlockLevel")
    confFile.write(fwrite)
    confFile.readfp(open(".Speedlust.conf", "r"))

  h = hashlib.new("Speedlust")
  h.update(str(lck))
  fwrite = open(".Speedlust.conf", "w+")
  confFile.set("unlockLevel", "key", str(lck) + " " + h.hexdigest())
  confFile.write(fwrite)
 
