import boto3
import csv
import io
import os
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
s3 = boto3.client('s3')

TABLE_NAME = os.environ['POAM_TABLE']
EXPORT_BUCKET = os.environ['EXPORT_BUCKET']


def handler(event, context):
    table = dynamodb.Table(TABLE_NAME)
    response = table.scan()
    items = response.get('Items', [])

    output = io.StringIO()
    fieldnames = [
        'poam_id', 'control_id', 'status', 'risk_rating',
        'title', 'description', 'resource', 'scheduled_completion',
        'milestone_1', 'responsible_party', 'date_identified'
    ]

    writer = csv.DictWriter(
        output, fieldnames=fieldnames, extrasaction='ignore')
    writer.writeheader()
    writer.writerows(items)

    file_name = f'poam-export-{datetime.utcnow().strftime("%Y-%m-%d")}.csv'

    s3.put_object(
        Bucket=EXPORT_BUCKET,
        Key=f'exports/{file_name}',
        Body=output.getvalue(),
        ContentType='text/csv'
    )

    print(
        f'Exported {len(items)} POAMs to s3://{EXPORT_BUCKET}/exports/{file_name}')

    return {
        'statusCode': 200,
        'body': f'Exported {len(items)} POAMs'
    }
