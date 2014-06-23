#!/usr/bin/python

# NOTE:
# This is the code. If you are seeing this when you open the program normally, please follow the steps here:
# https://sites.google.com/site/evanspythonhub/having-problems

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# INFO AREA:
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Program by: Evan
# PROGRAM made in 2012
# This program will facilitate games of Cards Against Humanity.

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# CONFIG AREA:
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# What files to get the white and black cards from:
whites = ["caha.txt", "homebrewa.txt", "expansion1a.txt", "expansion2a.txt", "expansion3a.txt", "expansion4a.txt"]
blacks = ["cahq.txt", "homebrewq.txt", "expansion1q.txt", "expansion2q.txt", "expansion3q.txt", "expansion4q.txt"]

# How many cards in a hand:
cards = 10

# Whether to turn on or off debug output:
debug = False

# What port to connect to:
port = 6775

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# DATA AREA: (IMPORTANT: DO NOT MODIFY THIS SECTION!)
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

import os
import sys

rootdir = os.path.join(os.path.split(os.getcwd())[0], 'rabbit')
if rootdir not in sys.path:
    sys.path.append(rootdir)

from game import main

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# CODE AREA: (IMPORTANT: DO NOT MODIFY THIS SECTION!)
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

main(whites=whites, blacks=blacks, cards=cards, port=port, debug=debug).start()
