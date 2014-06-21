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

# IMPORTANT: DO NOT MODIFY THIS LINE!
from __future__ import print_function

# What files to get the white and black cards from:
whites = ["caha.txt", "homebrewa.txt"]
blacks = ["cahq.txt", "homebrewq.txt"]

# How many cards in a hand:
cards = 10

# Whether to turn on or off debug output:
debug = True

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# DATA AREA: (IMPORTANT: DO NOT MODIFY THIS SECTION!)
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

from rabbit.all import serverbase, strlist, random, readfile, openfile, basicformat, superformat
import re

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# CODE AREA: (IMPORTANT: DO NOT MODIFY THIS SECTION!)
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class card(object):
    def __init__(self, text):
        self.text = str(text)
        if re.compile(r".* \(\d+\)").match(self.text):
            self.text, self.blanks = self.text.rsplit(" (", 1)
            self.blanks = int(self.blanks[:-1])
        else:
            self.blanks = len(re.compile(r"\b_+\b").findall(self.text))
    def __str__(self):
        out = self.text
        if self.blanks > 0:
            out += " ("+str(self.blanks)+")"
        return out
    def __eq__(self, other):
        if isinstance(other, card):
            return self.text == other.text and self.blanks == other.blanks
        else:
            return str(self) == other

def getcards(filenames):
    cards = []
    for name in filenames:
        try:
            f = openfile(name, "rb")
            for line in readfile(f).splitlines():
                line = basicformat(line)
                if not (line.startswith("#") or line.endswith(":")):
                    cards.append(card(basicformat(line)))
        except IOError:
            pass
        else:
            f.close()
    return cards

class main(serverbase):
    def __init__(self, name="Cards Against the Brotherhood", message="Loading...", height=35, speed=400, whites=["whites.txt"], blacks=["blacks.txt"], cards=10, debug=False):
        self.cards = int(cards)
        self.whites = whites
        self.blacks = blacks
        serverbase.__init__(self, name, message, height, speed, debug)
    def getwhites(self, count=1):
        self.whites, out = self.gen.take(self.whites, count)
        return out
    def getblacks(self, count=1):
        self.blacks, out = self.gen.take(self.blacks, count)
        return out
    def begin(self):
        self.printdebug(": BEGIN")
        self.gen = random()
        if self.server:
            self.whites = getcards(self.whites)
            self.printdebug("A#: "+str(len(self.whites)))
            self.blacks = getcards(self.blacks)
            self.printdebug("Q#: "+str(len(self.blacks)))
            self.scores = {None:0}
            for a in self.c.c:
                self.queue[a].append(strlist(self.getwhites(self.cards), ";;"))
                self.scores[a] = 0
            self.hand = self.getwhites(self.cards)
            self.order = [None]+self.c.c
            self.lastblack = None
            self.x = -1
        else:
            self.czar = False
            self.hand = map(card, self.receive().split(";;"))
        self.printdebug("A$: "+repr(self.hand))
        self.app.display("You just drew: '"+strlist(self.hand, "', '")+"'.")
        self.played = None
        self.phased = False
        self.endturn(False)
        self.ready = True
    def phaseturn(self):
        self.phased = True
        if self.server == None:
            return False
        else:
            if self.server:
                played = [(self.played, None)]
                self.played = {}
                for m,a in played+self.receive():
                    if m != "$":
                        m = card(m)
                        self.whites.append(m)
                        self.played[m] = a
                self.broadcast("The cards played were: '"+strlist(self.played.keys(), "', '")+"'.")
                if self.x:
                    self.send(strlist(self.played.keys(), ";;"), self.order[self.x])
                    for a in self.c.c:
                        if a != self.order[self.x]:
                            self.queue[a].append(self.getwhites())
                else:
                    for a in self.c.c:
                        self.queue[a].append(self.getwhites())
            else:
                self.send(self.played or "$")
                if self.czar:
                    self.played = map(card, self.receive().split(";;"))
                    self.app.display("Make your choice, Card Czar.")
                else:
                    self.hand.append(card(self.receive()))
                    self.app.display("You just drew: '"+str(self.hand[-1])+"'.")
            if not self.isczar():
                self.phased = False
                if self.server:
                    choice = card(self.receive())
                    self.scores[self.played[choice]] += 1
                    self.broadcast("An awesome point was awarded to '"+self.names[self.played[choice]]+"'.")
                self.played = None
                self.endturn()
        return True
    def endturn(self, send=True):
        if self.server:
            self.x += 1
            self.x %= len(self.order)
            self.broadcast("The Card Czar is: '"+self.names[self.order[self.x]]+"'.")
            if self.lastblack:
                self.blacks.append(self.lastblack)
            self.lastblack = self.getblacks()
            self.broadcast("The Black Card is: '"+str(self.lastblack)+"'.")
            if send:
                if self.x == 0:
                    self.send("$")
                else:
                    self.send("!", self.order[self.x])
                    self.send("$", exempt=self.order[self.x])
        elif self.server != None:
            if send:
                self.czar = self.receive() == "!"
        else:
            return False
        if self.isczar():
            self.phaseturn()
        return True
    def handler(self):
        if self.ready and self.server != None:
            original = basicformat(self.box.output())
            foriginal = superformat(original)
            if foriginal.startswith("pick "):
                original = original[5:]
                testnum = isreal(original)
                if testnum and (testnum <= 0 or testnum > len(self.played) or testnum != int(testnum)):
                    self.app.display("That's not a valid card index.")
                else:
                    if testnum:
                        original = self.played.keys()[int(1+testnum)]
                    else:
                        original = card(original)
                    if not self.phased:
                        self.app.display("You can't pick yet, you're still in the playing stage.")
                    elif not self.isczar():
                        self.app.display("You're not the Card Czar, so you're playing, not picking.")
                    elif not original in self.played:
                        self.app.display("You can't pick a card that nobody played.")
                    else:
                        self.phased = False
                        if self.server:
                            self.scores[self.played[original]] += 1
                            self.broadcast("An awesome point was awarded to "+self.names[self.played[original]]+".")
                        else:
                            self.send(original)
                        self.played = None
                        self.endturn()
            elif foriginal.startswith("play "):
                original = original[5:]
                testnum = isreal(original)
                if testnum and (testnum <= 0 or testnum > len(self.hand) or testnum != int(testnum)):
                    self.app.display("That's not a valid card index.")
                else:
                    if testnum:
                        original = self.hand[int(1+testnum)]
                    else:
                        original = card(original)
                    if self.phased:
                        self.app.display("You can't play yet, you're still in the picking stage.")
                    elif self.isczar():
                        self.app.display("You're the Card Czar, so you're picking, not playing.")
                    elif not original in self.hand:
                        self.app.display("You can't play a card you don't have in your hand.")
                    else:
                        self.played = card(original)
                        self.app.display("You just played: '"+str(self.played)+"'.")
                        self.hand.remove(self.played)
                        self.phaseturn()
            elif foriginal.startswith("say "):
                self.textmsg(original[4:])
            elif original != "":
                self.textmsg(original)
    def isczar(self):
        if self.server:
            return self.x == 0
        elif self.server != None:
            return self.czar
        else:
            return None

if __name__ == "__main__":
    main(whites=whites, blacks=blacks, cards=cards, debug=debug).start()
