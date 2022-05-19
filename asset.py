from functools import reduce
from typing import Optional

from persistent import Persistent, list

import config

ETHERSCAN_URL = "https://etherscan.io/address/"


class AssetContract(Persistent):
    address: str
    name: str
    external_link: Optional[str]
    image_url: Optional[str]

    def __init__(
        self,
        address: str,
        name: str,
        external_link: Optional[str] = None,
        image_url: Optional[str] = None
    ):
        self.address = address
        self.name = name
        self.external_link = external_link
        self.image_url = image_url


class AssetIdentifier:
    contract_address: str
    token_id: str

    def __init__(self, contract_address: str, token_id: str):
        self.contract_address = contract_address
        self.token_id = token_id

    def to_str(self) -> str:
        return fr"""{self.contract_address}/{self.token_id}"""


def to_asset_identifier(identifier: str) -> Optional[AssetIdentifier]:
    if not identifier.startswith('0x'):
        return None
    if identifier.find('/') != -1:
        parts = identifier.split('/')
        if len(parts) != 2:
            return None
        return AssetIdentifier(contract_address=parts[0], token_id=parts[1])
    else:
        return None


class Asset(Persistent):
    name: str
    contract: AssetContract
    token_id: str
    creator: str
    url: str
    external_link: Optional[str]
    image_url: Optional[str]
    traits: list.PersistentList

    def __init__(
        self,
        name: str,
        contract: AssetContract,
        token_id: str,
        creator: str,
        url: Optional[str] = None,
        external_link: Optional[str] = None,
        image_url: Optional[str] = None,
        traits: list.PersistentList = None
    ):
        if traits is None:
            traits = list.PersistentList()
        self.name = name
        self.contract = contract
        self.token_id = token_id
        self.creator = creator
        if url is None:
            self.url = f'https://opensea.io/assets/{contract.address}/{token_id}'
        else:
            self.url = url
        self.external_link = external_link
        self.image_url = image_url
        self.traits = traits

    def __get_identifier(self) -> AssetIdentifier:
        return AssetIdentifier(contract_address=self.contract.address, token_id=self.token_id)

    def __get_info(self) -> str:
        contract = self.contract.name
        if self.contract.external_link is not None:
            contract = fr"""<a href="{self.contract.external_link}">{self.contract.name}</a>"""
        adr = self.contract.address
        address = fr"""<a href="{ETHERSCAN_URL}{adr}">{adr}</a>"""
        return fr"""
- Contract: {contract}
- Address: {address}
- Token: {self.token_id}
- Name: {self.name}
- Creator: {self.creator}
- <a href="{self.url}">OpenSea</a> | <a href="{self.external_link}">Link</a>
        {self.traits_info}"""

    def __get_traits_info(self) -> str:
        def __append_trait(accumulator: str, trait: str) -> str:
            return f"{accumulator}\n- {trait}"

        if not self.traits:
            return ""
        else:
            return f"""\n<b>PROPERTIES</b>{reduce(__append_trait, self.traits, "")}"""

    def debug_str(self, indent: int = 0) -> str:
        indent_str = '    ' * indent
        return f"""{{
    {indent_str}"name": "{self.name}",
    {indent_str}"url": "{self.url}",
    {indent_str}"image_url": "{self.image_url}",
{indent_str}}}"""

    def debug(self):
        if config.DEBUG:
            print(f"""Asset: {self.debug_str(indent=1)}""")

    identifier = property(__get_identifier)
    info = property(__get_info)
    traits_info = property(__get_traits_info)


def to_asset(json) -> Asset:
    contract = AssetContract(
        address=json['asset_contract']['address'],
        name=json['asset_contract']['name'],
        external_link=json['asset_contract']['external_link'],
        image_url=json['asset_contract']['image_url']
    )
    username: Optional[str] = None
    try:
        username = json['creator']['user']['username']
    except TypeError:
        if config.DEBUG:
            print('Parse to Asset: User not found')
    return Asset(
        name=json['name'],
        contract=contract,
        token_id=json['token_id'],
        creator=username,
        url=json['permalink'],
        external_link=json['external_link'],
        image_url=json['image_url'],
        traits=list.PersistentList(
            map(lambda trait_json: trait_json['value'].strip(' \t\n\r'), json['traits']))
    )
