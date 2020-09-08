import os, sys, time, re

while (1):
    if os.environ.get('PS1') != None:
        prompt_input = input(os.environ['PS1']) # Add input.
    else:
        prompt_input = input("$ ")
    rc = os.fork()
    if rc < 0:
        os.write(2, ("fork failed, returning %d\n" % rc).encode())
        sys.exit(1)
    elif rc == 0:
        args = prompt_input.split()

        # Quietly
        if len(args) is 0:
            sys.exit(1)

        for dir in re.split(":", os.environ['PATH']):
            program = "%s/%s" % (dir, args[0])
