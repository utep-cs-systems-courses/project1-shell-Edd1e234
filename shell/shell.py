import os, sys, time, re

while (1):
    if os.environ.get('PS1') != None:
        prompt_input = input(os.environ['PS1']) # Add input.
    else:
        prompt_input = input("$ ")
    args = prompt_input.split(" ")

    if args[0] == "exit":
        sys.exit(1)

    rc = os.fork()

    if rc < 0:
        os.write(2,
            ("fork failed, returning %d\n" % rc).encode())
        sys.exit(1)
    elif rc == 0:
        process_flag = False
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
