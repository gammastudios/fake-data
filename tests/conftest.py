# common fixtures for testing fake data generation and metadata
import pytest
import tempfile

from fake_data.metadata.metadata_cache import MetadataCache


@pytest.fixture(scope="session")
def tmp_cache_dir():
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture(scope="session")
def test_metadata_cache(tmp_cache_dir):
    """
    A metadata cache with the following fake-data tables.
      - customer: id(int), name(str), age(int), account_id(int)
      - cstmr_account: id(int), name(str), balance(float)
    """

    mdc = MetadataCache(metadata_cache_dir=tmp_cache_dir)

    mdc.create_table(
        "customer",
        [
            {"attribute_name": "id", "data_type": "int"},
            {"attribute_name": "name", "data_type": "string"},
            {"attribute_name": "age", "data_type": "int"},
            {"attribute_name": "account_id", "data_type": "int"},
        ],
    )
    mdc.create_table(
        "customer_account",
        [
            {"attribute_name": "id", "data_type": "int"},
            {"attribute_name": "name", "data_type": "string"},
            {"attribute_name": "balance", "data_type": "float"},
        ],
    )

    yield mdc


# ---- Test metadata csv files ----
@pytest.fixture()
def customer_csv_file(tmpdir):
    """
    A csv file with an example "customer" entity definition.
    """

    csv_content = """
        attribute_name,data_type,key_type,reference_file,reference_attribute, relationship
        name,string,,,,
        age,int,,,,
        hire_date,date,,,,
        id,string,PK,,,
        customer_account_id,int,FK,customer_account.csv,id,1:1
    """

    # strippiing out the leading spaces from the rows above
    csv_content = "\n".join(line.lstrip() for line in csv_content.split("\n"))
    csv_file = tmpdir.join("test_customer.csv")
    with open(csv_file, "w", newline="") as file:
        file.write(csv_content)
    return csv_file
