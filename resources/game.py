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
# DATA AREA: (IMPORTANT: DO NOT MODIFY THIS SECTION!)
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

from __future__ import print_function
from rabbit.all import serverbase, strlist, random, readfile, openfile, basicformat, superformat, popup, isreal, islist
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
            self.blanks = 0
            inside = False
            for c in self.text:
                if c == "_" and not inside:
                    self.blanks += 1
                    inside = True
                else:
                    inside = False
    def black(self):
        if self.blanks == 0:
            self.blanks += 1
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

def getcards(filenames, black=False):
    cards = []
    for name in filenames:
        try:
            f = openfile(name, "rb")
            for line in readfile(f).splitlines():
                line = basicformat(line)
                if line and not (line.startswith("#") or line.endswith(":")):
                    if line[-1] not in [".", "?", "!", '"']:
                        line += "."
                    line = basicformat(line).replace("\\n", "\n")
                    cards.append(card(line))
                    if black:
                        cards[-1].black()
        except IOError:
            pass
        else:
            f.close()
    return list(set(cards))

class main(serverbase):
    def __init__(self, name="Cards Against the Brotherhood", message="Initializing...", height=35, speed=400, port=6775, whites=["whites.txt"], blacks=["blacks.txt"], cards=10, debug=False):
        self.cards = int(cards)
        self.whites = whites
        self.blacks = blacks
        serverbase.__init__(self, name, message, height, speed, port, debug)
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
            self.blacks = getcards(self.blacks, True)
            self.printdebug("Q#: "+str(len(self.blacks)))
            self.scores = {None:0}
            for a in self.c.c:
                self.queue[a].append(strlist(self.getwhites(self.cards), ";;"))
                self.scores[a] = 0
            self.hand = self.getwhites(self.cards)
            self.order = [None]+self.c.c.keys()
            self.x = -1
        else:
            self.czar = False
            self.hand = map(card, self.receive().split(";;"))
        self.app.display("Loaded.")
        self.black = None
        self.phased = False
        self.waiting = False
        self.onsent("end", self.endwait)
        self.onsent("phase1", self.phasewait)
        self.onsent("phase2", self.phaseturn)
        self.onsent("score", self.replyscore)
        self.onsent("pick", self.pickwait)
        if self.server:
            self.broadcast("Connected players are: "+strlist(self.names.values(), ", ")+".")
        self.app.display("You just drew: "+strlist(self.hand, ", ")+".")
        self.endturn(False)
        self.ready = True
    def phaseturn(self, arg="", a=None):
        self.phased = True
        if self.server == None:
            return False
        else:
            self.printdebug(": PHASE")
            if self.server:
                if self.played:
                    played = [(self.played, None)]
                else:
                    played = []
                played += self.receive()
                self.played = {}
                for m,a in played:
                    if m != "$":
                        if not islist(m):
                            m = map(card, m.split(";;"))
                        self.whites.extend(m)
                        self.played[strlist(m, ";;")] = a
                self.broadcast("The cards played were: "+strlist(self.played.keys(), ", ", lambda m: "("+strlist(m.split(";;"), "; ")+")")+".")
                played = {}
                for m,a in self.played.items():
                    played[strlist(m.split(";;"), "; ")] = a
                self.played = played
                if self.x:
                    self.send(strlist(self.played.keys(), ";;"), self.order[self.x])
                    for a in self.c.c:
                        if a != self.order[self.x]:
                            self.queue[a].append(strlist(self.getwhites(self.black.blanks), ";;"))
                    drew = self.getwhites(self.black.blanks)
                    self.hand.extend(drew)
                    self.app.display("You just drew: "+strlist(drew, "; ")+".")
                else:
                    for a in self.c.c:
                        self.queue[a].append(strlist(self.getwhites(self.black.blanks), ";;"))
            else:
                if self.played:
                    self.send(strlist(self.played, ";;"))
                else:
                    self.send("$")
                if self.czar:
                    self.played = self.receive().split(";;")
                else:
                    drew = map(card, self.receive().split(";;"))
                    self.hand.extend(drew)
                    self.app.display("You just drew: "+strlist(drew, "; ")+".")
            if self.isczar():
                self.app.display("Make your choice, Card Czar.")
            else:
                self.app.display("The Card Czar is making their choice.")
                self.phased = False
            self.waiting = "end"
        return True
    def sendscores(self):
        out = []
        for a in self.scores:
            name = self.names[a]
            out.append(""+name+" ("+str(self.scores[a])+")")
        self.broadcast("The current awesome point totals are: "+strlist(out, ", ")+".")
    def pickwait(self, arg="", a=None):
        if self.waiting == "end":
            arg = str(arg)
            self.scores[self.played[arg]] += 1
            self.broadcast("An awesome point was awarded to "+self.names[self.played[arg]]+" for ("+arg+").")
            self.trigger("end")
            self.sendscores()
        else:
            self.printdebug("ERROR: Tried triggering pick when not waiting for it.")
    def endwait(self, arg="", a=None):
        if self.waiting == "end":
            self.endturn()
        else:
            self.printdebug("ERROR: Tried triggering end when not waiting for it.")
    def phasewait(self, arg="", a=None):
        if self.waiting == "phase":
            if not a in self.didphase:
                self.didphase.append(a)
            if len(self.didphase) >= len(self.c.c):
                self.trigger("phase2")
        else:
            self.printdebug("ERROR: Tried triggering phase when not waiting for it.")
    def replyscore(self, arg="", a=None):
        self.send(str(arg)+str(self.scores[a]), a)
    def endturn(self, send=True):
        self.played = []
        if self.server == None:
            return False
        else:
            self.printdebug(": TURN")
            if self.server:
                self.didphase = []
                self.x += 1
                self.x %= len(self.order)
                self.broadcast("The Card Czar is: "+self.names[self.order[self.x]]+".")
                if self.black:
                    self.blacks.append(self.black)
                self.black = self.getblacks()[0]
                self.send(str(self.black))
                if send:
                    if self.x == 0:
                        self.send("$")
                    else:
                        self.send("!", self.order[self.x])
                        self.send("$", exempt=self.order[self.x])
            else:
                self.black = card(self.receive())
                if send:
                    self.czar = self.receive() == "!"
            self.app.display("The Black Card is: "+str(self.black)+".")
            self.waiting = "phase"
            return True
    def handler(self, event=None):
        if self.ready and self.server != None:
            self.process(self.box.output())
    def process(self, inputstring):
        original = basicformat(inputstring)
        foriginal = superformat(original)
        if foriginal == "help":
            self.app.display("The available commands are: pick, play, score, hand, say")
        elif foriginal.startswith("pick "):
            original = original[5:]
            testnum = isreal(original)
            if testnum and (testnum <= 0 or testnum > len(self.played) or testnum != int(testnum)):
                self.app.display("That's not a valid card index.")
            else:
                if testnum:
                    original = str(self.played.keys()[int(1+testnum)])
                if not self.phased:
                    self.app.display("You can't pick yet, you're still in the playing stage.")
                elif not self.isczar():
                    self.app.display("You're not the Card Czar, so you're playing, not picking.")
                elif self.waiting != "end":
                    self.app.display("You have to wait for others until you can pick.")
                elif not self.played:
                    self.app.display("You can't pick multiple people's cards.")
                else:
                    test = False
                    for play in self.played:
                        if play.startswith(original):
                            original = play
                            test = True
                            break
                    if not test:
                        self.app.display("You can't pick a card that nobody played.")
                    else:
                        self.phased = False
                        if self.server:
                            self.scores[self.played[original]] += 1
                            self.broadcast("An awesome point was awarded to "+self.names[self.played[original]]+" for ("+original+").")
                        else:
                            self.trigger("pick", original, toall=False)
                        self.trigger("end")
                        if self.server:
                            self.sendscores()
        elif foriginal.startswith("play "):
            original = original[5:]
            testnum = isreal(original)
            if testnum and (testnum <= 0 or testnum > len(self.hand) or testnum != int(testnum)):
                self.app.display("That's not a valid card index.")
            else:
                if testnum:
                    original = str(self.hand[int(1+testnum)])
                if self.phased:
                    self.app.display("You can't play yet, you're still in the picking stage.")
                elif self.isczar():
                    self.app.display("You're the Card Czar, so you're picking, not playing.")
                elif self.waiting != "phase":
                    self.app.display("You have to wait for others until you can play.")
                elif len(self.played) >= self.black.blanks:
                    self.app.display("You can't play anymore cards this turn.")
                else:
                    test = False
                    for choice in self.hand:
                        choice = str(choice)
                        if choice.startswith(original):
                            original = choice
                            test = True
                            break
                    if not test:
                        if ";" in original:
                            for item in original.split(";"):
                                self.process("play "+item)
                        else:
                            self.app.display("You can't play a card that you don't have in your hand.")
                    else:
                        self.played.append(original)
                        self.app.display("You just played: "+str(self.played[-1])+".")
                        self.hand.remove(self.played[-1])
                        if len(self.played) < self.black.blanks:
                            self.app.display("You still have "+str(self.black.blanks-len(self.played))+" more cards to play.")
                        elif self.server:
                            self.schedule(self.phasewait)
                        else:
                            self.trigger("phase1", toall=False)
        elif foriginal == "score":
            if self.server:
                points = self.scores[None]
            else:
                self.trigger("score", toall=False)
                points = self.receive()
            self.app.display("You currently have "+str(points)+" awesome points.")
        elif foriginal == "hand":
            self.app.display("Your hand contains: "+strlist(self.hand, "; ")+".")
        elif foriginal.startswith("say "):
            self.textmsg(original[4:])
        elif original:
            self.textmsg(original)
    def isczar(self):
        if self.server:
            return self.x == 0
        elif self.server != None:
            return self.czar
        else:
            return None
