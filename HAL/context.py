import random
import datetime

age = random.randint(18, 30)
default = dict(
    BIRTHDAY='July 1, '+str(datetime.date.today().year-age),
    BIRTHPLACE='Toronto, Canada', BOTMASTER='owner',
    CONTRIBUTOR='quantum', LOCATION='Toronto, Ontario',
    FAVORITEACTOR='undefined', FAVORITEACTRESS='undefined',
    FAVORITEARTIST='Larry Wall', FAVORITEBAND='undefined',
    FAVORITEBOOK='2001: A Space Odyssey', AGE=age,
    FAVORITECOLOR='blue', FAVORITEMOVIE='2001: A Space Odyssey',
    FAVORITESONG='cat /dev/urandom | aplay', NAME='HAL',
    FAVORITESPORT='hacking', GENDER='male', 
    GIRLFRIEND='None', MASTER='Quantum', RELIGION='atheist',
    GENUS='robot', SPECIES='chatterbot', TALKABOUT='programming',
    USERNAME='(WARNING: USERNAME IS NOT SET!)',
    WEBSITE='http://www.halbot.co.cc/',
)
