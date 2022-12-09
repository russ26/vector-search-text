from sentence_transformers import SentenceTransformer, util
from flask import Flask, render_template, request, jsonify
import os
import sys
import pymongo
import ssl
from bson import json_util
import json

sys.path.insert(1, '../config/')
from config_database import mongo_uri, db, collection

app = Flask(__name__,
            static_url_path='',
            static_folder='../encoder',)

connection = pymongo.MongoClient(mongo_uri)
product_collection = connection[db][collection]
preTrainedModelName = "paraphrase-MiniLM-L3-v2"
model = SentenceTransformer(preTrainedModelName)


@app.route('/searchResponses', methods=['GET'])
def searchResponses():

    vector_text = request.args.get('vector', default=None, type=str)
    vector_query = model.encode(vector_text).tolist()
    pipeline = [
        {
            '$search': {
                'index': 'vectorSearchResponse',
                'knnBeta': {
                    'vector': vector_query,
                    'path': 'vector',
                    'k': 10
                }
            }
        }, {
            '$set': {
                'highlight': True
            }
        }, {
            '$project': {
                'vector': 0
            }
        }
    ]

    # Execute the pipeline
    docs = list(product_collection.aggregate(pipeline))
    # Return the results unders the docs array field
    json_result = json_util.dumps(
        {'docs': docs}, json_options=json_util.RELAXED_JSON_OPTIONS)
    return jsonify(json_result)


@app.route('/searchTranscript', methods=['GET'])
def search():

    vector_text = request.args.get('vector', default=None, type=str)
    vector_query = model.encode(vector_text).tolist()
    call_id = request.args.get('call_id', default=None, type=str)
    pipeline = [
        {
            '$search': {
                'index': 'vectorSearchResponse',
                'knnBeta': {
                    'vector': vector_query,
                    'path': 'vector',
                    'k': 10
                }
            }
        }, {
            '$match': {
                'call_id': call_id
            }
        }, {
            '$set': {
                'highlight': True
            }
        }, {
            '$project': {
                'vector': 0
            }
        }, {
            '$group': {
                '_id': None,
                'call_id': {
                    '$addToSet': '$call_id'
                },
                'data': {
                    '$push': '$$ROOT'
                }
            }
        }, {
            '$lookup': {
                'from': 'responses',
                'localField': 'call_id',
                'foreignField': 'call_id',
                'as': 'result'
            }
        }, {
            '$project': {
                'responses': {
                    '$map': {
                        'input': '$result',
                        'as': 'one',
                        'in': {
                            '$mergeObjects': [
                                '$$one', {
                                    '$arrayElemAt': [
                                        {
                                            '$filter': {
                                                'input': '$data',
                                                'as': 'two',
                                                'cond': {
                                                    '$eq': [
                                                        '$$two._id', '$$one._id'
                                                    ]
                                                }
                                            }
                                        }, 0
                                    ]
                                }
                            ]
                        }
                    }
                }
            }
        }, {
            '$unwind': {
                'path': '$responses'
            }
        }, {
            '$group': {
                '_id': '$responses.call_id',
                'responses': {
                    '$push': '$$ROOT.responses'
                }
            }
        }
    ]

    # Execute the pipeline
    docs = list(product_collection.aggregate(pipeline))
    # Return the results unders the docs array field
    json_result = json_util.dumps(
        {'docs': docs}, json_options=json_util.RELAXED_JSON_OPTIONS)
    return jsonify(json_result)


# page
@app.route('/')
def index():
    return render_template("index.html")


if __name__ == '__main__':
    app.run(host="localhost", port=5050, debug=True)
