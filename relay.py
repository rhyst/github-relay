import sys
import json
import os
import logging
import datetime
import requests
import time
from flask import Flask, request
from flask_cors import CORS
import jwt
import json

# Load the config file
config = None
with open('../config.json') as json_data_file:
    config = json.load(json_data_file)

if config is None:
    print('No config file')
    exit()
else: 
    print("Configuration:")
    print(json.dumps(config, indent=4, sort_keys=True))

app = Flask(__name__)
CORS(app)

INSTALLATION_ID = config['INSTALLATION_ID']
REPO_ID = config['REPO_ID']
PEM_FILE_LOCATION = config['PEM_FILE_LOCATION']
URL_PREFIX = config['URL_PREFIX']
ROUTE_URL = config['ROUTE_URL']

@app.route(ROUTE_URL,methods=['POST'])
def relay():
    # Parse the post data
    str_response = request.data.decode('utf-8')
    data = json.loads(str_response)

    # Takes two posted strings
    # The user token and the requested url
    if 'token' in data:
        token = data['token']
        if 'url' in data:
            url = data['url']
        else:
            return "No url", 404
        response = requests.get('https://api.github.com/user/installations/' + INSTALLATION_ID + '/repositories', headers={'Authorization': 'token ' + token, 'Content-Type': 'application/json', 'Accept': 'application/vnd.github.machine-man-preview+json'})
        try:
            # Check that they have the correct permissions on the repo
            for repo in response.json()["repositories"]:
                if repo['id'] == REPO_ID and repo['permissions']['push']:
                    # If they do create an installation token
                    pem_file = open(PEM_FILE_LOCATION, "r")
                    encoded_jwt = jwt.encode({'iat': int(round(time.time())), 'exp': int(round(time.time()) + 60), 'iss': '6509'}, pem_file.read(), algorithm='RS256')
                    response = requests.post('https://api.github.com/installations/' + INSTALLATION_ID + '/access_tokens', headers={'Authorization': 'Bearer ' + str(encoded_jwt.decode("utf-8")), 'Content-Type': 'application/json', 'Accept': 'application/vnd.github.machine-man-preview+json'})
                    apptoken = response.json()['token']
                    # Make their request with the installation token and return the reponse
                    response = requests.get('https://api.github.com/' + URL_PREFIX + url, headers={'Authorization': 'token ' + apptoken, 'Content-Type': 'application/json', 'Accept': 'application/vnd.github.machine-man-preview+json'})
                    return response.text, response.status_code
        except Exception as error:
            print(error)
            return "Bad token", 401

    return "No token", 401

if __name__ == "__main__":
    app.run(host='0.0.0.0')