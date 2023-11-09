from os import remove
from random import choice, randint
from getpass import getuser
from pathlib import Path
from functools import reduce
import logging
from datetime import datetime
from errno import EPERM
from argparse import ArgumentParser
from glob import glob

class RussianRoulettePy():
	def __init__(
		self,
		mode: str = "normal",
		folders: list[str] = [
			"Documents",
			"Downloads",
			"Music",
			"Pictures",
			"Videos",
			"Desktop"
		],
		bullets: int = 6,
		practice: bool = False
	):
		'''
		Initializes Russian Roulette game.
		
		mode:
			"normal" - Normal game mode, random file removed when a shoot is executed.
			
			"baby" - It just doesn't remove files, but prints what file would have been removed. For babies.

			"realtime" - Similar to normal mode, but files are targeted each round (so you'd know what you could lose before pulling the trigger).

			"suicide" - Targets this script file.

			"extreme" - Targets System32 (MUST run the script with root privileges).

			"hard" - #TODO: Instead of targeting files, targets whole parent directory of random files.

			"hardrt" - #TODO: Hard mode realtime; i.e., directories are targeted each round before pulling the trigger.
		
			"apps" - #TODO: Would remove application directories from 'Program Files' and 'Program Files (x86)' instead of 'folders' arg.

			"executables" - #TODO: Would remove .exe files from the computer, variation of 'apps' mode.
		folders: list of folders to analize.
		bullets: number of bullets... lol
		practice:
			Whether instead of removing the files permanently, they're moved on to the Recycle Bin.
			
			Does not affect "baby" and "extreme" modes.
			
			REQUIRES Send2Trash MODULE INSTALLED
		
		Made by Benjas333
		'''
		indexingModes = ['normal', 'baby', 'realtime']
		notIndexingModes = ['suicide', 'extreme']
		if mode.lower() not in indexingModes and mode.lower() not in notIndexingModes:
			raise Exception("Unknown game mode.")
		self.mode = mode.lower()

		logging.info(f"{datetime.now()}| Initializing RussianRoulettePy {self.mode} game")
		print(f"------------ RUSSIAN ROULETTE ({self.mode} mode) ------------\nLoading... ", end='')
		
		self.user = getuser()
		self.basePath = f"C:/Users/{self.user}"
		self.folders = folders
		self.extension = "*"
		
		self.bullets = bullets
		self.boolToStr = {
			True: "BOOM",
			False: "PASS"
		}
		self.actTarget = None

		self.playing = False
		self.highscore = 0
		self.score = 0
		self.rounds = 0
		self.filesLost = 0

		self.noROOT = False # FIXME: this should be better xd

		if practice:
			from send2trash import send2trash
			self.remove = send2trash
		else:
			self.remove = remove

		if self.mode in indexingModes:
			self.paths = list(map(lambda a: f"{self.basePath}/{a}", self.folders))
			logging.info(f"{datetime.now()}| Indexing files...")
			self.filesArrays = list(map(lambda a: glob(f"{(Path(a) / '**' / f'*.{self.extension}').resolve()}", recursive=True), self.paths))
			# self.files = reduce(lambda a, b: a + b, self.foldersArray) # XXX: probably not necessary anymore
			logging.info(f"{datetime.now()}| Indexed {reduce(lambda x, y: x + y, map(lambda a: len(a), self.filesArrays))} files")
		print("Ready to play.")
		
	
	def targetFile(self) -> Path:
		'''
		Targets a file to remove.

		return Path
		'''
		self.folderIndex = randint(0, len(self.filesArrays) - 1)
		res = choice(self.filesArrays[self.folderIndex])
		logging.info(f"{datetime.now()}| {res} targeted")
		return res
	
	def shoot(self) -> bool:
		'''
		Executes a shoot.

		return bool
		'''
		if randint(0, self.bullets) == 1:
			res = True
			logging.info(f"{datetime.now()}| {self.boolToStr[res]}")
		else:
			res = False
		return res
	
	def scoreHandler(self, shoot: bool):
		'''
		Handles the score functionality.
		'''
		self.rounds += 1
		self.score += 1
		if self.score > self.highscore: self.highscore = self.score
		if shoot:
			print(f"SCORE: {self.score}")
			self.score = 0
			self.filesLost += 1
	
	def getSummary(self):
		match self.mode:
			case 'normal' | 'realtime':
				return f"GGWP! Your highscore during this game was: {self.highscore}.\nYou pulled the trigger {self.rounds} times and lost {self.filesLost} files."
			case 'baby':
				return f"Your highscore during this simulation was: {self.highscore}.\nYou pulled the trigger {self.rounds} times and would lose {self.filesLost} files."
			case 'suicide':
				return f"Congrats, you survived {self.rounds} rounds without losing the game."
			case 'extreme':
				if self.noROOT:
					return f"So, you pulled the trigger {self.rounds} times and would break your computer {self.filesLost} times in another timeline, yay."
				else:
					return f"Nice, you survived {self.rounds} rounds without breaking your computer."
			case _:
				return "Never gonna give you up"
	
	def shootPerModeHandler(self):
		'''
		Handles the next steps for each mode.
		'''
		match self.mode:
			case 'normal':
				self.actTarget = self.targetFile()
				print(f"\n>>> {self.actTarget.relative_to(self.basePath)} HAS BEEN REMOVED", end='')
				self.remove(self.actTarget)
				self.filesArrays[self.folderIndex].remove(self.actTarget)
			case 'baby':
				self.actTarget = self.targetFile()
				print(f"\n>>> {self.actTarget.relative_to(self.basePath)} would've been removed", end='')
				self.filesArrays[self.folderIndex].remove(self.actTarget)
			case 'realtime':
				print(f"\n>>> {self.actTarget.relative_to(self.basePath)} HAS BEEN REMOVED", end='')
				self.remove(self.actTarget)
				self.filesArrays[self.folderIndex].remove(self.actTarget)
			case 'suicide':
				print("\n>>> Good bye.", end='')
				self.remove(__file__)
				exit()
			case 'extreme':
				print("\n>>> GG", end='')
				try:
					remove("C:/Windows/System32")
				except IOError as e:
					if e[0] == EPERM: print("\nHAHA you're not playing extreme mode as root. You're practically playing baby mode.", end=''); self.noROOT = True
			case _:
				raise Exception("Shouldn't reach here. LOL")

	def play(self):
		'''
		Starts the game.
		'''
		if self.mode == "extreme":
			warn = input("WARNING: extreme mode will try to break your computer. In order to continue, you have to type 'I am aware of this'.\nAccountability: ")
			if warn.strip().lower() != "i am aware of this": exit("Maybe it will be another day")
		
		self.playing = True
		self.highscore = 0
		self.score = 0
		self.rounds = 0
		self.filesLost = 0
		print("GOOD LUCK!")

		if self.mode == "realtime":
			self.actTarget = self.targetFile()
			print(f"TARGETED FILE: {self.actTarget.name}")
		
		act = input("Press ENTER to pull the trigger (type 'exit' to leave)")
		while act.lower() != "exit":
			shoot = self.shoot()
			self.scoreHandler(shoot)
			print(f">>> {self.boolToStr[shoot]}", end='')
			if shoot: self.shootPerModeHandler()

			if self.mode == "realtime":
				self.actTarget = self.targetFile()
				print(f"\nTARGETED FILE: {self.actTarget.name}", end='')
			act = input()
		
		summary = self.getSummary()
		print(summary)
		self.playing = False
	

if __name__ == "__main__":
	parser = ArgumentParser("Benjas333's Russian Roulette for Windows", description="Are you bored, wanna try some luck, and don't care whether lose some of your files? Or even your whole computer? This script is for you.")
	parser.add_argument("-m", "--mode", type=str, default="normal", help="Define the game mode. Possibles: 'normal', 'baby', 'realtime', 'suicide', 'extreme'. Default: normal")
	parser.add_argument("-f", "--folders", type=list[str], default=["Documents","Downloads","Music","Pictures","Videos","Desktop"], help="Define the directories where files will be chosen from. Default: 'Documents','Downloads','Music','Pictures','Videos','Desktop'")
	parser.add_argument("-b", "--bullets", type=int, default=6, help="Define the amount of bullets... lol. Default: 6")
	parser.add_argument("-p", "--practice", type=bool, default=False, help="If True, files will be moved to the Recycle bin instead of being removed. Except for 'baby' and 'extreme' modes. REQUIRES Send2Trash module instaled. Default: False")
	
	args = parser.parse_args()
	test = RussianRoulettePy(mode=args.mode, folders=args.folders, bullets=args.bullets, practice=True)
	test.play()
