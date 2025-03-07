import logging
from recommendation import BuyerRecommendation
from models import *
from utils import *
from pyzohocrm import TokenManager, ZohoApi
import os
from dotenv import load_dotenv
load_dotenv()
import requests
import phonenumbers
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
        for index, row in recommendations_df.iloc[:30][::-1].iterrows():
            try:
            
                buyer_name = standardize_cname(row["Buyer"])
                logging.info(f"buyer_name : {buyer_name}")
                account_info = ZOHO_API.search_record(moduleName="Accounts",query= f"Account_Name:equals:{buyer_name}", token=access_token).json().get("data")[0]
                logging.info(f"account_info : {account_info}")
                buyer_id = account_info.get("id")

                try:
                    buyer_phone = format_phone_number(account_info.get("Dealer_Phone",None).split("ext")[0])
                except Exception as e:
                    logging.error(f"Error Occured While Formatting Phone Number {e}")
                    buyer_phone = None

                if buyer_id:
                    lead_data = {
                        "Last_Name": vehicle_name,
                        "Lead_Score": row["Score"],
                        "Vehicle_State": "Available",
                        "Buyer_Text": buyer_name,
                        "Vehicle_id": vehicle_id,
                        "Progress_Status": "To Be Contacted",
                        "buyer_id": buyer_id,
                        "Dealer_Phone":buyer_phone
                    }

                    data.append(lead_data)
        
            except Exception as e:
                print(e)

        payload = {"data": data}
        lead_attach_response = ZOHO_API.create_record(moduleName="Leads", data=payload, token=access_token)

        for lead_crm_response, lead_data in zip(lead_attach_response.json().get("data"), data):
            lead_record_id = lead_crm_response.get("details").get("id")

            try:
                number  = format_phone_number(lead_data.get("Dealer_Phone","").split("ext")[0])
            except Exception as e:
                number = ""

            bubble_lead_body = {
                "lead_score": lead_data.get("Lead_Score"),
                "offer_amount":"",
                "buyer_name": lead_data.get("Buyer_Text"),
                "progres_status": lead_data.get("Progress_Status"),
                "zoho_record_id":lead_record_id,
                "zoho_buyer_id":lead_data.get("buyer_id"),
                "zoho_vehicle_id":lead_data.get("Vehicle_id"),
                "phone_number":number

            }
            logging.info(f"Bubble Lead Body : {bubble_lead_body}")
            bubble_response = requests.post(url=os.getenv("BUBBLE_LEAD_API"), json=bubble_lead_body)
            logging.info(f"Bubble Lead Response : {bubble_response.status_code}")

        logging.info(f"Lead Attach Response : {lead_attach_response.status_code}")
        if lead_attach_response.status_code == 201 or lead_attach_response.status_code == 200:
            return {"status": "success","code": lead_attach_response.status_code,"message": lead_attach_response.json()}
        else:
            return {"status": "error","code": lead_attach_response.status_code,"message": lead_attach_response.json()}
       
    except Exception as e:
        logging.error(f"Error Occured While Adding Leads {e}")
        return {"status": "error","code": 500,"message": str(e)}

