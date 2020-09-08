import os, sys, time, re

while (1):
    if os.environ.get('PS1') != None:
        prompt_input = input(os.environ['PS1']) # Add input.
    else:
        prompt_input = input("$ ")
    args = prompt_input.split(" ")

    print(args[0])
    if args[0] == "exit":
        sys.exit(1)

    rc = os.fork()

    if rc < 0:
        os.write(2,
            ("fork failed, returning %d\n" % rc).encode())
        sys.exit(1)
    elif rc == 0:
        sys.exit(1)
    else:
        os.wait()
