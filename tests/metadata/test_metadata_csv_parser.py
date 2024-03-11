from fake_data.metadata.metadata_csv_parser import MetadataCsvParser


class TestMetadataCsvParser:
    def test_read_csv(self, customer_csv_file):
        mcp = MetadataCsvParser()
        table_md = mcp.read_csv(customer_csv_file)
        metadata_keys = [
            "attribute_name",
            "data_type",
            "key_type",
            "reference_entity",
            "reference_attribute",
            "relationship",
            "reference_entity",
            "relationship",
        ]
        for item in table_md:
            for key in metadata_keys:
                assert key in item.keys()
