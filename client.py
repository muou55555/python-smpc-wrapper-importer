from time import sleep
from flask import Flask, jsonify, request
from flask_cors.extension import CORS
from flask_restful import Resource, Api
from multiprocessing import Process
import subprocess
import json
import argparse
import numpy as np
import os

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
CORS(app, resources={r"/api/*": {"origins": "*"}})

dataset = "dataset/dataset.txt"
json_dataset = "dataset/full_dataset_{0}.json".format(client_id)
def job_dataset(x): return "dataset/dataset_{1}_{0}.txt".format(x, client_id)


class TriggerImportation(Resource):
    def get(self, jobId):
        print("importation triggered")
        cmd_run_clients = "./Client-Api.x {0} {1}".format(
            client_id, job_dataset(jobId))
        cmdpipe = subprocess.Popen(
            cmd_run_clients, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        print("the commandline is {}".format(cmd_run_clients))
        while True:
            out = cmdpipe.stdout.readline().decode()
            if out == "":
                break
            # print(out)


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


class ComputeCategoricalHistogram(Resource):
    def get(self, attribute, noValues, jobId):
        print("Computing histogram !!!")
        values = [int(i) for i in noValues.split(".")]
        histo = np.zeros(len(values))
        with open(json_dataset, 'r') as f:
            data = json.load(f)
            x = np.array([i["data"][attribute] for i in data])
            unique, counts = np.unique(x, return_counts=True)
            for idx, v in enumerate(values):
                if v in unique:
                    histo[idx] = int(counts[np.where(unique == v)])
            with open(job_dataset(jobId), 'w') as f:
                f.writelines([str(int(j)) + '\n' for j in list(histo)])
        return 200


class ComputeNumericalHistogram(Resource):
    def get(self, attribute, bins, start, end, jobId):
        histo = np.zeros(int(bins))
        with open(json_dataset, 'r') as f:
            data = json.load(f)
            x = np.array([i["data"][attribute] for i in data])
            x = x[x >= float(start)]
            x = x[x <= float(end)]
            D = (float(end) - float(start)) / int(bins)
            for i in range(1, int(bins) + 1):
                bucket = x[x <= D * i + float(start)]
                bucket = bucket[bucket >= D * (i - 1) + float(start)]
                histo[i-1] = bucket.shape[0]
            with open(job_dataset(jobId), 'w') as f:
                f.writelines([str(int(j)) + '\n' for j in list(histo)])
        return 200

class GetRawDataset(Resource):
    def get(self):
        with open(os.path.join("dataset", "full_dataset_{0}.json".format(client_id)), 'r') as f:
            data = json.load(f)
        return data
class Ping(Resource):
    def get(self):
        return 200


api.add_resource(Ping, '/api/ping')
api.add_resource(ComputeNumericalHistogram,
                 '/api/compute-numerical-histogram/attribute/<attribute>/bins/<bins>/start/<start>/end/<end>/jobId/<jobId>')
api.add_resource(ComputeCategoricalHistogram,
                 '/api/compute-histogram/attribute/<attribute>/values/<noValues>/jobId/<jobId>')
api.add_resource(GetDatasetSize, '/api/get-dataset-size')
api.add_resource(TriggerImportation, '/api/trigger-importation/job-id/<jobId>')
api.add_resource(GetRawDataset, '/api/get-raw-dataset')
api.add_resource(ChangeData, '/api/update-dataset')

if __name__ == '__main__':
    app.run(debug=True, port=9000+client_id, host="0.0.0.0")
