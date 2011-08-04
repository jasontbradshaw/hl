#!/usr/bin/env python

import sys
import re

def memoize(f):
    """
    Used to memoize the calls of any function with hashable arguments.
    """

    # dict where results are stored
    m = {}

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
def make_color(fg_color=None, bg_color=None):
    """
    Returns a string representing the begin code for the given color. This stays
    in effect until the reset code is used or the color is changed. Colors are
    created via the ANSI color escape codes.

    Since this gets memoized, its efficiency isn't quite as important as you'd
    think, but we'll still try to keep it relatively efficent.

    See http://en.wikipedia.org/wiki/ANSI_escape_code#Colors for details on ANSI
    color escape codes.
    """

    # store the incomplete color specification string
    result = []

    # add a foreground color if one is specified
    if fg_color is not None:
        result += "\033[38;5;"
        result += str(fg_color)
        result += "m"

    # add a background color if one is specified
    if bg_color is not None:
        result += "\033[48;5;"
        result += str(bg_color)
        result += "m"

    return ''.join(result)

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

        # get all the match indexes 
        match_indexes = self.__get_match_indexes(self.patterns, text)

        # add the color codes all at once, so we don't have to worry about
        # regexes matching the color codes themselves if we'd replaced in-place.
        hl_text = []
        last_index = 0
        for index, color in match_indexes:
            # add the new parts of our highlighted text
            hl_text += text[last_index:index]
            hl_text += color

            # move the last end up so we can continue highlighting from there
            last_index = index

        # add the remaining unmatched part (possibly all) of the original text
        hl_text += text[last_index:]

        # assemble and return the highlighted text
        return ''.join(hl_text)

    def __get_match_indexes(self, patterns, text):
        """
        Iterate over all the matches in a text (possibly none) to accumulate all
        the match positions as (index, color). Accumulating start and end
        indexes separately allows us to have overlapping matches without
        duplicating text.

        Returns a sorted list of unique start and end indexes paired with their
        respective colors.
        """

        # keep a set of indexes so we don't insert duplicate text
        match_indexes = set([])
        for pattern, color in patterns:
            for match in pattern.finditer(text):
                # accumulate by individual groups if there are any or multiple
                group_count = len(match.groups())
                if group_count > 0:
                    # we skip group 0 because it's just the entire match
                    for g in xrange(1, group_count + 1):
                        # add each group individually
                        match_indexes.add((match.start(g), make_color(*color)))
                        match_indexes.add((match.end(g), make_endc()))
                else:
                    # just add the entire match otherwise
                    match_indexes.add((match.start(), make_color(*color)))
                    match_indexes.add((match.end(), make_endc()))

        # sort the indexes by appearance order so matches can safely overlap
        return sorted(list(match_indexes))

def highlight_file(highlighter, infile, outfile):
    """
    Read the given input file line-by-line, highlighting it as specified and
    write the highlighted output to the given output file.
    """

    # loop over the file in a while loop, since this prevents python from
    # buffering the input. we don't want this to change a program's output
    # characteristics, after all.
    line = None
    while line != "":
        # read a line, write it to output, then flush the output
        line = infile.readline()
        outfile.write(highlighter.highlight(line))

if __name__ == "__main__":
    import time
    import optparse

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
        try:
            highlight_file(hl, sys.stdin, sys.stdout)
        except KeyboardInterrupt:
            # exit when the user kills the app
            sys.exit(0)
