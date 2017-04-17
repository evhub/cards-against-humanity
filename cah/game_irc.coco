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

from __future__ import with_statement, unicode_literals, print_function
from rabbit.all import basicformat
import socket
import random
import re
from collections import deque

try:
	import hackergen.phrasegen as hackergen
except ImportError:
	try:
		import hackergen
	except ImportError:
		hackergen = None
else:
	hackergen.tense("fut")

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# CODE AREA: (IMPORTANT: DO NOT MODIFY THIS SECTION!)
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# fake substitute for popup
def popup():
	pass

def getPhrase(*args, **kwargs):
	out = hackergen.getPhrase(*args, **kwargs)
	if out.endswith("."):
		out = out[:-1]
	return out

class card(object):
	def __init__(self, text, scan=False):
		if hackergen:
			out = self.phrasesub(text)
		else:
			out = str(text)
		self.blanks = 0
		if re.compile(r".* \(\d+\)").match(out):
			self.text, self.blanks = out.rsplit(" (", 1)
			self.blanks = int(self.blanks[:-1])
		elif scan:
			self.text = ""
			inside = False
			for c in out:
				if c != "_":
					inside = False
				elif not inside:
					do = False
					if len(self.text) != 0 and self.text[-1] == "\\":
						self.text = self.text[:-1]
						if len(self.text) != 1 and self.text[-2] == "\\":
							do = True
					else:
						do = True
					if do:
						self.blanks += 1
						inside = True
				self.text += c
		else:
			self.text = out
		self.check()

	def check(self):
		if self.text:
			self.text = self.text[0].upper()+self.text[1:]
		else:
			raise ValueError("Cannot have an empty card.")

	def phrasesub(self, text):
		out = ""
		inside = False
		for c in str(text):
			if inside:
				if c == "}":
					if inside is True:
						inside = ""
					parts = inside.split(":")
					if len(parts) == 2:
						done = False
						if parts[0] and parts[0] != "fut":
							try:
								hackergen.tense(parts[0])
							except:
								done = None
							else:
								done = True
						if done is not None:
							if not parts[1]:
								out += getPhrase()
								inside = False
							else:
								try:
									num = int(parts[1])
								except ValueError:
									inside = parts[1]
								else:
									out += getPhrase(num)
									inside = False
							if done:
								hackergen.tense("fut")
					if inside is not False:
						out += "{"+inside+"}"
						inside = False
				elif inside is True:
					inside = c
				else:
					inside += c
			elif c == "{":
				if len(out) != 0 and out[-1] == "\\":
					if len(out) != 1 and out[-2] == "\\":
						out = out[:-1]
						inside = True
					else:
						out = out[:-1]+c
				else:
					inside = True
			else:
				out += c
		if inside is True:
			out += "{"
		elif inside:
			out += "{"+inside
		return out

	def black(self):
		if self.blanks == 0:
			self.blanks = 1

	def white(self):
		self.blanks = 0

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
		f = None
		try:
			with open(name) as f:
				for line in f:
					line = line.strip()
					if line and not line.startswith("#"):
						if line.endswith(":"):
							if len(line) > 1 and line[-2] == "\\":
								line = line[:-2]+line[-1]
							else:
								continue
						elif not black and line.endswith(".") and len(line) > 1:
							if line[-2] == "\\":
								if len(line) > 2 and line[-3] == "\\":
									line = line[:-2]
								else:
									line = line[:-2]+line[-1]
							elif not "!" in line[:-1] or "?" in line[:-1] or "." in line[:-1]:
								line = line[:-1]
						line = line.replace("\\n", "\n").replace("\\\n", "\\n")
						cards.append(card(line, black))
						if black:
							cards[-1].black()
						else:
							cards[-1].white()
		except IOError:
			print("WARNING: Unable to find file "+str(name))
		finally:
			f.close()
	return list(set(cards))

class ircbot():
	def __init__(self, ip, port, channel, messagehandler, nick="cabbot", prefix="cab"):
		self.ip = ip
		self.port = port
		self.channel = channel
		self.prefix = prefix
		self.messagehandler = messagehandler

		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.socket.connect((ip, port))
		self.socket.send("USER " + (nick + " ") * 3 + ": This bot is for playing cards against the brotherhood\n")
		self.socket.send("NICK " + nick + "\n")
		self.socket.send("JOIN " + channel + "\n")

	def send(self, message):
		print(message)
		self.socket.send("PRIVMSG " + self.channel + " :" + message + "\n")

	def psend(self, nick, message):
		self.socket.send("PRIVMSG " + nick + " :" + message + "\n")
	
	def pong(self):
		self.socket.send("PONG :pingis\n")

	def recv(self, length):
		data = self.socket.recv(length)
		print(data)
		match = re.match(r':(.+?)\s+(.+?)\s+.*?:(.+)\s*', data)
		if match:
			sender = match.group(1).split('!')[0]
			dtype = match.group(2)
			message = match.group(3)
			return dtype, sender, message
		elif re.match(r'^PING', data):
			return 'PING', ' ', ' '
		return False, False, False
		
	def update(self):
		dtype,sender,message = self.recv(2048)
		if not dtype or not sender or not message:
			return #abort
		if dtype == "PRIVMSG" and message.startswith(self.prefix):
			self.messagehandler(self, sender, message[(len(self.prefix)):].strip())
		elif dtype == 'PING':
			self.pong()

	def run(self):
		while True:
			self.update()
					
class main():

	def cenumerate(self, sender):
		l = self.playercards[sender]
		ls = ''
		for i in range(len(l)):
			ls += "%s. '%s', " % (str(i),str(l[i]))
		return ls

	def senumerate(self):
		ls = ''
		for k in self.playerscores.keys():
			ls += "%s: %s, " % (k,str(self.playerscores[k]))
		return ls

	def __init__(self,
		name="Cards Against the Brotherhood",
		message="Initializing...",
		speed=400,
		port=6775,
		whites=["whites.txt"],
		blacks=["blacks.txt"],
		cards=10,
		debug=False):

		self.whites = whites
		self.blacks = blacks

		self.cards = cards

		self.whitecards = getcards(whites)
		self.blackcards = getcards(blacks, black=True)
		random.shuffle(self.whitecards)
		random.shuffle(self.blackcards)

		self.roundcards = {}
		self.playercards = {}
		self.playerscores = {}
		self.playerlist = []
		self.state = 'idle'

	def reset(self):
		self.roundcards = {}
		self.playercards = {}
		self.playerscores = {}
		self.playerlist = []
		self.state = 'idle'

		self.whitecards = getcards(self.whites)
		self.blackcards = getcards(self.blacks, black=True)
		random.shuffle(self.whitecards)
		random.shuffle(self.blackcards)
	
	def prepareplayers(self):
		self.playerlist = deque(self.playercards.keys())

	def newcardczar(self):
		self.playerlist.rotate(1)
		self.cardczar = self.playerlist[0]
		return self.cardczar

	def allplayed(self):
		for p in self.playerlist:
			if not p == self.cardczar:
				if not p in self.roundcards:
					return False
				if len(self.roundcards[p]) < self.blackcard.blanks:
					return False
		return True
	
	def givecards(self, sender, num):
		self.playercards[sender].extend([ self.whitecards.pop() for i in range(num) ])

	def helpmessage(self):
		return 'To see your cards, type \'cab cards\'. To play your card, type \'cab play <card index>\'. If you\'re card czar,\
			pick the winning card by typing \'cab pick <beginning of winning card>\'. To kill the game and ruin everyone\'s\
			fun, type \'cab abort\'.'

	def handlemessage(self, bot, sender, message):

		if message == 'abort':
			bot.send('Game aborted by %s.' % (sender))
			self.reset()

		if message == 'prepare' and self.state == 'idle':
			bot.send('Preparing for a game. type: "%s join" to join in.' % (bot.prefix))
			self.state = 'join'
			
		if message == 'join':
			self.playercards[sender] = []
			self.playerscores[sender] = 0
			self.givecards(sender, self.cards)
			if self.state == 'play' or self.state == 'pick':
				bot.send('%s has joined the game. Resetting this round.' % (sender))
				self.playerlist.push(sender)
				self.resetround()
				return
			bot.send('%s has joined the game.' % (sender))
		
		if message == 'leave':
			bot.send('%s is leaving the game.' % (sender))
			self.removeplayer(bot, sender)
	
		if message == 'start' and self.state == 'join':
			# begin the game
			if len(self.playercards.keys()) < 3:
				bot.send('Not enough players to start.')
				return
			bot.send('Starting the game. Too late to join now.')
			self.state = 'play'
			self.prepareplayers()
			self.startround(bot)

		if message == 'help':
			bot.psend(sender, self.helpmessage())

		# in game commands
		if self.state == 'play':

			if message == 'cards':
				bot.psend(sender, self.cenumerate(sender))

			if message.startswith('play'):
				if (sender == self.cardczar):
					bot.psend(sender, 'You can\'t play any cards; you\'re the card czar.')
					return
				self.playcard(bot, sender, message)

		if message.startswith('pick') and self.state == 'pick' and sender == self.cardczar:
			self.pickcard(bot, message)

	def removeplayer(self, bot, sender):
		del self.playercards[sender]
		del self.playerscores[sender]
		if self.state == 'play' or self.state == 'pick': 
			self.playerlist.remove(sender)
			bot.send('Skipping the remainder of this round.')
			self.resetround()
	
	def resetround(self):
			for k in self.playercards.keys():
				if len(self.playercards[k]) < self.cards:
					self.givecards(k, self.cards - len(self.playercards[k]))
			self.state = 'play'
			self.roundcards = {}
			self.startround(bot)

	def startround(self, bot):
		cardczar = self.newcardczar()	
		self.roundcards = {}
		self.blackcard = self.blackcards.pop()			
		bot.send('The card czar is %s, and the black card is: "%s." Play your cards.' % (cardczar, str(self.blackcard)))
		for k in self.playerlist:
			bot.psend(k, self.cenumerate(k))

	# don't mind this function
	def cardlisttostr(self, v):
		return '; '.join([ str(c) for c in v ])

	def pickround(self, bot):
		for k in self.roundcards.keys():
			self.givecards(k, self.blackcard.blanks)
	
		choices = self.roundcards.values()
		random.shuffle(choices)
		choicemessage = ''	
		for v in choices:
			choicemessage += '[%s], ' % (self.cardlisttostr(v))
		bot.send('Time to choose, %s. The card is "%s." Your choices are: %s.' % (self.cardczar, str(self.blackcard), choicemessage))

	def playcard(self, bot, sender, message):
		index = 0
		whitecard = None
		try:
			index = int(message[len('play'):].strip())
			whitecard = self.playercards[sender][index]
		except:
			bot.psend(sender, 'Invalid index: \'%s\'. Try using the \'cards\' command.' % (message))
			return	
		if not sender in self.roundcards:
			self.roundcards[sender] = [whitecard]
		elif len(self.roundcards[sender]) < self.blackcard.blanks:
			self.roundcards[sender].append(whitecard)
		else:
			bot.psend(sender, 'You\'ve already played enough cards.')
			return
		self.playercards[sender].pop(index)

		bot.psend(sender, 'You have played "%s"' % (str(whitecard)))
		if self.blackcard.blanks > 1:
			bot.psend(sender, 'Your cards are now: %s' % (self.cenumerate(sender)))

		if self.allplayed():
			self.state = 'pick'
			self.pickround(bot)

	def pickcard(self, bot, message):
		match = message[len('pick'):].strip()
		for k in self.roundcards.keys():
			for v in self.roundcards[k]:
				if str(v).lower().startswith(match.lower()):
					self.playerscores[k] += 1
					bot.send('The winner of this round is %s, with [%s]. Our current scores are: %s' %
						(k, self.cardlisttostr(self.roundcards[k]), self.senumerate()))
					self.state = 'play'
					self.startround(bot)
					return
		bot.psend(self.cardczar, 'Please enter a valid choice.')
