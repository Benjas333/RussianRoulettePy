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

class RussianRoulettePy(object):
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
			"normal" - Normal game mode, random file removed when a shot is executed.
			
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
		# [ ]: Add new game modes when ready
		indexingModes = ['normal', 'baby', 'realtime']
		otherModes = ['suicide', 'extreme']
		if mode.lower() not in indexingModes and mode.lower() not in otherModes:
			raise Exception("Unknown game mode.")
		self.__mode = mode.lower()

		logging.info(f"{datetime.now()}| Initializing RussianRoulettePy {self.__mode} game")
		print(f"------------ RUSSIAN ROULETTE ({self.__mode} mode) ------------\nLoading... ", end='')
		
		self.bullets = bullets
		self.__boolToStr = {
			True: "BOOM",
			False: "PASS"
		}
		self.__actTarget = None

		self.__playing = False
		self.__highscore = 0
		self.__score = 0
		self.__rounds = 0
		self.__filesLost = 0

		self.__noROOT = False # FIXME: this should be better done xd

		if practice:
			from send2trash import send2trash
			self.__remove = send2trash
		else:
			self.__remove = remove
		
		# [ ]: Not ready yet.
		self.__basePath = "C:/"
		self.__folders = [""]
		if self.__mode == "apps":
			self.__folders = ["Program Files", "Program Files (x86)"]
		if self.__mode in indexingModes:
			user = getuser()
			self.__basePath = f"C:/Users/{user}"
			if not len(folders):
				raise Exception("folders arg cannot be empty. I think you can make [''], but no empty dude.")
			self.__folders = folders		
		
		self.__extension = "*"
		if self.__mode == 'executables':
			self.__extension = "exe"
		
		
		# TODO: ADD indexing dir for hard, hardrt and apps
		if self.__mode in indexingModes or self.__mode == 'executables':
			self.__paths = list(map(lambda a: f"{self.__basePath}/{a}", self.__folders))

			self.__queryStr = f'**/*.{self.__extension}'
			self.__scanSubdirs = True

			logging.info(f"{datetime.now()}| Indexing files...")
			# TODO: Change to private method in order to use it on the future changeMode method
			self.__filesArrays = list(filter(lambda a: len(a) > 0, map(lambda a: glob(f"{(Path(a) / f"{self.__queryStr}").resolve()}", recursive=self.__scanSubdirs), self.__paths)))
			# print(self.__filesArrays) # XXX: remove later
			# self.files = reduce(lambda a, b: a + b, self.foldersArray) # XXX: probably not necessary anymore
			logging.info(f"{datetime.now()}| Indexed {reduce(lambda x, y: x + y, map(lambda a: len(a), self.__filesArrays))} files")
		
		print("Ready to play.")

	def __targetFile(self) -> tuple[str | None, int | None]:
		'''
		Targets a file to remove.

		return Path - if found

		return None - if no more files to play with.
		'''
		if not self.__playing:
			return None, None
		folderIndex = randint(0, len(self.__filesArrays) - 1)
		file = choice(self.__filesArrays[folderIndex])
		if not Path(file).exists():
			logging.error(f"{datetime.now()}| {file} targeted, but does not exists")
			self.__removeElementsHandler(file, folderIndex)
			file, folderIndex = self.__targetFile()
		logging.info(f"{datetime.now()}| {file} targeted")
		return file, folderIndex
	
	def __shoot(self) -> bool:
		'''
		Executes a shot.

		return bool
		'''
		if randint(0, self.bullets) == 1:
			shot = True
		else:
			shot = False
		logging.info(f"{datetime.now()}| {self.__boolToStr[shot]}")
		return shot
	
	def __scoreHandler(self, shot: bool):
		'''
		Handles the score functionality.
		'''
		self.__rounds += 1
		self.__score += 1
		if self.__score > self.__highscore: self.__highscore = self.__score
		if shot:
			print(f"SCORE: {self.__score}")
			self.__score = 0
			self.__filesLost += 1
	
	def __getSummary(self) -> str:
		'''
		Basic strings with a summary of the game final stats.

		return str
		'''
		match self.__mode:
			case 'normal' | 'realtime':
				return f"GGWP! Your highscore during this game was: {self.__highscore}.\nYou pulled the trigger {self.__rounds} times and lost {self.__filesLost} files."
			case 'baby':
				return f"Your highscore during this simulation was: {self.__highscore}.\nYou pulled the trigger {self.__rounds} times and would lose {self.__filesLost} files."
			case 'suicide':
				return f"Congrats, you survived {self.__rounds} rounds without losing the game."
			case 'extreme':
				if self.__noROOT:
					return f"So, you pulled the trigger {self.__rounds} times and would break your computer {self.__filesLost} times in another timeline, yay."
				else:
					return f"Nice, you survived {self.__rounds} rounds without breaking your computer."
			case _:
				return "Never gonna give you up"
	
	def __removeElementsHandler(self, file: str, index: int):
		'''
		Handles the removement of elements in lists n stuff.

		If there's no more files to play with, calls __forceFinishGame method.
		'''
		folder = self.__filesArrays[index]
		folder.remove(file)
		logging.info(f"{datetime.now()}| {file} removed from the array.")
		if not len(folder):
			folderName = self.__paths[index]
			self.__paths.remove(folderName)
			self.__filesArrays.remove(folder)
			logging.warn(f"{datetime.now()}| {folderName} removed from paths because of being empty.")
		if not len(self.__filesArrays):
			print("There's no more files to play with.")
			logging.warn(f"{datetime.now()}| There's no more files to play with.")
			self.__forceFinishGame()
			logging.warn(f"{datetime.now()}| Game ended earlier.")

	def __realtimeModeExtra(self):
		'''
		Extra stuff for the realtime mode execution.
		'''
		if not self.__playing:
			return
		if self.__mode == "realtime":
			self.__actTarget, self.__folderIndex = self.__targetFile()
			if self.__actTarget is None: return
			print(f"\nTARGETED FILE: {Path(self.__actTarget).relative_to(self.__basePath)}")

	def __shotPerModeHandler(self):
		'''
		Handles the next steps of a shot for each mode.
		'''
		match self.__mode:
			case 'normal' | 'baby':
				self.__actTarget, self.__folderIndex = self.__targetFile()
				if self.__actTarget is None: return
			case 'suicide':
				self.__actTarget = __file__
			case 'extreme':
				try:
					remove("C:/Windows/System32")
				except IOError as e:
					if e[0] == EPERM:
						print("HAHA you're not playing extreme mode as root. You're practically playing baby mode.")
						self.__noROOT = True
				finally:
					return
		
		shotDialogsVars = {
			'normal': Path(self.__actTarget).relative_to(self.__basePath),
			'baby': Path(self.__actTarget).relative_to(self.__basePath),
			'realtime': Path(self.__actTarget).name,
			'suicide': '',
			'extreme': ''
		}
		shotDialogs = {
			'normal': ' HAS BEEN REMOVED',
			'baby': " would've been removed",
			'realtime': " HAS BEEN REMOVED",
			'suicide': 'Good bye.',
			'extreme': 'GG'
		}
		print(f">>> {shotDialogsVars[self.__mode]}{shotDialogs[self.__mode]}")
		if self.__mode != 'baby':
			self.__remove(self.__actTarget)
		
		if self.__mode == 'suicide':
			exit()
		self.__removeElementsHandler(self.__actTarget, self.__folderIndex)
	
	def isAGameActive(self) -> bool:
		'''
		Whether or not a game is in progress.

		return bool
		'''
		return self.__playing
	
	def getActualTarget(self) -> Path | None:
		'''
		Returns the actual actTarget value. actTarget is the file/dir that the game is targeting to remove.

		return Path - not necessarily still exists, depends on the game mode.
		
		return None - not necessarily means the game is over. Check isAGameActive method.
		'''
		return self.__actTarget
	
	def getMode(self) -> str:
		'''
		Returns the actual configured game mode.

		return str
		'''
		return self.__mode
	
	def getBasePath(self) -> str:
		'''
		Returns the base Path used in the files scan.

		return str
		'''
		return self.__basePath
	
	def getPaths(self) -> list[str]:
		'''
		Returns a list with the active main folders that'll be used in games.

		return list[str]
		'''
		return self.__paths
	
	def getActualStats(self) -> tuple[int, int, int]:
		'''
		Returns a tuple with the highscore, rounds, and filesLost actual values.

		return tuple[int, int, int]
		'''
		return self.__highscore, self.__rounds, self.__filesLost
	
	def shotToStr(self, value: bool) -> str:
		'''
		Turns shot value to string.

		return str
		'''
		return self.__boolToStr[value]
	
	def setShotStrings(self, shot: str = "BOOM", noShot: str = "PASS"):
		'''
		Change the default values for the strings linked to shots.
		Default:
			shot: True = BOOM
			noShot: False = PASS
		'''
		self.__boolToStr = {
			True: shot,
			False: noShot
		}
	
	# TODO: add changeMode method

	def startGame(self) -> str | None:
		'''
		Initializes everything that's necessary to start playing.

		return None - There's already a game in execution.

		return str - The game mode that's actually being played.
		'''
		if self.__playing:
			logging.warn(f"{datetime.now()}| (startGame method) There's already a game in execution.")
			return None
		
		self.__playing = True
		self.__highscore = 0
		self.__score = 0
		self.__rounds = 0
		self.__filesLost = 0
		print("GOOD LUCK!")

		self.__realtimeModeExtra()
		logging.info(f"{datetime.now()}| Sucessfully game started.")
		return self.__mode
	
	def pullTrigger(self) -> bool | None:
		'''
		Pulls the trigger, what represents a round execution.

		return bool - Whether or not was a shot.

		return None - There's not any game in execution.
		'''
		if not self.__playing:
			logging.warn(f"{datetime.now()}| (pullTrigger method) There's not any game in execution.")
			return None
		shot = self.__shoot()
		self.__scoreHandler(shot)
		print(f">>> {self.__boolToStr[shot]}")
		if shot: self.__shotPerModeHandler()

		self.__realtimeModeExtra()
		return shot

	def __forceFinishGame(self):
		'''
		Forces the actual game to finish, kinda.
		'''
		summary = self.__getSummary()
		print(summary)
		self.__playing = False
	
	def finishGame(self) -> tuple[int, int, int] | None:
		'''
		Finishes the game and returns stats as getActualStats method do.

		return tuple[int, int, int] - highscore, rounds, filesLost

		return None - There's not any game in execution.
		'''
		if not self.__playing:
			logging.warn(f"{datetime.now()}| (endGame method) There's not any game in execution.")
			return None
		self.__forceFinishGame()
		logging.info(f"{datetime.now()}| Game ended sucessfully.")
		return self.__highscore, self.__rounds, self.__filesLost

	def playOnCMD(self):
		'''
		startGame, pullTrigger, and finishGame methods put together with a while loop and inputs.
		For those who want to play rn in cmd or terminal.
		'''
		if self.__mode == "extreme":
			warn = input("WARNING: extreme mode will try to break your computer. In order to continue, you have to type 'I am aware of this'.\nAccountability: ")
			if warn.strip().lower() != "i am aware of this": exit("Maybe it will be another day")
		
		self.startGame()
		
		act = input("Press ENTER to pull the trigger (type 'exit' to leave)")
		while act.lower() != "exit" and self.__playing:
			
			self.pullTrigger()

			act = input()
		
		self.finishGame()
	

if __name__ == "__main__":
	parser = ArgumentParser("Benjas333's RussianRoulettePy", description="Are you bored, wanna try some luck, and don't care whether lose some of your files? Or even your whole computer? This script is for you.")
	parser.add_argument("-m", "--mode", type=str, default="normal", help="Define the game mode. Possibles: 'normal', 'baby', 'realtime', 'suicide', 'extreme'. Default: normal")
	parser.add_argument("-f", "--folders", type=list[str], default=["Documents","Downloads","Music","Pictures","Videos","Desktop"], help="Define the directories where files will be chosen from. Default: 'Documents','Downloads','Music','Pictures','Videos','Desktop'")
	parser.add_argument("-b", "--bullets", type=int, default=6, help="Define the amount of bullets... lol. Default: 6")
	parser.add_argument("-p", "--practice", type=bool, default=False, help="If True, files will be moved to the Recycle bin instead of being removed. Except for 'baby' and 'extreme' modes. REQUIRES Send2Trash module instaled. Default: False")
	
	args = parser.parse_args()
	test = RussianRoulettePy(mode=args.mode, folders=args.folders, bullets=args.bullets, practice=True)
	test.playOnCMD()
