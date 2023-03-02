# Search POC
This repo contains an implementation of hybrid search approach inspired by this https://github.com/Searchium-ai/hybrid-search but using the latest version 
of Elasticsearch

To use it, make sure to have Docker installed to spin up Elasticsearch and Kibana as containers. 
### Setting up Elasticsearch
Under the `Dockerfiles` directory, run 
`docker-compose up -d `

This will spin up Elasticsearch and Kibana. Once they are up, try it in a browser
`http://localhost:5601/app/dev_tools#/console`

### Indexing data
To prepare the Python environment, create a virtual env
`python3 -m venv <your virtual env>`

Then install `poetry`

Once poetry is installed, run
`poetry init`

This will install all dependencies
Finally, run the indexer
`python indexer.py`

Verify that the index has been created in Kibana

### Perform Search
Run the app
`python app.py`

And you can search in your browser using
`http://127.0.0.1:5000/`