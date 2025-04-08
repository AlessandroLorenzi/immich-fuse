import os
import requests
from datetime import datetime
from functools import lru_cache
from cachetools import cached, TTLCache


class ImmichApi:
    def __init__(self):
        api_url = os.environ.get("IMMICH_API_URL")
        api_key = os.environ.get("IMMICH_API_KEY")

        if api_url is None or api_key is None:
            raise ValueError(
                "IMMICH_API_URL and IMMICH_API_KEY environment variables must be set."
            )

        self.http_client = CustomHttpClient(api_url, headers={"x-api-key": api_key})
    
    @cached(cache=TTLCache(maxsize=1, ttl=600))
    def get_people(self):
        people = self.http_client.get("/people")

        people_list = [person["name"] for person in people["people"]]
        people_list = [person for person in people_list if person != ""]
        return people_list
    
    @cached(cache=TTLCache(maxsize=1024, ttl=600))
    def get_buckets(self, person_name=None, favs=None):
        person_id = None
        if person_name:
            person_id = self.get_person_id(person_name)
        buckets = self.http_client.get(
            "/timeline/buckets",
            params={
                "isArchived": "false",
                "size": "MONTH",
                "personId": person_id,
                "isFavorite": favs,
            },
        )
        bucket_names = [bucket["timeBucket"] for bucket in buckets]
        return bucket_names

    @cached(cache=TTLCache(maxsize=1024, ttl=600))
    def get_assets(self, bucket_name, person_name=None, favs=None):
        person_id = None
        if person_name:
            person_id = self.get_person_id(person_name)

        assets = []
        bucket_assets = self.http_client.get(
            "/timeline/bucket",
            params={
                "isArchived": "false",
                "size": "MONTH",
                "timeBucket": bucket_name,
                "personId": person_id,
                "isFavorite": favs,
            },
        )

        for asset in bucket_assets:
            asset_id = asset["id"]
            originalFileName = asset["originalFileName"]
            assets.append(f"{asset_id}_{originalFileName}")
        return assets

    @lru_cache(maxsize=128)
    def get_person_id(self, person_name):
        people = self.http_client.get("/people")
        person_id = None
        for person in people["people"]:
            if person["name"] == person_name:
                person_id = person["id"]
                break
        return person_id

    @lru_cache(maxsize=1024)
    def get_asset_stats(self, asset_id):
        asset = self.http_client.get(f"/assets/{asset_id}")
        if asset:
            return {
                "id": asset["id"],
                "file_size_in_byte": asset["exifInfo"]["fileSizeInByte"],
                "date_time_original": datetime.fromisoformat(
                    asset["exifInfo"]["dateTimeOriginal"]
                ).timestamp(),
                "modifify_date": datetime.fromisoformat(
                    asset["exifInfo"]["modifyDate"]
                ).timestamp(),
            }
        else:
            raise Exception(f"Asset with ID {asset_id} not found.")

    @cached(cache=TTLCache(maxsize=128, ttl=600))
    def get_asset(self, asset_id):
        asset = self.http_client.get_asset(f"/assets/{asset_id}/original")
        return asset


class CustomHttpClient:
    def __init__(self, base_url, headers=None):
        self.base_url = base_url
        self.session = requests.Session()
        if headers:
            self.session.headers.update(headers)

    def get(self, endpoint, **kwargs):
        url = f"{self.base_url}{endpoint}"
        rsp = self.session.get(url, **kwargs)
        if rsp.status_code == 200:
            return rsp.json()
        else:
            raise Exception(f"Error: {rsp.status_code} - {rsp.text}")

    def get_asset(self, endpoint, **kwargs):
        url = f"{self.base_url}{endpoint}"
        rsp = self.session.get(url, **kwargs)
        if rsp.status_code == 200:
            return rsp.content
        else:
            raise Exception(f"Error: {rsp.status_code} - {rsp.text}")

    def post(self, endpoint, **kwargs):
        url = f"{self.base_url}{endpoint}"
        rsp = self.session.post(url, **kwargs)
        if rsp.status_code == 200:
            return rsp.json()
        else:
            raise Exception(f"Error: {rsp.status_code} - {rsp.text}")

    def put(self, endpoint, **kwargs):
        url = f"{self.base_url}{endpoint}"
        return self.session.put(url, **kwargs)

    def delete(self, endpoint, **kwargs):
        url = f"{self.base_url}{endpoint}"
        return self.session.delete(url, **kwargs)
