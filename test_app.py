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

def test_get(client):
    post_test = client.post("/items", json={"name": "widget"})
    post_test_id = post_test.get_json()["id"]

    #test with valid name should return 200
    get_test = client.get("/items", query_string={"id": post_test_id})
    assert get_test.status_code == 200
    assert get_test.get_json()["name"] == "widget"

    #test GET with non existant name should return 404
    get_test = client.get("/items", query_string={"name": "qwerty"})
    assert get_test.status_code == 404
    
    #test invalid params, should return 400
    get_test = client.get("/items", query_string={"nname": "widget"})
    assert get_test.status_code == 400
    
    #test no params, should return all items 200
    get_test = get_test = client.get("/items")
    assert get_test.status_code == 200
    items = get_test.get_json()

    assert len(items) == 1
    assert items[0]["name"] == "widget"


def test_put(client):
    #post test widget to client
    post_test = client.post("/items", json={"name": "widget"})
    post_test_id = post_test.get_json()["id"]

    #update item return 200
    put_test = client.put(f"/items/{post_test_id}", json={"name": "gadget"})
    assert put_test.status_code == 200

    #get correct item
    db_response = table.get_item(Key={"id": post_test_id})
    assert db_response["Item"]["name"] == "gadget"

    #test return correct item
    s3_response = s3.get_object(Bucket="items-bucket", Key=f"{post_test_id}.json")
    s3_item = json.loads(s3_response["Body"].read())
    assert s3_item == db_response["Item"]

def test_put_not_found(client):
    put_test = client.put("/items/nonexistent-id", json={"name": "gadget"})
    assert put_test.status_code == 404

def test_delete(client):
    post_test = client.post("/items", json={"name": "widget"})
    post_test_id = post_test.get_json()["id"]

    delete_test = client.delete(f"/items/{post_test_id}")
    assert delete_test.status_code == 204

    # confirm removed from both stores
    db_response = table.get_item(Key={"id": post_test_id})
    assert "Item" not in db_response

def test_delete_not_found(client):
    delete_test = client.delete("/items/nonexistent-id")
    assert delete_test.status_code == 404

