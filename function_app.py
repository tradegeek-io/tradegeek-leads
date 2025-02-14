import azure.functions as func
import logging
import pandas as pd
from src.funcmain import *
import json 

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

global sold_df, average_price_df
sold_df = pd.read_csv("sold_appraise.csv", low_memory=False)
average_price_df = pd.read_csv("average_purchase.csv")


@app.route(route="ping", methods=['GET'])
async def ping(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Ping request received.')
    return func.HttpResponse("Service is up", status_code=200)

        
@app.route(route="leads/add", methods=["POST"])
async def leads(req: func.HttpRequest) -> func.HttpResponse:
    logging.info(f"Request received from {req.url}")

    data = req.form
    try:
        response = await generate_leads(
            data, sold_database=sold_df, avg_purchase_price_df=average_price_df
        )
        return func.HttpResponse(json.dumps(response))
    
    except Exception as e:
        logging.error(f"Error processing request: {str(e)}")
        return func.HttpResponse("Internal server error", status_code=500)

