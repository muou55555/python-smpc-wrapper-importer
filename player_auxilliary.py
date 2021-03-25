import subprocess
import requests
import os, sys
import json
MPC_PROGRAM = "Programs/aa/aa.mpc"

WAIT = '@'
OUTPUT_START = '# OUTPUT START:'

cmd_compile_player = ['python', 'compile.py', 'Programs/aa']

coordinator = "http://0.0.0.0:12314/api/result"

ClientsRepo = {
    "1": "http://0.0.0.0:9000"
}

def handle_output(line_output):
    if line_output == WAIT:
        requests.get(ClientsRepo["1"] + "/api/trigger-importation")

def generate_code(replacement_line_1, replacement_line_2):
    f = open(MPC_PROGRAM)
    _, _, remainder = f.readline(), f.readline(), f.read()
    t = open(MPC_PROGRAM,"w")
    t.write(replacement_line_1 + "\n")
    t.write(replacement_line_2 + "\n")
    t.write(remainder)
    t.close()

def generate_and_compile(no_clients, dataset_size):
    MPC_Fi_LINE = lambda x: 'no_clients = {0}'.format(no_clients)
    MPC_Se_LINE = lambda x: 'bins = {0}'.format(dataset_size)
    print("the commandline is {}".format(cmd_compile_player))
    generate_code(MPC_Fi_LINE(no_clients), MPC_Se_LINE(dataset_size))
    try:
        out = subprocess.check_output(cmd_compile_player)
    except subprocess.CalledProcessError as e:
        print("There was an error")

def run_smpc_computation(player_id, no_clients, jobId):
    cmd_run_player = "./Player.x {0} Programs/aa -clients {1}".format(player_id, no_clients)
    cmdpipe = subprocess.Popen(cmd_run_player, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    computation_result = None
    print("the commandline is {}".format(cmd_run_player))
    
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