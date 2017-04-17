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
whites = ["caha.txt",
		  "homebrewa.txt",
		  "expansion1a.txt",
		  "expansion2a.txt",
		  "expansion3a.txt",
		  "expansion4a.txt",
		  "misca.txt",
		  "xkcda.txt",
		  "rationalitya.txt",
		  "devopsa.txt"
		  ]
blacks = ["cahq.txt",
		  "homebrewq.txt",
		  "expansion1q.txt",
		  "expansion2q.txt",
		  "expansion3q.txt",
		  "expansion4q.txt",
		  "miscq.txt",
		  "xkcdq.txt",
		  "rationalityq.txt",
		  "devopsq.txt"
		  ]

# Extra files to use if hackergen is found:
hackergen_whites = ["hackergena.txt"
					]
hackergen_blacks = ["hackergenq.txt"
					]

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

rootdir = os.path.join(os.path.abspath(os.path.dirname(os.path.realpath(__file__))), "rabbit")
if rootdir not in sys.path:
	sys.path.append(rootdir)

from game import main, hackergen, ircbot

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# CODE AREA: (IMPORTANT: DO NOT MODIFY THIS SECTION!)
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

if hackergen:
	whites.append(hackergen_whites)
	blacks.append(hackergen_blacks)

if len(sys.argv) < 4:
	print "USAGE: ip, port, channel"
	exit(1)
ip, port, channel = sys.argv[1], int(sys.argv[2]), sys.argv[3]

game = main(whites=whites, blacks=blacks, cards=cards, port=port, debug=debug)
bot  = ircbot(ip, port, channel, game.handlemessage)

bot.run()
