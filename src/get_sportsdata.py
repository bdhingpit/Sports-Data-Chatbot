import requests
from dotenv import load_dotenv
from pyprojroot import here
import os
import pandas as pd
from sqlalchemy import create_engine
from utils.load_sportsdataio_config import LoadConfig
import json


load_dotenv()

PROJECT_ROOT = here()
SPORTSDATAIO_CFG = LoadConfig()

"""
TODO: 
Collection of data from endpoints will be stratified according to frequency of collection
e.g. team_standings, team_season_stats, player_season_stats are collected daily (after all games of the day)
while live game stats will be collected more frequently.
"""


def fetch_data(event, context):
    endpoint_name = event.get('endpoint')
    endpoint_url = getattr(SPORTSDATAIO_CFG, endpoint_name)

    if not endpoint_url:
        return {'statusCode': 400, 'body': json.dumps({'error': 'Invalid endpoint'})}

    try:
        response = requests.get(endpoint_url, timeout=10)
        response.raise_for_status()
        data = response.json

        print(f'Fetched data from {endpoint_name}: {data}')

        return {'statusCode': 200, 'body': json.dumps({'message': 'Success', 'data': data})}
    except requests.RequestException as e:
        print(f'Error fetching data from {endpoint_name}: {e}')

        return {'statusCode': '500', 'body': json.dumps({'error': str(e)})}
