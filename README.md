# MongoDB Atlas Vector Search on Text Responses

- Create MongoDB Atlas Cluster with the M10 tier in your preferred region
- Load sample data that has vector arrays
- Add search index to collection
- Execution was successful with the following dependencies
  - Python 3.9.2 along with pip
    - Following libraries will be required
      - Flask==2.1.0
      - Pillow==9.3.0
      - pymongo==4.1.1
      - sentence_transformers==2.2.2
    - `requirements.txt` includes all the dependencies and if you want to install dependencies in one shot:
      ```bash
      pip install -r requirements.txt
      ```



# Steps to Install and Test

## Configure database connection 

Modify the `config/config_database.py` file accordingly with the database connection string, database and collection information. 

## Create the Search Index

Create the following search index on the collection that you configured in the config file:

```json
{
  "mappings": {
    "fields": {
      "vector": [
        {
          "dimensions": 384,
          "similarity": "cosine",
          "type": "knnVector"
        }
      ]
    }
  }
}
```

## Run the Web Application to Search for Responses

Switch to `webapp/` folder and run `flask_server.py`.

```bash
$ python flask_server.py
```

This web application has 2 views: 

1. 10 related responses to field being searched
2. View of all responses in transcript, with related responses highlighted (viewed by clicking Call ID for one of the responses)




