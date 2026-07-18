import pytest
import json
from app import app
from app import table
from app import s3
from boto3.dynamodb.conditions import Attr
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
    
    db_response = table.get_item(Key={"id": post_test_id})
    assert db_response["Item"]["name"] == "widget"
    assert post_test.status_code == 201
    
    s3_response = s3.get_object(Bucket="items-bucket", Key=f"{post_test_id}.json")
    s3_item = json.loads(s3_response["Body"].read())

    assert s3_item == db_response["Item"]

def test_duplicate_post(client):
    post_test = client.post("/items", json={"name": "widget"})
    post_test_id = post_test.get_json()["id"]

    #test first post succeeded
    assert post_test.status_code == 201
       
    #now duplicate post and check status code
    duplicate_test_id = client.post("/items", json={"name": "widget"})
    assert duplicate_test_id.status_code == 409

    #finally scan for duplicate in table to confirm that
    #only one widget got made
    scan_response = table.scan(FilterExpression=Attr("name").eq("widget"))
    assert len(scan_response["Items"]) == 1 
    