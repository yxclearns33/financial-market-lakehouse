import requests
import pandas as pd
import duckdb
import os
from datetime import datetime


database_path = "data/financial_market.duckdb"


country = {
    "GBR": "United Kingdom"
}


indicators = {
    "GDP_GROWTH": "NY.GDP.MKTP.KD.ZG",
    "INFLATION": "FP.CPI.TOTL.ZG",
    "UNEMPLOYMENT": "SL.UEM.TOTL.ZS"
}


print("Starting World Bank ingestion...")


rows = []


for country_code, country_name in country.items():

    for indicator_name, indicator_code in indicators.items():

        print(f"Downloading {country_name} - {indicator_name}")

        url = (
            f"https://api.worldbank.org/v2/"
            f"country/{country_code}/indicator/{indicator_code}"
            f"?format=json&per_page=100"
        )

        response = requests.get(url)

        data = response.json()

        records = data[1]


        for item in records:

            if item["value"] is not None:

                rows.append({
                    "country": country_name,
                    "country_code": country_code,
                    "indicator": indicator_name,
                    "year": int(item["date"]),
                    "value": item["value"],
                    "ingestion_time": datetime.now()
                })


df = pd.DataFrame(rows)


print("Writing to DuckDB...")


os.makedirs("data", exist_ok=True)


conn = duckdb.connect(database_path)


conn.execute("""
CREATE OR REPLACE TABLE bronze_uk_economic_indicators AS
SELECT *
FROM df
""")


conn.close()


print("World Bank ingestion complete!")
print(datetime.now())