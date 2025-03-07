import pandas as pd
import re
from fuzzywuzzy import fuzz
import numpy as np
import logging

class BuyerRecommendation:

    def __init__(self):
        """ Buyer Recommendation Class """
        print("--Getting Buyer Recommendation---")

    ## matrix Trim Score
    def trim_m(self, df :pd.DataFrame ,vehicle_trim : str  )  -> pd.DataFrame:
        df['Trim Score'] = df['Trim'].apply(lambda x: fuzz.ratio(x, vehicle_trim)/10 if isinstance(x, str) else 0)
        return df
#    

    ## matrix year Score
    def year_m(self, df : pd.DataFrame, vehicle_year : str)->pd.DataFrame:
        # Convert vehicle_year to numeric, if it's not already
        try:
            vehicle_year = int(vehicle_year)  # Assuming vehicle_year should be an integer
        except ValueError:
            raise ValueError("vehicle_year must be a valid integer.")
        try:
            # Optionally drop rows with NaN values in 'Year' column
            df = df.dropna(subset=['Year'])

            # Ensure 'Year' column is numeric and handle non-numeric values
            df['Year'] = pd.to_numeric(df['Year'], errors='coerce')
            # Calculate the absolute difference between each year and the input year
            df['year_diff'] = abs(df['Year'] - vehicle_year)

            # Find the maximum difference to normalize scores
            max_year_diff = df['year_diff'].max()

            # Define the scoring logic based on the absolute year difference
            def calculate_year_score(year_diff, max_diff):
                if max_diff == 0:
                    return 10
                score = 10 - (year_diff / max_diff) * 10
                # Ensure the score is not negative
                return max(score, 0)

            # Apply the scoring function to calculate YearScore
            df['Year Score'] = df['year_diff'].apply(calculate_year_score, max_diff=max_year_diff)

            return df
        except Exception as e:
            print(e)

    ## matrix mileage Score
    def mileage_m(self, df : pd.DataFrame, vehicle_mileage : str)->pd.DataFrame:
        try:
            # calculate mileage difference to get deviation
            df['Mileage_diff'] = abs(df['Mileage'] - vehicle_mileage)
            # calculate max mileage
            max_mileage_diff = df['Mileage_diff'].max()
        
            def calculate_mileage_score(mileage_diff, max_diff):
                if max_diff == 0:
                    return 10
                score = 10 - (mileage_diff / max_diff) * 10
                return max(score, 0)

            df['Mileage Score'] = df['Mileage_diff'].apply(calculate_mileage_score, max_diff=max_mileage_diff)
            return df
        except Exception as e:
            print(e)

    
    ## matrix apprasail 
    def appraisal_m(self, df : pd.DataFrame)->pd.DataFrame:
        def cal_appraisal_score(purchase_price, app_95, app_100, app_105, app_110):
            if purchase_price > app_110:
                return 10
            elif purchase_price > app_105:
                return 8
            elif purchase_price > app_100:
                return 6
            elif purchase_price > app_95:
                return 4
            else:
                return 0

        df['Appraisal Score'] = df[['Purchase Price', '95', '100','105','110']].apply(
            lambda row: cal_appraisal_score(row['Purchase Price'], row['95'], row['100'], row['105'], row['110']), axis=1
        )

        df['Count'] = 1

        return df
    
    # Categorizer
    def categorize_intensity(self, percentage: float) -> str:
        if percentage < 12.5:
            return 'Cold'
        elif percentage < 25:
            return 'Moderate'
        elif percentage < 37.5:
            return 'Warm'
        else:
            return 'Hot'
        


    def recommend_buyers(self,vehicle_row, df_sold,vehicle_source,avg_price_df):
        ## extract the required attributes
        try:
            # Convert Make, Model, Trim to lowercase and strip spaces
            for col in ['Make', 'Model', 'Trim']:
                df_sold[col] = df_sold[col].astype(str).str.lower().str.strip()

            # Convert Mileage & Year to numeric values
            df_sold['Mileage'] = pd.to_numeric(df_sold['Mileage'].astype(str).str.replace(r'[^\d]', '', regex=True), errors='coerce').fillna(0)
            df_sold['Year'] = pd.to_numeric(df_sold['Year'].astype(str).str.replace(r'[^\d]', '', regex=True), errors='coerce').fillna(0)

            # Extract vehicle attributes safely
            vehicle_make = str(vehicle_row.get('Make', '')).lower().strip()
            vehicle_model = str(vehicle_row.get('Model', '')).lower().strip()
            vehicle_trim = str(vehicle_row.get('Trim', '')).lower().strip()
            vehicle_mileage = int(re.sub(r'[^\d]', '', str(vehicle_row.get('Mileage', 0))).strip())
            vehicle_year = int(re.sub(r'[^\d]', '', str(vehicle_row.get('Year', 0))).strip())

        except Exception as e:
            print(f"Error extracting vehicle details: {e}")
            return None  # Exit early if there's an error
            
        try:
            filtered_df = df_sold[
                (df_sold['Make'] == vehicle_make) &
                (df_sold['Model'] == vehicle_model) 
            ]
            filtered_df = self.trim_m(filtered_df, vehicle_trim)
            filtered_df = self.year_m(filtered_df, vehicle_year)
            filtered_df = self.mileage_m(filtered_df, vehicle_mileage)
            filtered_df = self.appraisal_m(filtered_df)
            
            buyers = filtered_df.groupby('Buyer').agg({
                "Trim Score":"mean",
                "Year Score":"mean",
                'Mileage Score':'mean',
                "Appraisal Score":"mean",
                "Count":"sum",
                "Platform":"first"
            }).reset_index()

            ## scale count score
            buyers['Count Score'] = buyers['Count'].apply(lambda x : (x/buyers['Count'].max()) * 10)
            buyers['BScore'] = buyers['Trim Score'] + buyers['Year Score'] + buyers['Mileage Score'] + buyers['Appraisal Score'] + buyers['Count Score']
            buyers.sort_values(by='BScore',inplace=True, ascending=False)
            buyers['Score'] = buyers['BScore'].apply(lambda x : self.categorize_intensity(x))
            final_leads=self.update_lead_score(buyers,vehicle_source,avg_price_df)

            print(final_leads[['Buyer','Score']])
       
            return final_leads
        except Exception as e:

            print(e)
            return []
           

    ## standardize company name by removing potentially conflicting charactersdef clean_company_name(name):
    # Capitalize the first letter of each word
    def standardize_cname(self, name):
        name = name.title()
        # Remove punctuation except hyphens
        name = re.sub(r'[^\w\s-]', '', name)
        # Remove extra spaces
        name = name.strip()
        return name

    def update_lead_score(self, leads, vehicle_source, avg_price_df):
        """Update lead score based on purchase price and platform conditions."""

        # Standardize Buyer names
        leads['Buyer'] = leads['Buyer'].apply(self.standardize_cname)

        # Merge with avg_price_df to get the Average Purchase Price
        if 'Buyer' in avg_price_df.columns and 'Buyer' in leads.columns:
            leads = leads.merge(avg_price_df[['Buyer', 'Average Purchase Price']], on='Buyer', how='left')
        else:
            logging.warning("Missing 'Buyer' column in leads or avg_price_df")
            leads['Average Purchase Price'] = 0

        # Fill missing values
        leads['Average Purchase Price'] = leads['Average Purchase Price'].fillna(0)

        # Ensure 'Platform' column exists
        if 'Platform' not in leads.columns:
            leads['Platform'] = ""

        # Define conditions
        conditions = [
            (leads['Average Purchase Price'] >= 105) & (leads['Score'] == 'Cold'),
            (leads['Average Purchase Price'] >= 105) & (leads['Score'] == 'Warm'),
            (leads['Average Purchase Price'] >= 105) & (leads['Platform'] == 'Only Traderev') & (vehicle_source in ['Run List', 'If Bid']),
            (leads['Average Purchase Price'] >= 105) & (leads['Platform'] == 'Only Eblock') & (vehicle_source == 'TR Upcoming')
        ]

        # Define corresponding choices
        choices = ['Warm', 'Hot', 'Hot', 'Hot']

        # Apply conditions
        leads['Score'] = np.select(conditions, choices, default=leads['Score'])

        logging.info(f"Length of leads updated: {len(leads)}")
        # Define custom sorting order
        score_order = {'Hot': 0, 'Warm': 1, 'Cold': 2}
        leads['Score Order'] = leads['Score'].map(score_order)

        # Sort by Score Order
        leads = leads.sort_values(by='Score Order', ascending=True).drop(columns=['Score Order'])

        logging.info(f"Length of leads updated: {len(leads)}")

        return leads
