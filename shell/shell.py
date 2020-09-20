#!/usr/bin/env python3

import os, sys, time, re

AMOUNT_OF_CHAR = 10000
DEBUG = False

def excute_program(args):
    """
    Will excute a program. Process should be created outside.
    """
    process_flag = False
    if DEBUG:
        os.write(1,"Args: ".encode())
        os.write(1, ("\t" + str(args) + "\n").encode())

    try:
        if '>' in args: # redirects for output.txt
            os.close(1)
            os.open(args[args.index('>') + 1], os.O_CREAT | os.O_WRONLY)
            os.set_inheritable(1, True)
            args.remove(args[args.index('>') + 1])
            args.remove('>')

        if '<' in args: # redirects for input file.
            os.close(0)
            os.open(args[args.index('<') + 1], os.O_RDONLY)
            os.set_inheritable(0, True)
            args.remove(args[args.index('<') + 1])
            args.remove('<')

    except IndexError:
        if DEBUG:
            os.write(1,"Nothing comes up.")

    for dir in re.split(":", os.environ['PATH']):
        program = "%s/%s" % (dir, args[0])
        try:
            os.execve(program, args, os.environ)
            process_flag = True
        except FileNotFoundError:
            pass
        if process_flag is True:
            os.write(1, (args[0] + ": command not found\n").encode())
    sys.exit(1)

def run_command(prompt_input):

        rc = os.fork()
        if rc < 0:
            os.write(2, ("fork failed, returning %d\n" % rc).encode())
            sys.exit(1)
        elif rc == 0:
            if DEBUG:
                os.write(1,"inside rc\n".encode())

            if "|" in prompt_input:
                pipe = prompt_input.split("|")
                cmd_1 = pipe[0].split()
                cmd_2 = pipe[1].split()

                pr, pw = os.pipe() # file descriptors for reading and writing.
                for file_descriptor in (pr, pw):
                    os.set_inheritable(file_descriptor, True)

                pipe_rc = os.fork()
                if pipe_rc < 0:
                    os.write(2, ("fork FAILED").encode())
                    sys.exit(1)

                elif pipe_rc == 0:
                    os.close(1)
                    os.dup(pw)
                    os.set_inheritable(1, True)
                    for file_descriptor in (pr, pw):
                        os.close(fd)
                    excute_program(cmd_1)
                else:
                    os.close(0)
                    os.dup(pr)
                    os.set_inheritable(0, True)
                    for file_descriptor in (pw, pr):
                        os.close(file_descriptor)
                    excute_program(cmd_2)
            else:
                if DEBUG:
                    os.write(1,"EXCUTE PROGRAM".encode())
                    os.write(1, (str(prompt_input) + "\n").encode())
                excute_program(prompt_input)
        else:
            os.wait()


while (1):
    prompt = "$ "
    if "PS1" in os.environ:
        prompt = os.environ["PS1"]
    os.write(1, prompt.encode())
    try:
        prompt_input = os.read(0, AMOUNT_OF_CHAR)
        prompt_input = prompt_input.decode().split("\n")
        if DEBUG:
            os.write(1,("Right After prompt\n").encode())
            os.write(1, (str(prompt_input) + "\n").encode())
    except EOFError:
        sys.exit(1)

    # Skips if prompt_input is empty.
    if prompt_input == ['', '']:
        if DEBUG:
            os.write(2, ("Nothing was written\n").encode())
        continue

    if "exit" in prompt_input:
        sys.exit(1)

    prompt_input[0] = prompt_input[0].split()

    if DEBUG:
        os.write(1, ("Moving into cd..").encode())
        os.write(1, (str(prompt_input) + "\n").encode())

    # change directory
    if "cd" in prompt_input[0]:
        args = prompt_input[0]
        try:
            if DEBUG:
                os.write(1, ("Changing Directory\n" + args[1] + "\n").encode())
            os.chdir(args[1])
        except FileNotFoundError:
            os.write(2, ("cd FAILED").encode())
        continue

    if DEBUG:
        os.write(1, (str(prompt_input) + "\n").encode())
    for arg in prompt_input:
        if "" in arg:
            continue
        if DEBUG:
            os.write(1, ("AFTER COMBINE").encode())
            os.write(1, (str(prompt_input) + "\n").encode())
        run_command(arg)
