from time import sleep
from flask import Flask, jsonify, request
from flask_restful import Resource, Api
from multiprocessing import Process
import subprocess
import argparse

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument(
    'client_id',
    metavar='id',
    type=int,
    nargs=1,
    help='Specify player Id'
)

args = parser.parse_args()
client_id = args.client_id[0]

app = Flask(__name__)
api = Api(app)

dataset = "dataset/dataset.txt"

class TriggerImportation(Resource):
    def get (self):
        cmd_run_clients = "./Client-Api.x {0} {1}".format(client_id, dataset)
        cmdpipe = subprocess.Popen(cmd_run_clients, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        print("the commandline is {}".format(cmd_run_clients))

class GetDatasetSize(Resource):
    def get(self):
        try:
            with open(dataset, 'r') as f:
                lines = f.readlines()
            return len(lines)
        except Exception as e:
            print(e)
            return 500

class ChangeData(Resource):
    def get(self):
        with open(dataset, 'r') as f:
            ret = [i.split("\n")[0] for i in f.readlines()]
            return jsonify(ret)

    def post(self):
        json_data = request.get_json(force=True)
        result = {}
        with open(dataset, 'w') as f:
            f.writelines([str(j) + '\n' for j in json_data['data']])
        return 200

class Ping(Resource):
    def get(self):
        return 200

api.add_resource(Ping, '/api/ping')
api.add_resource(GetDatasetSize, '/api/get-dataset-size')
api.add_resource(TriggerImportation, '/api/trigger-importation')
api.add_resource(ChangeData, '/api/update-dataset')

if __name__ == '__main__':
    app.run(debug=True, port=9000+client_id, host="0.0.0.0")