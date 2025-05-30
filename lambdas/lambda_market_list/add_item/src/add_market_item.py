import json
import os
import uuid
from datetime import datetime
import boto3

dynamodb = boto3.resource("dynamodb")
TABLE_NAME = os.environ["DYNAMODB_TABLE_NAME"]
table = dynamodb.Table(TABLE_NAME)


def lambda_handler(event, context):
    print("Processando requisição para adicionar item à lista de tarefas")

    try:
        item = json.loads(event["body"])
        response = create_item(item, table)
        return response

    except Exception as e:
        print(f"Erro ao processar a solicitação: {str(e)}")
        return create_error_response(500, f"Erro ao processar a solicitação: {str(e)}")


def create_item(item, table):
    if "name" not in item or not item["name"].strip():
        return create_error_response(400, "O nome do item é obrigatório")

    item_id = str(uuid.uuid4())
    pk = datetime.now().strftime("%Y%m%d")

    item_attributes = {
        "PK": f"LIST#{pk}",
        "SK": f"ITEM#{item_id}",
        "name": item["name"],
        "date": datetime.now().isoformat(),
        "status": "todo",
    }

    table.put_item(Item=item_attributes)

    response_body = {
        "success": True,
        "message": "Item adicionado com sucesso à lista de tarefas",
        "item": item_attributes,
    }

    return {
        "statusCode": 201,
        "body": json.dumps(response_body),
        "headers": {"Content-Type": "application/json"},
    }


def create_error_response(status_code, message):
    return {
        "statusCode": status_code,
        "body": json.dumps({"success": False, "message": message}),
        "headers": {"Content-Type": "application/json"},
    }
