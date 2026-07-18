import boto3
import uuid #used for giving each item a unique id
import json
from flask import Flask, jsonify, request
from boto3.dynamodb.conditions import Attr
items = {}
next_id = 1
app = Flask (__name__)

dynamodb = boto3.resource(
    "dynamodb",
    endpoint_url="http://localhost:4566/",
    aws_access_key_id="test",
    aws_secret_access_key="test",
    region_name="us-east-1"
)
table = dynamodb.Table("items")
s3 = boto3.client(
    "s3",
    endpoint_url="http://localhost:4566/",
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


@app.route("/items/<int:item_id>", methods=["PUT"])
def update_item(item_id):
    if item_id not in items:
        return "", 404
    data = request.get_json()
    items[item_id] = data
    return jsonify(items[item_id]), 200

@app.route("/items/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    if item_id not in items:
        return "", 404
    del items[item_id]
    return "", 204


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)