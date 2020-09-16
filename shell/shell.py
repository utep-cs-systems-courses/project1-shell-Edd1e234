import os, sys, time, re

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
    Will excute a program. In process.
    """
    args, has_to_file, from_file_name = parse_single_cmd(single_cmd)
    print("Args are: ")
    print(args)
    print(has_to_file)

    process_flag = False
    if has_to_file:
        os.close(1)
        os.open(has_to_file.groups()[1], os.O_CREAT | os.O_WRONLY)
        os.set_inheritable(1, True)
    if from_file_name:
        args.append(from_file_name)

    for dir in re.split(":", os.environ['PATH']):
        program = "%s/%s" % (dir, args[0])
        try:
            process_flag = True
            os.execve(program, args, os.environ)
        except FileNotFoundError:
            pass
    if process_flag:
        print("'" + args[0] +"' command not found.")
    sys.exit(1)

while (1):
    if os.environ.get('$PS1') != None:
        prompt_input = input(os.environ['$PS1']) # Add input.
    else:
        prompt_input = input("$ ")

    if prompt_input == "":
        continue

    if prompt_input.lower() in "exit":
        sys.exit(1)

    # change directory
    if "cd" in prompt_input:
        args = prompt_input.split(" ")
        try:
            process_flag = True;
            os.chdir(os.getcwd() + "/" + args[1])
        except FileNotFoundError:
            print("Does not exist.")
        continue

    rc = os.fork()
    if rc < 0:
        os.write(2,
                ("fork failed, returning %d\n" % rc).encode())
        sys.exit(1)
    elif rc == 0:
        if "|" in prompt_input:
            print("Pipe found.")
            pipe = prompt_input.split("|")
            cmd_1 = pipe[0].split()
            cmd_2 = pipe[1].split()

            pr, pw = os.pipe() # file descriptors for reading and writing.
            for file_descriptor in (pr, pw):
                os.set_inheritable(file_descriptor, True)

            pipe_rc = os.fork()
            if pipe_rc < 0:
                os.write(2, ("fork faile").encode())
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
