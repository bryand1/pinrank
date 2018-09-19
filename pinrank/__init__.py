from typing import Dict, List, Optional
import urllib.parse

import requests

from . import config, util
from .err import PinrankException


class Pinrank:

    @classmethod
    def login(cls, email: str, password: str):
        session = util.requests_retry_session()
        headers = config.headers.copy()
        # Land on home page
        resp = session.get("https://www.pinterest.com", headers=headers)
        assert resp.status_code == 200
        # Land on login page
        resp = session.get("https://www.pinterest.com/login/", headers=headers)
        assert resp.status_code == 200
        # UnauthUserDataResource
        headers['Accept'] = 'application/json, text/javascript, */*, q=0.01'
        headers['Referer'] = 'https://www.pinterest.com/'
        headers['X-Requested-With'] = 'XMLHttpRequest'
        headers['X-Pinterest-AppState'] = 'active'
        url = ("https://www.pinterest.com/resource/UnauthUserDataResource/get/?source_url="
               "%2Flogin%2F&data=%7B%22options%22%3A%7B%7D%2C%22context%22%3A%7B%7D%7D&_=" + util.ts(str))
        resp = session.get(url, headers=headers)
        assert resp.status_code == 200
        # UserSessionResource/create
        csrftoken = None
        for c in session.cookies:
            if c.name == 'csrftoken':
                csrftoken = c.value
                break
        assert csrftoken is not None
        headers['X-CSRFtoken'] = csrftoken
        headers['Content-Type'] = 'application/x-www-form-urlencoded'
        url = "https://www.pinterest.com/resource/UserSessionResource/create/"
        data = ("source_url=%2Flogin%2F&data=%7B%22options%22%3A%7B%22username_or_email"
                "%22%3A%22{email}%22%2C%22password%22%3A%22{password}%22%2C%22"
                "app_type_from_client%22%3A5%7D%2C%22context%22%3A%7B%7D%7D")
        data = data.format(email=urllib.parse.quote(email), password=urllib.parse.quote(password))
        resp = session.post(url, headers=headers, data=data)
        assert resp.status_code == 200
        return Pinrank(session)

    def __init__(self, session: requests.Session):
        self.session = session
        self._is_logged_in = True

    def search(self, keyword: str, fields: List[str] = None) -> Optional[List[Dict]]:
        headers = config.headers.copy()
        # Obtain cookies from session
        url = "https://www.pinterest.com/resource/BaseSearchResource/get/" \
              "?source_url=%2Fsearch%2Fpins%2F%3Fq%3Dhalloween%2520costumes" \
              "%26rs%3Dtyped%26term_meta%5B%5D%3Dhalloween%257Ctyped%26" \
              "term_meta%5B%5D%3Dcostumes%257Ctyped&data=%7B%22options%22%3A%7B%22" \
              "article%22%3Anull%2C%22auto_correction_disabled%22%3Afalse%2C%22corpus" \
              "%22%3Anull%2C%22customized_rerank_type%22%3Anull%2C%22filters%22%3Anull" \
              "%2C%22page_size%22%3Anull%2C%22query%22%3A%22halloween%20costumes%22%2C%22" \
              "query_pin_sigs%22%3Anull%2C%22redux_normalize_feed%22%3Atrue%2C%22rs" \
              "%22%3A%22typed%22%2C%22scope%22%3A%22pins%22%2C%22source_id%22%3A" \
              "null%7D%2C%22context%22%3A%7B%7D%7D&_=" + util.ts(str)
        resp = self.session.get(url, headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        if fields is None:
            fields = ['domain', 'images', 'link', 'created_at', 'dominant_color', 'id', 'grid_title', 'description']
        pins = []
        for result in data['resource_response']['data']['results']:
            pin = {field: result.get(field) for field in fields}
            pins.append(pin)
        return pins

    def saves(self, pins: List[Dict]) -> List[Dict]:
        # Obtain cookies from session
        raise NotImplementedError
