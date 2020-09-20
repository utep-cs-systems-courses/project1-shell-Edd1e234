
#!/usr/bin/env python3

import os, sys, time, re

AMOUNT_OF_CHAR = 100
DEBUG = True

def parse_single_cmd(cmd):
        """
        Assumes command has already been split by '|'.

        Returns list of items. First item is args for the command to execute,
        the second and third are match objects for input and output file.
        If present of course.
        """
        if cmd[-1] == "\n":
            cmd = cmd[0:-1]

        from_file_name = to_file_name = has_directory_path = None
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
        return re.split(" +", cmd), has_to_file, from_file_name

def excute_program(single_cmd):
    """
    Will excute a program. Process should be created outside.
    """
    args, has_to_file, from_file_name = parse_single_cmd(single_cmd)
    process_flag = False

    if DEBUG:
        print("Args: ")
        print("\t",args)


    if has_to_file: # redirects for output file.
        os.close(1)
        os.open(has_to_file.groups()[1], os.O_CREAT | os.O_WRONLY)
        os.set_inheritable(1, True)

    if from_file_name: # redirects for input file.
        args.append(from_file_name)

    for dir in re.split(":", os.environ['PATH']):
        program = "%s/%s" % (dir, args[0])
        try:
            os.execve(program, args, os.environ)
        except FileNotFoundError:
            process_flag = True
            pass
    if process_flag is True:
        os.write(1, (args[0] + ": command not found\n").encode())
    sys.exit(1)

while (1):
    prompt = "$ "
    if "PS1" in os.environ:
        prompt = os.environ["PS1"]
    os.write(1, prompt.encode())
    try:
        prompt_input = os.read(0, AMOUNT_OF_CHAR)
        prompt_input = [str(chr) for chr in prompt_input.decode().split("\n")]
        if DEBUG:
            print(prompt_input)
    except EOFError:
        sys.exit(1)

    # Skips if prompt_input is empty.
    if not prompt_input:
        if DEBUG:
            os.write(2, ("Nothing was written\n").encode())

        continue

    if "exit" in prompt_input:
        sys.exit(1)

    prompt_input = ' '.join([str(chr) for chr in prompt_input])
    if DEBUG:
        print(prompt_input)

    # change directory
    if "cd" in prompt_input:
        args = prompt_input.split(" ")
        try:
            if DEBUG:
                os.write(1, ("Changing Directory").encode())
                print("Changing dir")
            os.chdir(os.getcwd() + "/" + args[1])
        except FileNotFoundError:
            os.write(2, ("cd FAILED").encode())
        continue

    rc = os.fork()
    if rc < 0:
        os.write(2, ("fork failed, returning %d\n" % rc).encode())
        sys.exit(1)
    elif rc == 0:
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
            excute_program(prompt_input)
    else:
        os.wait()
