# generate-fake-data
Generate fake data sets using the `faker` library.

# Background

I work on a data project, utilising dbt and bigquery, with pipelines in gitlab. We ingest finance data from core systems, transform that with dbt (data vault methodology) and serve it in a curate layer in bigquery. We need to test our data vault models with appropriate data, since we don't have access to Prod data.

# Requirements

1. Use a csv driven process, where the csv defines the ingestion file metadata with attribute names and data types
   
2. generate fake data that can simulate real-world scenarios; i.e. if an attribute is `name` with type `string`, try and generate a realistic name
   
3. allow the ability for different options and scenarios. pass in those runtime parameters using something like the `typer` library
   
4. output a csv file, that conforms to the ingestion metadata, that can be stored in GCS

## Installation
Install using poetry.  This makes the `generate-fake-data` cli utility
```
poetry install
poetry shell
```

```
generate-fake-data
```

