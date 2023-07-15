#!/usr/bin/env python
# coding: utf-8

import os
import sys
import pickle
import pandas as pd

def get_input_path(year, month):
    
    default_input_pattern = "s3://nyc-duration/in/{year:04d}-{month:02d}.parquet"
    input_pattern = os.getenv('INPUT_FILE_PATTERN', default_input_pattern)
    input_pattern = input_pattern.format(year=year, month=month)
    return input_pattern


def get_output_path(year, month):
    
    default_output_pattern = "s3://nyc-duration/out/{year:04d}-{month:02d}.parquet"
    output_pattern = os.getenv('OUTPUT_FILE_PATTERN', default_output_pattern)
    return output_pattern.format(year=year, month=month)

def read_data(S3_ENDPOINT_URL, year, month):
    input_file = get_input_path(year, month)
    options = {
    'client_kwargs': {
        'endpoint_url': S3_ENDPOINT_URL
        }
    }
    df = pd.read_parquet(input_file, storage_options=options)
    return df

def prepare_data(df, categorical):
    df['duration'] = df.tpep_dropoff_datetime - df.tpep_pickup_datetime
    df['duration'] = df.duration.dt.total_seconds() / 60

    df = df[(df.duration >= 1) & (df.duration <= 60)].copy()

    df[categorical] = df[categorical].fillna(-1).astype('int64').astype('str')
    
    return df

def save_data(S3_ENDPOINT_URL, df, year, month):
    options = {
        'client_kwargs': {
            'endpoint_url': S3_ENDPOINT_URL
            }
        }

    output_path = get_output_path(year, month)
    df.to_parquet(
        output_path,
        engine='pyarrow',
        compression=None,
        index=False,
        storage_options=options
        )
    print(f'Results saved to {output_path}')


def main():

    year = int(sys.argv[1])
    month = int(sys.argv[2])
    
    S3_ENDPOINT_URL = os.getenv('S3_ENDPOINT_URL', 'http://localhost:4566')
    
    with open('model.bin', 'rb') as f_in:
        dv, lr = pickle.load(f_in)


    categorical = ['PULocationID', 'DOLocationID']

    df = read_data(S3_ENDPOINT_URL, year, month)
    df['ride_id'] = f'{year:04d}/{month:02d}_' + df.index.astype('str')

    
    df = prepare_data(df, categorical)


    dicts = df[categorical].to_dict(orient='records')
    X_val = dv.transform(dicts)
    y_pred = lr.predict(X_val)

    print(f'predicted mean duration: {y_pred.mean():.2f}')
    print(f'sum of predicted duration: {y_pred.sum():.2f}')

    df_result = pd.DataFrame()
    df_result['ride_id'] = df['ride_id']
    df_result['predicted_duration'] = y_pred
  
    save_data(S3_ENDPOINT_URL, df_result, year, month)


if __name__ == '__main__':
    main()