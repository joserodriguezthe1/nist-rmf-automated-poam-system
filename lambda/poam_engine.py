import os
import json
import boto3
import uuid
from datetime import datetime, timedelta
from control_mapper import map_to_nist_control

dynamodb = boto3.resource('dynamodb')
sns = boto3.client('sns')

TABLE_NAME = os.environ['POAM_TABLE']
EXPORT_BUCKET = os.environ['EXPORT_BUCKET']
RISK_HIGH_DAYS = int(os.environ['RISK_HIGH_DAYS'])
RISK_MEDIUM_DAYS = int(os.environ['RISK_MEDIUM_DAYS'])
RISK_LOW_DAYS = int(os.environ['RISK_LOW_DAYS'])
SNS_TOPIC_ARN = os.environ.get('SNS_TOPIC_ARN', '')


def get_milestone_date(severity):
    days = {
        'HIGH': RISK_HIGH_DAYS,
        'MEDIUM': RISK_MEDIUM_DAYS,
        'LOW': RISK_LOW_DAYS
    }.get(severity, RISK_LOW_DAYS)
    return (datetime.utcnow() + timedelta(days=days)).strftime('%Y-%m-%d')


def send_sns_alert(poam_id, title, severity, control_id, scheduled_completion):
    if not SNS_TOPIC_ARN or severity != 'HIGH':
        return
    try:
        sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject=f'HIGH Severity POAM Created — {control_id}',
            Message=f"""
A new HIGH severity POAM has been automatically created.

POAM ID: {poam_id}
Title: {title}
NIST Control: {control_id}
Risk Rating: {severity}
Due Date: {scheduled_completion}

Log into the POAM Dashboard to review and assign remediation actions.
            """
        )
        print(f'SNS alert sent for POAM {poam_id}')
    except Exception as e:
        print(f'SNS alert failed: {str(e)}')


def handler(event, context):
    table = dynamodb.Table(TABLE_NAME)

    for finding in event.get('detail', {}).get('findings', []):
        severity = finding.get('Severity', {}).get('Label', 'LOW')
        title = finding.get('Title', 'Unknown Finding')
        description = finding.get('Description', '')
        finding_id = finding.get('Id', str(uuid.uuid4()))
        resource = finding.get('Resources', [{}])[0].get('Id', 'Unknown')
        control_id = finding.get('Compliance', {}).get(
            'SecurityControlId', 'UNKNOWN')

        nist_control = map_to_nist_control(control_id)
        poam_id = str(uuid.uuid4())
        scheduled_completion = get_milestone_date(severity)

        item = {
            'poam_id': poam_id,
            'control_id': nist_control,
            'status': 'OPEN',
            'risk_rating': severity,
            'finding_id': finding_id,
            'title': title,
            'description': description,
            'resource': resource,
            'scheduled_completion': scheduled_completion,
            'milestone_1': f'Remediate {title}',
            'responsible_party': 'Security Team',
            'date_identified': datetime.utcnow().strftime('%Y-%m-%d'),
            'ttl': int((datetime.utcnow() + timedelta(days=365)).timestamp())
        }

        table.put_item(Item=item)
        print(f'POAM created: {poam_id} mapped to {nist_control}')
        send_sns_alert(poam_id, title, severity,
                       nist_control, scheduled_completion)

    return {
        'statusCode': 200,
        'body': json.dumps('POAMs processed successfully')
    }
