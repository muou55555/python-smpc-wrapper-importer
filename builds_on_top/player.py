from time import sleep
from flask import Flask, jsonify
from flask_cors.extension import CORS
from flask_restful import Resource, Api
from multiprocessing import Process
from player_auxilliary import generate_and_compile, run_smpc_computation
import json
import argparse

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument(
    'player_id',
    metavar='id',
    type=int,
    nargs=1,
    help='Specify player Id'
)

args = parser.parse_args()
player_id = args.player_id[0]
app = Flask(__name__)
api = Api(app)

CORS(app, resources={r"/api/*": {"origins": "*"}})
class TriggerComputation(Resource):
    def get(self, jobId, clients, datasetSize):
        try:
            generate_and_compile(str(clients), datasetSize)
            p = Process(target=run_smpc_computation, args=(player_id, str(clients), jobId,))
            p.start()
            sleep(0.05)
            if p.exitcode == 0:
                raise ValueError
            return 200
        except Exception as e:
            print(e)
            return 500

class Ping(Resource):
    def get(self):
        return 200

api.add_resource(Ping, '/api/ping')
api.add_resource(TriggerComputation, '/api/job-id/<jobId>/clients/<clients>/dataset-size/<datasetSize>')
    
if __name__ == '__main__':
    app.run(debug=True, port=7100+player_id, host="0.0.0.0")