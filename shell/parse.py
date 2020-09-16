import sys
import re

def parse(cmd):
    """
    Assumes command has already been split by '|'.
    """

    if cmd[-1] == "\n":
        cmd = cmd[0:-1]

    from_file_name = to_file_name = None
    cmd = " " + cmd + " "

    # isolate < from_file_name
    from_file_name = re.match("([^<]+)<[ ]*([^ ]*)(.*)", cmd)

    if from_file_name:
        pre, from_file_name, post = from_file_name.groups()
        cmd = pre + " " + post

    # isolate > to_file_name
    has_to_file = re.match("([^>]+)>[ ]*([^ ]*)(.*)", cmd)
    if has_to_file:
        pre, to_file_name, post = has_to_file.groups()
        cmd = pre + " " + post

    cmd = re.sub(" +", " ", cmd) # remove extra spaces between tokens
    cmd = cmd[1:-1]
    return re.split(" +", cmd), from_file_name, has_to_file

print(parse("ls -l > output.txt\n"))
