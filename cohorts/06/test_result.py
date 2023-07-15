import os
import pandas as pd

year = 2022
month = 1

S3_ENDPOINT_URL = os.getenv('S3_ENDPOINT_URL', 'http://localhost:4566')

def test_results ():
    input_file = 's3://nyc-duration/out/2022-01.parquet'
    options = {
    'client_kwargs': {
        'endpoint_url': S3_ENDPOINT_URL
        }
    }
    df = pd.read_parquet(input_file, storage_options=options)
    actual_result = df['predicted_duration'].sum()

    expected_result = 31.507450372727607

    assert actual_result == expected_result