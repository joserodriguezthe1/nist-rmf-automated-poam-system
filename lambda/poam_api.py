import json
import boto3
import os
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
TABLE_NAME = os.environ['POAM_TABLE']


class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return str(obj)
        return super().default(obj)


def handler(event, context):
    table = dynamodb.Table(TABLE_NAME)

    http_method = event.get('httpMethod', 'GET')
    path = event.get('path', '/poams')

    if http_method == 'GET' and path == '/poams':
        response = table.scan()
        items = response.get('Items', [])
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(items, cls=DecimalEncoder)
        }

    return {
        'statusCode': 404,
        'body': json.dumps('Route not found')
    }
