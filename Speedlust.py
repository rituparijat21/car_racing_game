import pygame
from pygame.locals import *

import time
import sys
import os

sys.path.append("modules")
import misc
import player
import game
import menu
import track


def main():
    if os.name == "nt":
        full = 0
        double = 0
    else:
        full = 0
        double = 1

    displayFlags = HWSURFACE

    # Get commandline options
    if len(sys.argv) != 1:
        for i in range(1, len(sys.argv)):
            if sys.argv[i].upper() == "--RESOLUTION":
                # Get the resolution
                if i != len(sys.argv) - 1 and sys.argv[i + 1].upper() == "640X480":
                    misc.zoom = 0.625
                elif i != len(sys.argv) - 1 and sys.argv[i + 1].upper() == "320X240":
                    misc.zoom = 0.3125
            if sys.argv[i].upper() == "--FULLSCREEN":
                full = 1
            if sys.argv[i].upper() == "--DOUBLEBUF":
                double = 1
            if sys.argv[i].upper() == "--NODOUBLEBUF":
                double = 0
            if sys.argv[i].upper() == "--NOSOUND":
                misc.music = 0
            if sys.argv[i].upper() == "--HELP" or sys.argv[i].upper() == "-H":
                print(
                    "USAGE: Speedlust.py [--resolution 640x480|320x240] [--fullscreen] [--doublebuf|--nodoublebuf] [--nosound] [--help|-h] [--version]")
                print()
                print("  --resolution   Change resolution (default is 1024x768)")
                print("  --fullscreen   Enable fullscreen display")
                print("  --doublebuf    Enable double buffering display (DEFAULT on other platform than Windows)")
                print("  --nodoublebuf  Disable double buffering display (DEFAULT on Windows)")
                print("  --nosound      Disable Sound")
                print("  --help|-h      Display this help and exit")
                print("  --version      Output version information and exit")
                sys.exit(0)
            if sys.argv[i].upper() == "--VERSION":
                print("Speedlust version " + misc.VERSION + ", Copyright (C) 2018 Ritu <rituparijat21@gmail.com>")
                print()
                print("Speedlust comes with ABSOLUTELY NO WARRANTY.")
                print("This is free software, and you are welcome to redistribute it")
                print("under certain conditions; see the COPYING file for details.")
                sys.exit(0)

    if full == 1 and double == 1:
        displayFlags = displayFlags | DOUBLEBUF | FULLSCREEN
    elif full == 1 and double == 0:
        displayFlags = displayFlags | FULLSCREEN
    elif full == 0 and double == 1:
        displayFlags = displayFlags | DOUBLEBUF
    elif full == 0 and double == 0:
        displayFlags = displayFlags

    try:
        pygame.init()
    except:
        print("Cannot initialize pyGame:")
        sys.exit(-1)

    if pygame.display.mode_ok((int(1024 * misc.zoom), int(768 * misc.zoom)), displayFlags, 24) == 0:
        print("Speedlust cannot initialize display...")
        sys.exit(-1)
    else:
        misc.screen = pygame.display.set_mode((int(1024 * misc.zoom), int(768 * misc.zoom)), displayFlags, 24)

    pygame.display.set_caption("Speedlust v" + misc.VERSION)
    pygame.display.set_icon(pygame.image.load(os.path.join("sprites", "SpeedlustIcon.bmp")))

    if misc.music == 1:
        pygame.mixer.music.load(os.path.join("sounds", "start.ogg"))
        pygame.mixer.music.play()

    try:
        import psyco
        psyco.full()
    except:
        print("Cannot use psyCo...")
        pass

    pygame.mouse.set_visible(0)

    misc.init()

    select1 = 1

    while select1 != -1:
        menu1 = menu.SimpleMenu(misc.titleFont, "Speedlust v" + misc.VERSION, 20 * misc.zoom, misc.itemFont,
                                ["Single Race", "Tournament", "Hi Scores", "Credits", "License"])
        select1 = menu1.getInput()

        # Single Race
        if select1 == 1:
            race = game.Game("singleRace")

            menu2 = menu.ChooseTrackMenu(misc.titleFont, "singleRace: Track", 2 * misc.zoom, misc.itemFont)
            select2 = menu2.getInput()
            if select2 != -1:
                race.listTrackName = [[select2[0], select2[1]]]

                menu3 = menu.ChooseValueMenu(misc.titleFont, "singleRace: Laps", 0, misc.itemFont, 1, 10)
                select3 = menu3.getInput()
                if select3 != -1:
                    race.maxLapNb = select3

                    menu4 = menu.ChooseValueMenu(misc.titleFont, "singleRace: HumanPlayers", 0, misc.itemFont, 0, 4)
                    select4 = menu4.getInput()
                    if select4 != -1:

                        isExit = 0
                        race.listPlayer = []
                        for i in range(1, select4 + 1):
                            menu5 = menu.ChooseHumanPlayerMenu(misc.titleFont, "singleRace: HumanPlayer" + str(i),
                                                               5 * misc.zoom, misc.itemFont)
                            thePlayer = menu5.getInput()
                            if thePlayer == -1:
                                isExit = 1
                                break
                            race.listPlayer.append(thePlayer)

                        # If there's no exit during enter of player
                        if isExit == 0:
                            # If there's no Human player, there should exist at least a Bot player
                            if select4 == 0:
                                minBot = 1
                            else:
                                minBot = 0
                            menu6 = menu.ChooseValueMenu(misc.titleFont, "singleRace: RobotPlayers", 0, misc.itemFont,
                                                         minBot, 4)
                            select6 = menu6.getInput()
                            if select6 != -1:
                                isExit = 0
                                for i in range(1, select6 + 1):
                                    menu7 = menu.ChooseRobotPlayerMenu(misc.titleFont,
                                                                       "singleRace: RobotPlayer" + str(i),
                                                                       5 * misc.zoom, misc.itemFont)
                                    thePlayer = menu7.getInput()
                                    if thePlayer == -1:
                                        isExit = 1
                                        break
                                    race.listPlayer.append(thePlayer)

                                # If there's no exit during enter of player
                                if isExit == 0:
                                    race.play()

        # Tournament
        elif select1 == 2:
            tournament = game.Game("tournament")

            tournament.listTrackName = []

            # Get all tracks to put in the tournament
            listAvailableTrackNames = track.getAvailableTrackNames()

            for trackName in listAvailableTrackNames:
                tournament.listTrackName.append([trackName, 0])

            # Also Reverse tracks
            for trackName in listAvailableTrackNames:
                tournament.listTrackName.append([trackName, 1])

            menu2 = menu.ChooseValueMenu(misc.titleFont, "tournament: Laps", 0, misc.itemFont, 1, 10)
            select2 = menu2.getInput()
            if select2 != -1:
                tournament.maxLapNb = select2

                menu3 = menu.ChooseValueMenu(misc.titleFont, "tournament: HumanPlayers", 0, misc.itemFont, 0, 4)
                select3 = menu3.getInput()
                if select3 != -1:

                    isExit = 0
                    tournament.listPlayer = []
                    for i in range(1, select3 + 1):
                        menu4 = menu.ChooseHumanPlayerMenu(misc.titleFont, "tournament: HumanPlayer" + str(i),
                                                           5 * misc.zoom, misc.itemFont)
                        thePlayer = menu4.getInput()
                        if thePlayer == -1:
                            isExit = 1
                            break
                        tournament.listPlayer.append(thePlayer)

                    # If there's no exit during enter of player
                    if isExit == 0:
                        # If there's no Human player, there should exist at least a Bot player
                        if select3 == 0:
                            minBot = 1
                        else:
                            minBot = 0
                        menu6 = menu.ChooseValueMenu(misc.titleFont, "tournament: RobotPlayers", 0, misc.itemFont,
                                                     minBot, 4)
                        select6 = menu6.getInput()
                        if select6 != -1:
                            isExit = 0
                            for i in range(1, select6 + 1):
                                menu7 = menu.ChooseRobotPlayerMenu(misc.titleFont, "tournament: RobotPlayer" + str(i),
                                                                   5 * misc.zoom, misc.itemFont)
                                thePlayer = menu7.getInput()
                                if thePlayer == -1:
                                    isExit = 1
                                    break
                                tournament.listPlayer.append(thePlayer)

                    # If there's no exit during enter of player
                    if isExit == 0:
                        tournament.play()

        elif select1 == 3:
            hiscoresMenu = menu.MenuHiscores(misc.titleFont, "hiscores", 10 * misc.zoom, misc.smallItemFont)
            hiscoresMenu.getInput()
        elif select1 == 4:
            creditsMenu = menu.MenuCredits(misc.titleFont, "credits", 10 * misc.zoom, misc.itemFont)
            misc.wait4Key()
        elif select1 == 5:
            licenseMenu = menu.MenuLicense(misc.titleFont, "license", 10 * misc.zoom, misc.smallItemFont)
            misc.wait4Key()


if __name__ == '__main__': main()
