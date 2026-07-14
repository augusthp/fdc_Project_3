import boto3

# Create a client pointed at Localstack instead of real AWS
dynamodb = boto3.client(
    "dynamodb",
    endpoint_url="http://localhost:4566/",  
    aws_access_key_id="test", #dummy key values
    aws_secret_access_key="test",
    region_name="us-east-1"
)
print("Dynamodb created")

s3 = boto3.client(
    "s3",
    endpoint_url="http://localhost:4566/",
    aws_access_key_id="test",
    aws_secret_access_key="test",
    region_name="us-east-1"
)
print("boto3 created")

dynamodb.create_table(
    TableName="items",
     KeySchema=[
        {
            'AttributeName': 'id',
            'KeyType': 'HASH'
        },
     ],
    AttributeDefinitions=[
    {
        'AttributeName': 'id',
        'AttributeType': "S"
    },
],
    BillingMode="PAY_PER_REQUEST"
)
print("table created")

s3.create_bucket(
    Bucket="items-bucket"
)
print("item bucket created")