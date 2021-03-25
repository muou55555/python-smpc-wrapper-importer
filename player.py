import os, sys
import subprocess

WAIT = '@'
OUTPUT_START = '# OUTPUT START:'
player_id = '1'
no_clients = '1'
cmd = ['./Player.x', player_id, 'Programs/aa', '-clients', no_clients]
cmd = "./Player.x {0} Programs/aa -clients {1}".format(player_id, no_clients)

def handle_output(line_output):
    if line_output == WAIT:
        print('trigger wait')


def main():
    cmdpipe = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    computation_result = None
    print("the commandline is {}".format(cmd))
    
    while True:
        out = cmdpipe.stdout.readline()
        if out == '' and cmdpipe.poll() != None:
            break
        if out != '':
            line_output = out.split("\n")[0]
            handle_output(line_output)
            if (line_output == OUTPUT_START):
                computation_result = cmdpipe.stdout.readline().split("\n")[0]
            sys.stdout.write(out)
            sys.stdout.flush()
    print("The computation result is {0}".format(computation_result))

if __name__ == '__main__':
    main()