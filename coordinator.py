import os
import sys
import subprocess
from time import sleep
from flask import Flask, jsonify, request
from flask_restful import Resource, Api, abort
from multiprocessing import Process, Value, Manager
import requests
import json
from ctypes import c_char_p
from threading import Thread
from flask_cors import CORS

app = Flask(__name__)
api = Api(app)
CORS(app, resources={r"/api/*": {"origins": "*"}})
manager = Manager()
return_url = Value(c_char_p, b"")

PlayersRepo = {
    "2": "http://localhost:7102",
    "1": "http://localhost:7101",
    "0": "http://localhost:7100"
}

ClientsRepo = {
    "2": "http://localhost:9002",
    "1": "http://localhost:9001",
    "0": "http://localhost:9000"
}

# PlayersRepo = {
#     "2": "http://dl058.madgik.di.uoa.gr:7102",
#     "1": "http://dl057.madgik.di.uoa.gr:7101",
#     "0": "http://dl056.madgik.di.uoa.gr:7100"
# }

# ClientsRepo = {
#     "2": "http://dl058.madgik.di.uoa.gr:9002",
#     "1": "http://dl057.madgik.di.uoa.gr:9001",
#     "0": "http://dl056.madgik.di.uoa.gr:9000"
# }


def trigger_computation(job_id, clients):
    client_list = clients.split(".")
    for i in client_list:
        r = requests.get(ClientsRepo[i] + "/api/get-dataset-size")
    dataset_size = str(r.json())
    for k in ['2', '1', '0']:
        r = requests.get(PlayersRepo[k] + "/api/job-id/{0}/clients/{1}/dataset-size/{2}".format(
            str(job_id), str(clients), dataset_size))
        if r.json() != 200:
            print(r.json())
            print(PlayersRepo[k] + "/api/job-id/{0}/clients/{1}/dataset-size/{2}".format(
                str(job_id), str(clients), dataset_size))
            abort(500)


class PreComputePoll(Resource):
    def get(self, job_id, clients):
        trigger_computation(job_id, clients)
        return 200


def trigger_categorical_histo_on_clients(k, attribute, noValues, jobId):
    r = requests.get(ClientsRepo[k] + "/api/compute-histogram/attribute/{0}/values/{1}/jobId/{2}".format(
        str(attribute), str(noValues), jobId))
    if r.json() != 200:
        abort(500)


class CategoricalHistogramTrigger(Resource):
    def get(self, attribute, noValues, jobId, clients):
        clients_list = clients.split(".")
        threads = []
        for k in clients_list:
            thread = Thread(target=trigger_categorical_histo_on_clients, args=(
                k, attribute, noValues, jobId))
            threads.append(thread)
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        trigger_computation(jobId, clients)
        return 200

class NumericalHistogramTrigger(Resource):
    def get(self, attribute, noValues, jobId, clients):
        clients_list = clients.split(".")
        threads = []
        for k in clients_list:
            thread = Thread(target=trigger_categorical_histo_on_clients, args=(
                k, attribute, noValues, jobId))
            threads.append(thread)
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        trigger_computation(jobId, clients)
        return 200

class SetReturnUrl(Resource):
    def get(self):
        return return_url.value.decode()

    def post(self):
        json_data = request.get_json(force=True)
        return_url.value = str.encode(json_data['url'])
        return 200


class Return(Resource):
    def post(self):
        json_data = request.get_json(force=True)
        result = {}
        for k in json_data:
            if str(k) == "jobId":
                result[str(k)] = str(json_data[k])
            else:
                result[str(k)] = [str(i) for i in json_data[k]]
        print(result)
        print(return_url.value)
        if (return_url.value != ""):
            requests.post(
                return_url.value,
                json={
                    result
                }
            )
        return 200

class Ping(Resource):
    def get(self):
        return 200

api.add_resource(
    PreComputePoll, '/api/secure-aggregation/job-id/<job_id>/clients/<clients>')
api.add_resource(
    CategoricalHistogramTrigger, '/api/compute-histogram/attribute/<attribute>/values/<noValues>/jobId/<jobId>/clients/<clients>')
api.add_resource(SetReturnUrl, '/api/set-return-url')
api.add_resource(Ping, '/api/ping')

if __name__ == '__main__':
    app.run(debug=True, port=12314, host="0.0.0.0")
