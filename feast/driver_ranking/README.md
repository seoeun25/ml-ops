# Feast Quickstart
A quick view of what's in this repository:

* `data/` contains raw demo parquet data
* `example_repo.py` contains demo feature definitions
* `feature_store.yaml` contains a demo setup configuring where data sources are
* `test_workflow.py` showcases how to run all key Feast commands, including defining, retrieving, and pushing features. 

You can run the overall workflow with `python test_workflow.py`.

## To move from this into a more production ready workflow:
1. `feature_store.yaml` points to a local file as a registry. You'll want to setup a remote file (e.g. in S3/GCS) or a 
SQL registry. See [registry docs](https://docs.feast.dev/getting-started/concepts/registry) for more details.
2. Setup CI/CD + dev vs staging vs prod environments to automatically update the registry as you change Feast feature definitions. See [docs](https://docs.feast.dev/how-to-guides/running-feast-in-production#1.-automatically-deploying-changes-to-your-feature-definitions).
3. (optional) Regularly scheduled materialization to power low latency feature retrieval (e.g. via Airflow). See [Batch data ingestion](https://docs.feast.dev/getting-started/concepts/data-ingestion#batch-data-ingestion)
for more details.
4. (optional) Deploy feature server instances with `feast serve` to expose endpoints to retrieve online features.
   - See [Python feature server](https://docs.feast.dev/reference/feature-servers/python-feature-server) for details.
   - Use cases can also directly call the Feast client to fetch features as per [Feature retrieval](https://docs.feast.dev/getting-started/concepts/feature-retrieval)

## How to test

1. Register feature definitions and deploy feature store 
```
$ cd driver_ranking/feature_repo
$ feast apply
```
2. Build a point-in-time correct training dataset and train a model using Redshift
```
$ cd driver_ranking
$ python train.py
$ ls -l driver_model.bin
```

3. Load and serve features in production using DynamoDB
Get the latest feature values from offline store and load into online store 
```
$ cd driver_ranking/feature_repo
$ feast materialize 2021-01-01T00:00:00 2021-08-01T00:00:00 
```
Prediction
```
$ cd driver_ranking
$ python predict.py
```
