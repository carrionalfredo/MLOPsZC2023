docker-compose up -d

timeout /t 2

aws --endpoint-url=http://localhost:4566 s3 mb s3://nyc-duration

pipenv run python integration_test.py

aws --endpoint-url=http://localhost:4566 s3 ls s3://nyc-duration --recursive

pipenv run python batch.py 2022 1

pipenv run pytest test_result.py

docker-compose down
