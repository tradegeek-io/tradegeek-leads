from pydantic import BaseModel, Field
from typing import Optional
class Vehicle(BaseModel):
    Name: Optional[str] = None
    Make: str
    Model: str
    Year: str
    VIN: str
    Mileage: str
    URL: Optional[str] = None
    Notes: Optional[str] = None
    Price: Optional[str] = None
    Body_Type: Optional[str] = None
    Pickup_Location: Optional[str] = None
    DisplacementL: Optional[str] = None
    Number_of_Cylinders: Optional[str] = None
    Drivetrain: Optional[str] = None
    Transmission: Optional[str] = None
    Number_of_Passengers: Optional[str] = None
    Number_of_Doors: Optional[str] = None
    Tires: Optional[str] = None
    Tire_Condition: Optional[str] = None
    Carfax: Optional[str] = None
    Trim: Optional[str] = None
    Options: Optional[str] = None
    Declarations: Optional[str] = None
    Exterior_Image_URLs: Optional[str] = None
    Interior_Image_URLs: Optional[str] = None
    Damaged_Image_URLs: Optional[str] = None
    Exterior_Color: Optional[str] = None
    Source: Optional[str] = None
    Seller_Name: Optional[str] = None
    Seller_Email: Optional[str] = None
    Vehicle_ID: Optional[str] = None
    Vehicle_Image_Url: Optional[str] = None
    Carfax_URL: Optional[str] = None
    Seller_ID: Optional[str] = None
    Seller_Name : Optional[str] = None
    VehicleDescription : Optional[str] = None
    VehicleCaptureType : Optional[str] = None
    VehicleConditionScore : Optional[str] = None
    Auction_URL : Optional[str] = None
    Auction_Date : Optional[str] = None
    Status : Optional[str] = None


class ActivationVehicle(BaseModel):
    Vehicle_ID : str
    Vehicle_VIN : str 
    Make : str 
    Model : str 
    Year : str 
    Trim : str  
    Mileage : str
    Price : str
