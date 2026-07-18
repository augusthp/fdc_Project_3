import boto3
import uuid #used for giving each item a unique id
import json
import os
from flask import Flask, jsonify, request
from boto3.dynamodb.conditions import Attr
items = {}
next_id = 1
app = Flask (__name__)
LOCALSTACK_ENDPOINT = os.environ.get("LOCALSTACK_ENDPOINT", "http://localhost:4566")

dynamodb = boto3.resource(
    "dynamodb",
    endpoint_url=LOCALSTACK_ENDPOINT,
    aws_access_key_id="test",
    aws_secret_access_key="test",
    region_name="us-east-1"
)
table = dynamodb.Table("items")
s3 = boto3.client(
    "s3",
    endpoint_url=LOCALSTACK_ENDPOINT,
    aws_access_key_id="test",
    aws_secret_access_key="test",
    region_name="us-east-1"
)





# GET, needs to return expected JSON from database 
@app.route("/items", methods=["GET"])
def get_items():
    get_id = request.args.get("id")
    get_name = request.args.get("name")
    #check to make sure no other items in request
    allowed_keys = {"id", "name"}
    request_keys = set(request.args.keys())
    if request_keys.issubset(allowed_keys) is not True:
        return jsonify("Error too many words"), 400
    
    if get_id is not None:
        response = table.get_item(Key={"id": get_id})
        if "Item" in response:
            return jsonify(response["Item"]), 200
        else:
            return jsonify({"error": "not found"}), 404
    elif get_name is not None:
        response = table.scan(FilterExpression=Attr("name").eq(get_name))
        if response["Items"]:
            return jsonify(response["Items"][0]), 200
        else:
            return jsonify({"error": "not found"}), 404
    else:
        response = table.scan()
        return jsonify(response["Items"]), 200
    

#Sending GET with no parameters needs to return appropriate response

#Seding a GET response that finds no parameters returns appropriate response

#Sedning GET resquest with incurect params returns appropriate response

@app.route("/items", methods=["POST"])
def post_items():
    data = request.get_json() #get the json body
    #and check for valid name
    if (data.get("name") is None):
        return jsonify({"error": "name is required"}), 400
    #check if name already exists in this dict
    response = table.scan(FilterExpression=Attr("name").eq(data.get("name")))
    if response["Items"]:
        return jsonify({"error": "name already exists"}), 409
    #verified it exist and is not duplicate so return
    ## call uuid to make new id for item
    new_id = str(uuid.uuid4())
    full_item = {"id": new_id, **data}

    #write to dynamodb
    table.put_item(Item=full_item)

    #write to s3
    s3.put_object(Bucket="items-bucket", Key=f"{new_id}.json", Body=json.dumps(full_item))

    return jsonify(full_item),201


@app.route("/items/<string:item_id>", methods=["PUT"])
def update_item(item_id):
    data = request.get_json() #get the json body
    item = table.get_item(Key={"id": item_id})
    if "Item" not in item:
        return jsonify({"error": "not found"}), 404
    response = table.scan(FilterExpression=Attr("name").eq(data.get("name")))
    #check for item conflict by seeing if an item has 2 ids
    conflict = any(match["id"] != item_id for match in response["Items"])
    if conflict:
        return jsonify({"error": "name already exists"}), 409
    #didnt fail any checks so build item return 200
    updated_item = {"id": item_id, **data}
    table.put_item(Item=updated_item)
    s3.put_object(Bucket="items-bucket", Key=f"{item_id}.json", Body=json.dumps(updated_item))
    return jsonify(updated_item), 200
     



@app.route("/items/<string:item_id>", methods=["DELETE"])
def delete_item(item_id):
    item = table.get_item(Key={"id": item_id})
    #check item exists if not return 404
    if "Item" not in item:
        return jsonify({"error": "not found"}), 404
    
    #item exists delete item
    table.delete_item(Key={"id": item_id})
    s3.delete_object(Bucket="items-bucket", Key=f"{item_id}.json")
    return "", 204


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)