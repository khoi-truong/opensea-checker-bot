from typing import Optional

import requests

import config
from asset import Asset, AssetIdentifier, to_asset

ASSETS_API_URL = "https://api.opensea.io/api/v1/assets"
EVENTS_API_URL = "https://api.opensea.io/api/v1/events"


def get_asset(identifier: AssetIdentifier) -> Optional[Asset]:
    try:
        response = requests.get(
            url=ASSETS_API_URL,
            params={
                'asset_contract_address': identifier.contract_address,
                'token_ids': identifier.token_id
            }
        )
        json = response.json()
        assets_json = json['assets']
        asset_json = assets_json[0]
        return to_asset(asset_json)
    except IndexError:
        return None
    except Exception as e:
        if config.DEBUG:
            print(e)
        return None


def get_created_event(identifier: AssetIdentifier) -> Optional[str]:
    try:
        response = requests.get(
            url=EVENTS_API_URL,
            params={
                'asset_contract_address': identifier.contract_address,
                'token_id': identifier.token_id,
                'event_type': 'created'
            }
        )
        json = response.json()
        events_json = json['asset_events']
        if len(events_json) > 0:
            return 'created'
    except IndexError:
        return None
    except Exception as e:
        if config.DEBUG:
            print(e)
        return None
