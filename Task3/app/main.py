from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
from typing import List
from concurrent.futures import ThreadPoolExecutor
import asyncio
import aiofiles
from pathlib import Path

app = FastAPI()
executor = ThreadPoolExecutor()

CSV_FILE = 'items.csv'

class Record(BaseModel):
    name: str
    state_province: str

def read_csv_sync():
    if Path(CSV_FILE).exists():
        return pd.read_csv(CSV_FILE)
    else:
        return pd.DataFrame(columns=['name', 'state_province'])

def write_csv_sync(df: pd.DataFrame):
    df.to_csv(CSV_FILE, index=False, mode='a')

@app.get("/records", response_model=List[Record])
async def get_records():
    loop = asyncio.get_event_loop()
    df = await loop.run_in_executor(executor, read_csv_sync)
    records = df.to_dict(orient='records')
    return [Record(**record) for record in records]

@app.post("/records")
async def add_record(record: Record):
    loop = asyncio.get_event_loop()
    df = await loop.run_in_executor(executor, read_csv_sync)
    if record.name in df['name'].values:
        raise HTTPException(status_code=400, detail="Record with this name already exists.")
    df = pd.DataFrame(columns=['name', 'state_province'])
    record = {'name': record.name, 'state_province': record.state_province}
    new_row_df = pd.DataFrame([record])
    df = pd.concat([df, new_row_df], ignore_index=True)
    await loop.run_in_executor(executor, write_csv_sync, df)
    return record

@app.put("/records/{name}")
async def update_record(name: str, record: Record):
    loop = asyncio.get_event_loop()
    df = await loop.run_in_executor(executor, read_csv_sync)
    if name not in df['name'].values:
        raise HTTPException(status_code=404, detail="Record not found.")
    df.loc[df['name'] == name, 'state_province'] = record.state_province
    await loop.run_in_executor(executor, write_csv_sync, df)
    return record