import json
import os
from datetime import datetime

import boto3

dynamodb = boto3.resource("dynamodb")
TABLE_NAME = os.environ["DYNAMODB_TABLE_NAME"]
table = dynamodb.Table(TABLE_NAME)


def lambda_handler(event, context):
    print("Processando requisição para atualizar item")

    try:
        item_id = event.get("pathParameters", {}).get("item_id")
        body = json.loads(event["body"])

        if "status" in body and body["status"] not in ["TODO", "DONE"]:
            response = {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps(
                    {"success": False, "message": "Status deve ser TODO ou DONE"}
                ),
            }
            return response


        # Verifica existência do item
        query_result = table.query(
            IndexName="item_id",
            KeyConditionExpression=boto3.dynamodb.conditions.Key("SK").eq(f"ITEM#{item_id}")
        ).get("Items")

        existing_item = query_result[0] if query_result else None

        if not existing_item:
            response = {
                "statusCode": 404,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps(
                    {"success": False, "message": "Item não encontrado"}
                ),
            }
            return response

        update_expr = []
        expr_values = {}
        expr_names = {}

        if "name" in body:
            update_expr.append("#nm = :name")
            expr_values[":name"] = body["name"]
            expr_names["#nm"] = "name"

        if "date" in body:
            update_expr.append("#dt = :date")
            expr_values[":date"] = body["date"]
            expr_names["#dt"] = "date"

        if "status" in body:
            update_expr.append("#st = :status")
            expr_values[":status"] = body["status"]
            expr_names["#st"] = "status"

        if not update_expr:
            response = {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps(
                    {
                        "success": False,
                        "message": "Nenhum campo válido para atualização",
                    }
                ),
            }
            return response

        # rastreia a ultima atualização
        update_expr.append("#updatedAt = :updatedAt")
        expr_values[":updatedAt"] = datetime.now().isoformat()
        expr_names["#updatedAt"] = "updatedAt"

        # atualização
        update_result = table.update_item(
            Key={"PK": existing_item["PK"], "SK": existing_item["SK"]},
            UpdateExpression="SET " + ", ".join(update_expr),
            ExpressionAttributeValues=expr_values,
            ExpressionAttributeNames=expr_names,
            ReturnValues="ALL_NEW",
        )

        # Retorna o item completo atualizado
        updated_item = update_result["Attributes"]
        response = {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(
                {
                    "success": True,
                    "message": "Item atualizado com sucesso",
                    "item": updated_item,
                },
                ensure_ascii=False,
            ),
        }
        return response

    except Exception as e:
        print(f"Erro: {str(e)}")
        response = {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(
                {"success": False, "message": f"Erro interno: {str(e)}"}
            ),
        }
        return response
