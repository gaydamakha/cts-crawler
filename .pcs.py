'''
PyLint score checker. Returns 0 if the pylint score is greater than the one
specified below. This script allows us to use pylint normally with all the
standard paramaters.
'''
from re import findall
from sys import exit as sysexit

MIN_SCORE = 7.0

with open('.pylint.log') as plfh:
    try:
        SCORE_LINE = plfh.readlines()[-2]
        SCORE = float(findall(r'([\-0-9\.]+)/10', SCORE_LINE)[0])
        sysexit(0 if SCORE > MIN_SCORE else 1)
    except IndexError as exception:
        print("{}".format(exception))
