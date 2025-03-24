from typing import Dict, Optional
from urllib.parse import urljoin

import requests

from pydantic import  BaseModel


class DpPesClient:

    def __init__(
        self,
        url: str,
        apikey: str
    ):
        self.url = url
        self.apikey = apikey
    
    def get(
        self,
        route: str,
        params: Optional[Dict[str, str]] = None,
        headers: Optional[Dict[str, str]] = None
    ):
        if headers is None:
            headers = {}
        headers['px-apikey'] = self.apikey
        return requests.get(urljoin(self.url, route), params=params, headers=headers)
    
    def post(
        self,
        route: str,
        body: Optional[BaseModel] = None,
        params: Optional[Dict[str, str]] = None,
        headers: Optional[Dict[str, str]] = None
    ):
        if headers is None:
            headers = {}
        headers['px-apikey'] = self.apikey
        body_json = body.model_dump_json() if body is not None else None
        return requests.post(urljoin(self.url, route), data=body_json, params=params, headers=headers)
