import tempfile

from fake_data.metadata.metadata_cache import MetadataCache
import os
import pytest


@pytest.fixture(scope="session")
def tmp_cache_dir():
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


class TestMetadataCache:
    def test_init_default(self):
        # not the best test as the file could be created outside of the test case
        expected_cache_dir = "./.fake_data_cache"
        _ = MetadataCache()

        # Check if the file "fake_data.db" exists the default metadata cache directory
        assert os.path.isfile(f"{expected_cache_dir}/fake_data.db")

    def test_init_with_cache_dir(self, tmp_cache_dir):
        # Perform testing with the temporary cache directory
        _ = MetadataCache(metadata_cache_dir=tmp_cache_dir)

        # Check if the file "fake_data.db" exists in the cache_dir directory
        assert os.path.isfile(os.path.join(tmp_cache_dir, "fake_data.db"))

    def test_create_table_sttmt(self):
        mdc = MetadataCache()
        table_name = "test_table"
        columns = [
            {"name": "id", "type": "int"},
            {"name": "name", "type": "string"},
        ]
        expected = "CREATE TABLE test_table (id int, name string)"
        assert mdc._create_table_sttmt(table_name, columns) == expected

    def test_create_table(self):
        pass
