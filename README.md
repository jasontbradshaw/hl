hl
----
`hl` is a small program for highlighting output on the console. Given any number
of regular expressions, it uses them to parse the text given to it and wraps the
matching sections in ANSI color code escape sequences. `hl` supports 16 and 256
color output.

Usage
----
`python hl.py REGEXP [REGEXP ...]`

Pipe the output of any program to `hl`, and it will read from the output and
print the parsed output directly to the console as it comes in.

Shortcomings
---
Currently, `hl` hardcodes the highlight color to green. In the future, support
for custom colors and per-pattern colors is planned.
