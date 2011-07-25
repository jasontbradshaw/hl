#!/usr/bin/env python

import sys
import optparse
import functools
import re
import time

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
def make_color(fg_color, bg_color=None):
    """
    Returns a string representing the begin code for the given color. This stays
    in effect until the reset code is used or the color is changed.
    """

    # build and return the minimum viable color string for the requested color
    if bg_color is None:
        # we don't need the background color if none was specified
        return "\033[38;5;" + str(fg_color) + "m"
    else:
        # if both were specified, put the two colors together
        return "\033[38;5;" + str(fg_color) + "m\033[48;5;" + str(bg_color) + "m"

def make_endc():
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
            make_color(c)

def rainbow():
    """
    Print a nice rainbow of colors to the terminal.
    """

    # print a fabulous rainbow of colors!
    print "Standard colors:"
    for c in xrange(256):
        # add a break and heading after the standard colors
        if c == 16:
            print
            print "Extetitlended colors:"

        print str(c).rjust(3) + ": " + make_color(0, c) + (" " * 5) + make_endc()

class Highlighter:
    """
    Builds an object that highlights a given string using supplied patterns and
    colors.
    """

    def __init__(self, default_color=(0, 10)):
        # black text, green highlight as default
        self.default_color = default_color

        # all the patterns and their colors that we'll match against
        self.patterns = []

    def add_pattern(self, pattern, color=None):
        """
        Adds a pattern and an optional color for the pattern. 'pattern' is
        either a string or a compiled regular expression, and 'color' is a tuple
        of (foreground color, background color).
        """

        # determine if the pattern is a compiled regex and compile if necessary
        our_pattern = pattern
        if not hasattr(pattern, "finditer"):
            our_pattern = re.compile(pattern)

        # use the default color if none was supplied
        our_color = self.default_color
        if color is not None:
            our_color = color

        # add the compiled regex and its color tuple to our list
        self.patterns.append((our_pattern, our_color))

    def highlight(self, text):
        """
        Takes a text string and highlights it with all the supplied patterns,
        returning the highlighted result.
        """

        match_indexes = []
        for pattern, color in self.patterns:
            # iterate over all the matches in our text (possibly none)
            matches = pattern.finditer(text)

            # accumulate all the match positions as (start, end, color)
            for match in matches:
                m = (match.start(), match.end(), color)
                match_indexes.append(m)

        # sort matches by their beginning indexes
        # TODO: make overlapping matches work!
        match_indexes = sorted(match_indexes, key=(lambda x: x[0]))

        # add the color codes all at once, so we don't have to worry about
        # regexes matching the color codes themselves if we replaced in-place.
        hl_text = []
        last_end = 0
        for start, end, color in match_indexes:
            # add the new parts of our highlighted text
            hl_text += text[last_end:start]
            hl_text += make_color(*color)
            hl_text += text[start:end]
            hl_text += make_endc()

            # move the last end up so we can continue highlighting from there
            last_end = end

        # add the remaining unmatched part (possibly all) of the original text
        hl_text += text[last_end:]

        # assemble and return the highlighted text
        return ''.join(hl_text)

def highlight_file(highlighter, infile, outfile):
    """
    Read the given input file line-by-line, highlighting it as specified and
    write the highlighted output to the given output file.
    """

    # highlight and write out every line in the file
    for line in infile:
        outfile.write(highlighter.highlight(line))

if __name__ == "__main__":
    # test the efficiency of our highlighting function
    if len(sys.argv) == 2 and sys.argv[1] == "stresstest":
        iters = 50000
        print "Stressing for %d iterations..." % iters
        start_time = time.time()
        stress_test(iters)
        end_time = time.time()

        print "%.3f seconds" % (end_time - start_time)

    elif len(sys.argv) == 2 and sys.argv[1] == "rainbow":
        # print a pretty rainbow to the console
        rainbow()

    else:
        # add all the supplied patterns to the highlighter
        hl = Highlighter()
        for pattern in sys.argv[1:]:
            hl.add_pattern(pattern)

        # highlight stdin and write to stdout using our highlighter
        highlight_file(hl, sys.stdin, sys.stdout)
