#!/usr/bin/env python

import sys
import optparse
import functools
import re

def memoize(f):
    """
    Used to memoize the calls of any function with hashable arguments.
    """

    # dict where results are stored
    m = {}

    @functools.wraps(f)
    def wrapper(*args):
        try:
            # if we've already calculated the result, return it
            return m[args]
        except KeyError:
            # otherwise, calculate the result, store it, then return it
            result = f(*args)
            m[args] = result
            return result
        except TypeError:
            # args we're hashable, ex. dicts aren't hashable, so just call f
            return f(*args)

    return wrapper

@memoize
def color(fg_color, bg_color=None):
    """
    Returns a string representing the begin code for the given color. This stays
    in effect until the reset code is used or the color is changed.
    """

    # we return only the first 3 items if there's no bg color, else all of it
    if bg_color is None:
        return "\033[38;5;" + str(fg_color) + "m"
    else:
        return "\033[38;5;" + str(fg_color) + "m\033[48;5;" + str(bg_color) + "m"

def endc():
    """
    Returns a string representing the end code for a color escape sequence. This
    resets all color changes back to the default.
    """

    # 0 is the reset code, so we reset all attributes
    return "\033[0;0;0m"

def stress_test(iters):
    """
    Stress test the color generating function. We want this to be fast, baby.
    """

    # test our efficiency
    for i in xrange(iters):
        for c in xrange(256):
            color(c)

def rainbow():
    """
    Print a nice rainbow of colors to the terminal.
    """

    # print a fabulous rainbow of colors!
    for c in xrange(256):
        print color(0, c) + str(c).center(3) + endc()

def main(infile):
    """
    Read the given file line-by-line, highlighting it as specified and printing
    the highlighted output to the console.
    """

    for line in infile:
        print repr(line)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r') as f:
            main(f)
    else:
        main(sys.stdin)
