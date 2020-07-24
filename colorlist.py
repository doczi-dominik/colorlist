#!/usr/bin/env python3
import argparse
import re
import os.path as osp

from sys import exit as sysexit, argv
from os import getenv
from tempfile import NamedTemporaryFile
from shlex import split as shsplit
from subprocess import Popen
from threading import Thread

import src.helpers as helpers
from src.color import Color

#############
# CONSTANTS #
#############

PROG_PATH = osp.dirname(osp.abspath(argv[0]))


############
# ARGPARSE #
############

# Set up parser
parser = argparse.ArgumentParser(
    prog="colorlist",
    description="Extract and show colors in an HTML document")

# Add options
parser.add_argument(
    "-p",
    "--program",
    help="The program used to open the HTML doc by passing the filename to $1. (default: $BROWSER)",
    default=getenv("BROWSER"),
    metavar="CMD")
parser.add_argument(
    "-s",
    "--stdout",
    help="Output all colors in a text-based format to STDOUT",
    action="store_true")
parser.add_argument(
    "-ab",
    "--args-before",
    help="Extra arguments to pass to the program before the HTML doc",
    metavar="ARGS")
parser.add_argument(
    "-aa",
    "--args-after",
    help="Extra arguments to pass to the program after the HTML doc",
    metavar="ARGS")
parser.add_argument(
    "-f",
    "--format",
    help=r"Search for the specified color format. Can be specified repeatedly. [r,g,b,a: Decimal value][R,G,B,A: Single digit hex value][Escape values using '\'] E.g.: #0A0B0C matches '#RRGGBB'; argb(255, 0, 255, 127) matches '\a\r\g\b(a, r, g, b)'",
    action="append")
parser.add_argument(
    "-t",
    "--template",
    help="The name of the HTML template to use (default: default)",
    default="default",
    metavar="TEMP")
parser.add_argument(
    "-o",
    "--out",
    help="Output HTML to FILE ('-' for STDOUT) instead of opening a program",
    metavar="FILE/-")
parser.add_argument(
    "-C",
    "--no-cleanup",
    help="Disable cleanup operations in '/tmp'",
    action="store_true")
parser.add_argument(
    "-q",
    "--quiet",
    help="Suppress error messages",
    action="store_false",
    dest="enable_warns")

# Add positionals
parser.add_argument(
    "source",
    help="The plaintext or file ('-' for STDIN) to extract colors from (default: '-')",
    default="-",
    nargs="?")

args = parser.parse_args()

########
# MAIN #
########


def main():
    # Clean up leftover files in /tmp on
    # a separate thread
    cleanup_thread = Thread(
        target=helpers.tmp_cleanup,
        args=(args.no_cleanup, args.enable_warns))
    cleanup_thread.start()

    # Convert format strings to regex patterns
    patterns = {}
    format_list = args.format or ["#RRGGBB"]

    replacements = {
        r"(?<!\\)[rgba]": r"([0-9]+)",
        r"(?<!\\)[RGBA]": r"([0-9a-fA-F])",
        r"\\\\([RGBArgba])": r"\1"}

    for format in format_list:
        escaped_format = re.escape(format)

        format_tokens = re.findall(r"((?<!\\)[RGBArgba])", escaped_format)

        # Check for errors
        str_tokens = "".join(format_tokens)
        test_letters = "RGB" if str_tokens.isupper() else "rgb"

        for letter in test_letters:
            if letter not in str_tokens:
                sysexit(f"ERROR - Invalid format '{format}' - '{letter}' not found")

        for letter in str_tokens:
            min = 0 if letter in "aA" else 1
            max = 2 if letter in "RGBA" else 1

            if len(re.findall(letter, str_tokens)) not in range(min, max + 1):
                sysexit(f"ERROR - Invalid format '{format}' - '{letter}' occurences not in range: [{min};{max}]")

        if not str_tokens.isupper() and not str_tokens.islower():
            sysexit(f"ERROR - Invalid format '{format}' - Hex and decimal values clash")


        # Associate provided format with a matching
        # regexp pattern and a list of tokens
        patterns[format] = (
            format_tokens,
            helpers.multi_replace(escaped_format, replacements))

    if args.source == "-":
        try:
            source_text = input()
        except KeyboardInterrupt:
            sysexit(1)

        source_type = "stdin"
    elif osp.isfile(args.source):
        try:
            with open(args.source) as f:
                source_text = f.read()
        except OSError as err:
            sysexit(f"ERROR - Could not read '{args.source}' - {err.strerror}")

        source_type = "file"
    else:
        source_text = args.source
        source_type = "text"

    # Find and match strings from the source
    colors = {}

    for format, tuple_ in patterns.items():
        tokens, pattern = tuple_

        colors[format] = []

        # Collect values into a dict
        for match in re.finditer(pattern, source_text, re.IGNORECASE):
            values = match.groups()

            # Remove the first "whole match" group
            # (see: re.Match.group() on Python Docs)
            if len(values) > len(tokens):
                values = values[1:]

            groupped = {}
            color_dict = {}

            for i in range(len(values)):
                token = tokens[i]
                value = values[i]

                # Group all occurences of a value
                # by token
                if token not in groupped:
                    groupped[token] = []

                groupped[token].append(value)

                # Hex values
                if token.isupper():
                    color_dict[token] = int("".join(groupped[token]), 16)
                # Decimal values
                else:
                    color_dict[token] = int(groupped[token][0])

            # Support for short hex notation (#RGB)
            for token in groupped:
                if token.isupper() and len(groupped[token]) < 2:
                    digit = groupped[token][0]
                    color_dict[token] = int(f"0x{digit}{digit}", 16)

            # Create and addcolor value
            # from dict of values
            colors[format].append(Color(match[0], color_dict))

        # Filter duplicates
        colors[format] = list(set(colors[format]))

    # Wait for cleanup thread to finish
    cleanup_thread.join()

    ####################
    # TEXT OUTPUT MODE #
    ####################

    if args.stdout:
        for format, color_list in colors.items():
            print(format)
            print("-" * len(format))

            for color in color_list:
                print(color)

            print()

        sysexit()

    # Read templates
    template_dir = osp.join(PROG_PATH, "templates", args.template)

    try:
        with open(osp.join(template_dir, "page.html")) as f:
            base_template = f.read()
    except OSError as err:
        sysexit(f"ERROR - Could not read page template '{args.template}/page.html' - {err.strerror}")

    try:
        with open(osp.join(template_dir, "color.html")) as f:
            color_template = f.read()
    except OSError as err:
        sysexit(f"ERROR - Could not read color template '{args.template}/color.html': {err.strerror}")

    # Collect colors into a large string
    html_colors = ""
    for format, color_list in colors.items():
        for color in color_list:
            html_colors += color.as_html(color_template)

    # Insert the list into the base
    list_token_pattern = re.compile(r"(?<!\[)\[list\](?!\])")

    if not list_token_pattern.search(base_template):
        helpers.warn(args.enable_warns, "Placeholder [list] not found in 'page.html'. No colors will be shown")

    full_html = list_token_pattern.sub(html_colors, base_template)

    # Convert escaped [] to normal
    full_html = re.sub(r"\[\[(.*)\]\]", r"[\1]", full_html)

    ####################
    # FILE OUTPUT MODE #
    ####################

    if args.out == "-":
        print(full_html)
        sysexit()
    elif args.out:
        try:
            with open(args.out, "w") as f:
                f.write(full_html)
        except OSError as err:
            sysexit(f"ERROR - Could not write '{args.out}' - {err.strerror}")

        sysexit()

    #####################
    # OPEN PROGRAM MODE #
    #####################

    # Check for provided program
    if not args.program:
        sysexit("ERROR - Could not read $BROWSER. Please specify a program manually using --program / -p")

    # Determine filename prefix
    if source_type == "stdin":
        temp_prefix = "colorlist_STDIN_"
    elif source_type == "file":
        temp_prefix = f"colorlist_{osp.basename(args.source)}_"
    else:
        temp_prefix = "colorlist_TEXT_"

    # Write HTML to tempfile
    temp_file = NamedTemporaryFile(
        mode="w",
        prefix=temp_prefix,
        delete=False)
    temp_file.write(full_html)

    # Assemble command line and open command
    prefix_args = shsplit(args.args_before or "")
    postfix_args = shsplit(args.args_after or "")

    command = [args.program] + prefix_args + [temp_file.name] + postfix_args

    try:
        Popen(command)
    except OSError as err:
        sysexit(f"ERROR - Could not run '{' '.join(command)}' - {err.strerror}")


if __name__ == "__main__":
    main()
