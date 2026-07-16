import pytest
from app import app
from app import table
from app import s3
from app import boto3

@pytest.fixture(autouse=True)
def clean_resources():
    # clear dynamodb
    response = table.scan()
    for item in response["Items"]:
        table.delete_item(Key={"id": item["id"]})
    # clear s3
    response = s3.list_objects_v2(Bucket="items-bucket")
    for obj in response.get("Contents", []):
        s3.delete_object(Bucket="items-bucket", Key=obj["Key"])
    yield

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_post(client):
    post_test = client.post("/items", json={"name": "widget"})
    post_test_id = post_test.get_json()["id"]
    table.get_item(Key={"id": "widget"})
    f"{id}.json" s3.get_object(...)

