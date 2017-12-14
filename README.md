
# Github Relay

A Flask app to relay requests to the Github API for situations where storing your access token 
would be a bad idea (i.e. a web app that needs to use a Github App token).

## Installation

Clone the repository to your webserver and install the dependencies (ideally using virtualenv).

    git clone https://github.com/rhyst/github-relay/
    cd github-relay
    virtualenv -p python3 venv
    source venv/bin/activate
    pip install -r requirements.txt

To run the app I recommend using uwsgi. In the `extras/` folder are two example files, one to 
set it up via a systemd service (`github_relay.service`) and the other to set it up as a 
[wsgi emperor vassal](http://uwsgi-docs.readthedocs.io/en/latest/Emperor.html) (`github_relay.ini`).

Both of these methods should provide a socket file to connect to. Here is an example nginx config:

    location = /github-relay {
        rewrite ^ /github-relay/;
    }
    location /github-relay/ {
        try_files $uri @github-relay;
    }
    location @github-relay {
        include uwsgi_params;
        uwsgi_pass unix:/path/to/process.sock;
    }
    
## Config

The config.json file should be customised. It contains the following:

    INSTALLATION_ID = "123456"                        // Installation ID of your Github App on a repo
    REPO_ID = "12345678"                              // ID of Rrepo that App is installed on
    PEM_FILE_LOCATION = "mypem.private-key.pem"       // Location of secret key PEM from App
    URL_PREFIX = 'repos/orgname/reponame/contents/'   // This determines what endpoint you access
    ROUTE_URL = '/github-relay/'                      // This should match the url you give the app in nginx/apache/etc.

## Usage

It should be easy to modify to your usage but by default it accepts post requests with a json of the form:

    {
        token: "sometoke"
        url: "some/path/to/a/file.md"
    }

Where token is the user access token and url is a file path within the repo (will depend on how you set `URL_PREFIX`).

The response will be whatever the Github API sends back.
