# RussianRoulettePy

Have you ever been so bored that you wouldn't mind losing some files? Check this repo!

So, I was so bored with nothing to do, then saw the next image.
![](meme.jpg)
At first, I laughed. Then, the intrusive ideas came in and... well, here we are.

## Requirements
I'm not sure. I did it in the rush. I used [Python 3.12](https://www.python.org/downloads/), I don't know if it works on older versions.

 Requires [Send2Trash](https://pypi.org/project/Send2Trash/) for 'practice' arg.
```
pip install Send2Trash
```

## Features
- Various game modes:

|Mode  | Description| Can practice? (arg) |
|------|--------------|-------------|
|normal | Normal game mode, random file removed when a shoot is executed. | **Yes**
|baby | It just doesn't remove files, but prints what file would have been removed. For babies. | **No** (unnecessary)
|realtime | Similar to normal mode, but files are targeted each round (so you'd know what you could lose before pulling the trigger). | **Yes**
|suicide | Targets the script file. | **Yes**
|extreme | Targets System32 (MUST run the script with root privileges). | Why would I move System32 to the Recycle bin?

- Especify the victim folders.
- Change amount of bullets.
- Practice flag (make files get moved to the Recycle Bin instead of getting eliminated. REQUIRES [Send2Trash](https://pypi.org/project/Send2Trash/)).
- Score and highscore system :D

## Coming Soon
- Even more game modes:

|Mode  | Description|
|------|--------------|
|hard | Instead of targeting files, targets whole parent directory of random files.
|hardrt | Hard mode realtime; i.e., directories are targeted each round before pulling the trigger.
|apps | Would remove application directories from 'Program Files' and 'Program Files (x86)' instead of 'folders' arg.
|executables | Would remove .exe files from the computer, variation of 'apps' mode.
- Maybe add global score using env variables.
- GUI Program (just to visualize the files you're gonna lose before losing them LMAO).
- Some day I'll make this shit a videogame (probably wouldn't use Python).
