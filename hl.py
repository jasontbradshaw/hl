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
            # args weren't hashable (ex. dicts aren't hashable) so just call f
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

def highlight(pattern, infile=sys.stdin, outfile=sys.stdout):
    """
    Read the given file line-by-line, highlighting it as specified and printing
    the highlighted output to the console.
    """

    for line in infile:

        # iterate over all the matches in our line (possibly none)
        matches = pattern.finditer(line)

        # accumulate all the match positions
        match_indexes = []
        for match in matches:
            match_indexes.append((match.start(), match.end()))

        # add the color codes all at once, so we don't have to worry about
        # regexes matching the color codes themselves if we replaced in-place.
        hl_line = []
        last_end = 0
        for start, end in match_indexes:
            # add the new parts of our highlighted line
            hl_line += line[last_end:start]
            hl_line += color(3)
            hl_line += line[start:end]
            hl_line += endc()

            # move the last end up so we can continue from there
            last_end = end

        # add the remaining unmatched part (possibly all) of the original line
        hl_line += line[last_end:]

        # write out the final, highlighted line
        outfile.write(''.join(hl_line))

if __name__ == "__main__":
    highlight(re.compile(sys.argv[1]))
