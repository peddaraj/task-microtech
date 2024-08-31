from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx, json, csv

app = FastAPI()
EXTERNAL_API_URL = "http://universities.hipolabs.com/search?country=Canada"

@app.get("/fetch-data")
async def fetch_data():
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(EXTERNAL_API_URL)
            response.raise_for_status()
            data = response.json()
            print(data)
            filename = 'items.csv'
            with open(filename, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(['name', 'state-province'])
                for item in data:
                    name = item.get("name", "")
                    state_province = item.get("state-province", "")
                    writer.writerow([name, state_province])
            return "Success!"
        except httpx.HTTPStatusError as http_err:
            raise HTTPException(status_code=response.status_code, detail=str(http_err))
        except Exception as err:
            raise HTTPException(status_code=500, detail=str(err))
