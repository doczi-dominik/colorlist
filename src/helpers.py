import re

from os import listdir, remove
from sys import stderr, exit as sysexit
from os.path import join as ospjoin

if __name__ == "__main__":
    sysexit("This is a helper module for 'colorlist.py'. Please avoid running it as a script.")


def multi_replace(string, repls):
    for pattern, repl in repls.items():
        string = re.sub(pattern, repl, string)

    return string


def warn(print_warning, string):
    if print_warning:
        stderr.write(f"WARNING - {string}\n")


def tmp_cleanup(disabled, print_warning):
    if disabled:
        return

    tmp = [x for x in listdir("/tmp") if re.match(r"^colorlist_.*", x)]

    if len(tmp) > 5:
        warn(print_warning, "Performing cleanup in '/tmp'...")

        try:
            for file in tmp:
                path = ospjoin("/tmp", file)

                remove(path)
        except OSError as err:
            warn(print_warning, f"Could not perform cleanup: {err.strerror}")

            return
