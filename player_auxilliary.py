import subprocess
import requests
import os, sys
import json
MPC_PROGRAM = "Programs/aa/aa.mpc"

WAIT = '@'
OUTPUT_START = '# OUTPUT START:'
OUTPUT_END = "$ OUTPUT END"

cmd_compile_player = ['python', 'compile.py', 'Programs/aa']

# coordinator = "http://0.0.0.0:12314/api/result"
coordinator = "http://dl056.madgik.di.uoa.gr:12314/api/result"

# ClientsRepo = {
#     "0": "http://0.0.0.0:9000",
#     "1": "http://0.0.0.0:9001",
#     "2": "http://0.0.0.0:9002"
# }

ClientsRepo = {
    "2": "http://dl058.madgik.di.uoa.gr:9002",
    "1": "http://dl057.madgik.di.uoa.gr:9001",
    "0": "http://dl056.madgik.di.uoa.gr:9000"
}


def handle_output(player_id, line_output, client_list):
    if player_id != 0:
        return
    if line_output == WAIT:
        for client in client_list:
            requests.get(ClientsRepo[str(client)] + "/api/trigger-importation")

def generate_code(replacement_line_1, replacement_line_2):
    f = open(MPC_PROGRAM)
    _, _, remainder = f.readline(), f.readline(), f.read()
    t = open(MPC_PROGRAM,"w")
    t.write(replacement_line_1 + "\n")
    t.write(replacement_line_2 + "\n")
    t.write(remainder)
    t.close()

def generate_and_compile(clients, dataset_size):
    no_clients = clients.split(".")
    MPC_Fi_LINE = lambda x: 'no_clients = {0}'.format(len(no_clients))
    MPC_Se_LINE = lambda x: 'bins = {0}'.format(dataset_size)
    print("the commandline is {}".format(cmd_compile_player))
    generate_code(MPC_Fi_LINE(no_clients), MPC_Se_LINE(dataset_size))
    try:
        out = subprocess.check_output(cmd_compile_player)
    except subprocess.CalledProcessError as e:
        print("There was an error")

def run_smpc_computation(player_id, clients, jobId):
    client_list = clients.split(".")
    cmd_run_player = "./Player.x {0} Programs/aa -clients {1}".format(player_id, len(client_list))
    cmdpipe = subprocess.Popen(cmd_run_player, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    computation_result = None
    print("the commandline is {}".format(cmd_run_player))
    switch = False
    while True:
        out = cmdpipe.stdout.readline()
        print(out)
        # print(cmdpipe.stderr.readline())
        if out == '' and cmdpipe.poll() != None:
            break
        if out != '':
            line_output = out.split("\n")[0]
            handle_output(player_id, line_output, client_list)
            if (line_output == OUTPUT_END):
                switch = False
            if (switch):
                computation_result += [str(out.split("\n")[0])]
            if (line_output == OUTPUT_START and computation_result is None):
                computation_result = []
                switch = True
            sys.stdout.write(out)
            sys.stdout.flush()
            
    print("The computation result is {0}".format(computation_result))
    if computation_result is None:
        exit(0)
    else:
        requests.post(
            coordinator,
            json={
                "jobId": jobId,
                "computation_output": computation_result
            }
        )