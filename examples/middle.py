from RussianRoulettePy import RussianRoulettePy

rrp = RussianRoulettePy(
        mode='baby',
        folders=['Videos'],
        bullets=5,
        practice=True
)
rrp.setShotStrings("BAD LUCK", "*nothing happens*")
rrp.startGame()
while rrp.isAGameActive():
        a = input("Pull trigger? [Y/N]: ").upper()
        responses = ['Y', 'YES', 'N', 'NO']
        while a not in responses:
                a = input("Pull trigger? [Y/N] (Enter a valid input): ").upper()
        match a:
                case 'Y' | 'YES':
                        shot = rrp.pullTrigger()
                case 'N' | 'NO':
                        rrp.finishGame()

highscore, rounds, filesLost = rrp.getActualStats()
if highscore == 69:
        print("7u7")
