import os
import requests
from datetime import datetime

class ImmichApi:
    def __init__(self):
        api_url = os.environ.get("IMMICH_API_URL")
        api_key = os.environ.get("IMMICH_API_KEY")

        if api_url is None or api_key is None:
            raise ValueError(
                "IMMICH_API_URL and IMMICH_API_KEY environment variables must be set."
            )

        self.http_client = CustomHttpClient(api_url, headers={"x-api-key": api_key})
        # TODO: add cache for the photos

    def get_people(self):
        people = self.http_client.get("/people")

        people_list = [person["name"] for person in people["people"]]
        people_list = [person for person in people_list if person != ""]
        return people_list

    def get_buckets_by_person(self, person_name):
        people = self.http_client.get("/people")
        person_id = None
        for person in people["people"]:
            if person["name"] == person_name:
                person_id = person["id"]
                break
        if person_id is None:
            return []

        buckets = self.http_client.get(
            "/timeline/buckets",
            params={
                "isArchived": "false",
                "personId": person_id,
                "size": "MONTH",
            },
        )
        bucket_names = [bucket["timeBucket"] for bucket in buckets]
        return bucket_names

    def get_photos_by_person(self, person_name, bucket_name):
        people = self.http_client.get("/people")
        person_id = None
        for person in people["people"]:
            if person["name"] == person_name:
                person_id = person["id"]
                break
        if person_id is None:
            return []

        photos = []
        bucket_photos = self.http_client.get(
            "/timeline/bucket",
            params={
                "isArchived": "false",
                "personId": person_id,
                "size": "MONTH",
                "timeBucket": bucket_name,
            },
        )
        for photo in bucket_photos:
            photo_id = photo["id"]
            originalFileName = photo["originalFileName"]
            photos.append(f"{photo_id}_{originalFileName}")
        return photos

    def get_asset_stats(self, photo_id):
        asset = self.http_client.get(f"/assets/{photo_id}")
        if asset:
            return {
                "id": asset["id"],
                "file_size_in_byte": asset["exifInfo"]["fileSizeInByte"],
                "date_time_original":  datetime.fromisoformat(asset["exifInfo"]["dateTimeOriginal"]).timestamp(),
                "modifify_date": datetime.fromisoformat(asset["exifInfo"]["modifyDate"]).timestamp(),
            }
        else:
            raise Exception(f"Asset with ID {photo_id} not found.")
    

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
