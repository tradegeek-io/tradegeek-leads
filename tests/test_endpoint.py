from unittest.mock import patch
from src.funcmain import *
import pytest


@pytest.mark.asyncio
@patch("src.apis.token_manager.TokenManager.get_access_token")
@patch("src.apis.VehicleApi.add_form_vehicle_into_crm")
async def test_process_vehicle_and_lead(
    add_form_vehicle_into_crm_mock, get_access_token_mock
):
    # Set up the mock objects and their return values
    get_access_token_mock.return_value = "mock_access_token"
    add_form_vehicle_into_crm_mock.return_value = {
        "data": [{"details": {"id": "12345"}}]
    }

    form_data = {
        "Name": "test_vehicle_3",
        "Make": "Nissan",
        "Model": "Rogue",
        "Year": 2016,
        "VIN": "GSDG345",
        "Mileage": "87560mi",
        "URL": "https://azure.microsoft.com/en-in/get-started/azure-portal",
        "Notes": "seller note",
        "Price": 10000,
        "Body_Type": "Sedan",
        "Pickup_Location": "New York",
        "DisplacementL": 2.5,
        "Number_of_Cylinders": 4,
        "Drivetrain": "Front-wheel drive",
        "Transmission": "Automatic",
        "Number_of_Passengers": 5,
        "Number_of_Doors": 4,
        "Tires": "All-season",
        "Tire_Condition": "Good",
        "Carfax": 12379,
        "Trim": "AWD 4dr SV",
        "Options": "Sunroof, Leather seats, Navigation system",
        "Declarations": "None",
        "Exterior_Image_URLs": [
            "https://a1a38c43d0c31f6413020becb68e6712.cdn.bubble.io/f1718354899723x197748343562582660/bubble-interior1718354898845.png",
            "https://a1a38c43d0c31f6413020becb68e6712.cdn.bubble.io/f1718354900473x680258562581412900/bubble-interior1718354898846.png",
        ],
        "Interior_Image_URLs": [
            "https://a1a38c43d0c31f6413020becb68e6712.cdn.bubble.io/f1718354899723x197748343562582660/bubble-interior1718354898845.png",
            "https://a1a38c43d0c31f6413020becb68e6712.cdn.bubble.io/f1718354900473x680258562581412900/bubble-interior1718354898846.png",
        ],
        "Damaged_Image_URLs": [
            "https://a1a38c43d0c31f6413020becb68e6712.cdn.bubble.io/f1718354906996x559854550927514560/bubble-damage-photos1718354906236.png",
            "https://a1a38c43d0c31f6413020becb68e6712.cdn.bubble.io/f1718354908364x110490990900387060/bubble-damage-photos1718354906237.png",
        ],
        "Exterior_Color": "Black",
        "Source": "Website Input",
        "Vehicle_Image_Url": "https://scontent-iad3-2.xx.fbcdn.net/v/t39.30808-6/445235041_7555021634567183_8163520236057280227_n.jpg?stp=c0.29.261.261a_dst-jpg_p261x260&_nc_cat=106&ccb=1-7&_nc_sid=5f2048&_nc_ohc=F0rHF4bIJM4Q7kNvgEWKN6-&_nc_ht=scontent-iad3-2.xx&oh=00_AYA-RoCoTKgDjoQL1kTxt9A3rivryo0LyWo4HBSKWsvyIw&oe=66753DD3",
        "Carfax_URL": "https://a1a38c43d0c31f6413020becb68e6712.cdn.bubble.io/f1718354906996x559854550927514560/bubble-damage-photos1718354906236.png",
        "Seller_ID": "3384000000451081",
    }

    # Encode the form data properly for `application/x-www-form-urlencoded`
    encoded_form_data = "&".join(f"{key}={value}" for key, value in form_data.items())

    req = func.HttpRequest(
        body=encoded_form_data.encode("utf-8"),
        method="POST",
        url="/generate-lead",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    response = await process_vehicle_and_lead(req)
    print(response.get_body())
    # Assert the response
    assert response.status_code == 200


@pytest.mark.asyncio
@patch("src.apis.VehicleApi.update_vehicle")  # Mock VehicleApi
@patch("src.apis.LeadApi.get_specific_lead")
@patch("src.apis.token_manager.TokenManager.get_access_token")  # Mock TokenManager
async def test_reactivate_vehicle(
    get_access_token_mock, get_specific_lead_mock, update_vehicle_mock
):
    get_access_token_mock.return_value = "mock_access_token"
    get_specific_lead_mock.return_value = [
        {"buyer_id": {"name": "Buyer1"}},
        {"buyer_id": {"name": "Buyer2"}},
    ]

    update_vehicle_mock.return_value = {"status": "success"}

    form_data = {
        "Vehicle_ID": "mock_vehicle_id",
        "Vehicle_VIN": "mock_vin",
        "Make": "Test Make",
        "Model": "Test Model",
        "Year": "2022",
        "Trim": "Base",
        "Mileage": "10000",
        "Price": "15000",
    }

    # Mock request with necessary form data
    encoded_form_data = "&".join(f"{key}={value}" for key, value in form_data.items())
    req = func.HttpRequest(
        body=encoded_form_data.encode("utf-8"),
        method="POST",
        url="/api/reactivate_vehicle",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    response = await reactivate_vehicle(req)

    # Assert the response
    assert response.status_code == 200
