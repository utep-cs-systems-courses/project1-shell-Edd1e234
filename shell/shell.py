import os, sys, time, re

def parse_single_cmd(cmd):
        """
        Assumes command has already been split by '|'.
        """
        if cmd.lower() == "exit":
            sys.exit(1)

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
        return re.split(" +", cmd), from_file_name, has_to_file

while (1):
    if os.environ.get('$PS1') != None:
        prompt_input = input(os.environ['$PS1']) # Add input.
    else:
        prompt_input = input("$ ")
    args = prompt_input.split(" ")

    if args[0] == "":
        continue

    args, from_file_name, has_to_file = parse_single_cmd(prompt_input)

    # change directory
    if "cd" in args:
        process_flag = True;
        os.chdir(os.getcwd() + "/" + args[1])
        continue

    # Need to sperate pipes here.

    rc = os.fork()
    if rc < 0:
        os.write(2,
                ("fork failed, returning %d\n" % rc).encode())
        sys.exit(1)
    elif rc == 0:
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
    else:
        os.wait()
