import logging
from recommendation import BuyerRecommendation
from models import *
from utils import *
from pyzohocrm import TokenManager, ZohoApi
import os
from dotenv import load_dotenv
load_dotenv()

TEMP_DIR = "/tmp/"

TOKEN_INSTANCE =  TokenManager(
                                domain_name="Canada",
                                refresh_token=os.getenv("REFRESH_TOKEN"),
                                client_id=os.getenv("CLIENT_ZOHO_ID"),
                                client_secret=os.getenv("CLIENT_ZOHO_SECRET"),
                                grant_type="refresh_token",
                                token_dir=TEMP_DIR
                                )
buyer_instance = BuyerRecommendation()

ZOHO_API = ZohoApi(base_url="https://www.zohoapis.ca/crm/v2")

async def generate_leads(vehicle_row, sold_database=None, avg_purchase_price_df=None):
    try:
        logging.info(f"vehicle_row : {vehicle_row}")
        access_token = TOKEN_INSTANCE.get_access_token()
        vehicle_id = vehicle_row['id']
        ## update URL field with bubble app vehicle listing link 
        url = f"https://tradegeek.io/vehicle_details/{vehicle_id}"

        update_response = ZOHO_API.update_record(moduleName="Vehicles", id=vehicle_id, data={"data": [{"id": vehicle_id,"URL":url}]}, token=access_token)
        logging.info(f"Update URL Response : {update_response.json()}")
        recommendations_df = buyer_instance.recommend_buyers(vehicle_row, sold_database, vehicle_row['source'], avg_purchase_price_df  )
        logging.info(f"length of recommendation received for RUNLIST vehicle  :  {len(recommendations_df)}")
        vehicle_name = f"{vehicle_row.get('Make', '')} {vehicle_row.get('Model', '')} {vehicle_row.get('Trim', '')} {str(vehicle_row.get('Year', ''))} - {vehicle_row.get('Vin', '')}".strip()


        data = []
        ## convert this into batch request
        for index, row in recommendations_df.iloc[:20][::-1].iterrows():
            try:
            
                buyer_name = standardize_cname(row["Buyer"])
                logging.info(f"buyer_name : {buyer_name}")
                account_info = ZOHO_API.search_record(moduleName="Accounts",query= f"Account_Name:equals:{buyer_name}", token=access_token).json().get("data")[0]
                logging.info(f"account_info : {account_info}")
                buyer_id = account_info.get("id")

                if buyer_id:
                    lead_data = {
                        "Last_Name": vehicle_name,
                        "Lead_Score": row["Score"],
                        "Vehicle_State": "Available",
                        "Buyer_Text": buyer_name,
                        "Vehicle_id": vehicle_id,
                        "Progress_Status": "To Be Contacted",
                        "buyer_id": buyer_id,
                    }
                    data.append(lead_data)
        
            except Exception as e:
                print(e)

        payload = {"data": data}
        lead_attach_response = ZOHO_API.create_record(moduleName="Leads", data=payload, token=access_token)
        logging.info(f"Lead Attach Response : {lead_attach_response.status_code}")
        if lead_attach_response.status_code == 201 or lead_attach_response.status_code == 200:
            return {"status": "success","code": lead_attach_response.status_code,"message": lead_attach_response.json()}
        else:
            return {"status": "error","code": lead_attach_response.status_code,"message": lead_attach_response.json()}
       
    except Exception as e:
        logging.error(f"Error Occured While Adding Leads {e}")
        return {"status": "error","code": 500,"message": str(e)}

