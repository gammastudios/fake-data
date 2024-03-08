from fake_data.metadata.metadata_cache import MetadataCache
import os
import pytest


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
            {"attribute_name": "id", "data_type": "int"},
            {"attribute_name": "name", "data_type": "string"},
        ]
        expected = "CREATE TABLE IF NOT EXISTS test_table (id int, name string)"
        assert mdc._create_table_sttmt(table_name, columns) == expected

    @pytest.mark.parametrize(
        "table_name,columns",
        [
            (
                "test_table",
                [
                    {"attribute_name": "id", "data_type": "int"},
                    {"attribute_name": "name", "data_type": "string"},
                ],
            ),
            (
                "test_varchar_table",
                [
                    {"attribute_name": "id", "data_type": "int"},
                    {"attribute_name": "attr_a", "data_type": "varchar"},
                ],
            ),
        ],
    )
    def test_create_table(self, tmp_cache_dir, table_name, columns):
        # using the tmp cache dir ensures a clean db on each test case
        mdc = MetadataCache(metadata_cache_dir=tmp_cache_dir)

        mdc.create_table(table_name, columns)

        assert table_name in mdc.fake_tables

        result = mdc.db.execute(f"SELECT * FROM {table_name}")
        act_column_names = [column[0] for column in result.description]
        expected_column_names = [column["attribute_name"] for column in columns]
        assert act_column_names == expected_column_names

    def test_get_fake_tables(self, test_metadata_cache):
        mdc = test_metadata_cache
        assert mdc.fake_tables == mdc.get_fake_tables()

        table_name = "test_table"
        columns = [
            {"attribute_name": "id", "data_type": "int"},
            {"attribute_name": "name", "data_type": "string"},
        ]
        mdc.create_table(table_name, columns)
        assert mdc.fake_tables == mdc.get_fake_tables()
        assert "test_table" in mdc.fake_tables
