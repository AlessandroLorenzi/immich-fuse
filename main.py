#!/usr/bin/env python3
import os
import stat
import requests
from fuse import FUSE, Operations


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
            photos.append(photo["deviceAssetId"])
        return photos


class ImmichFuse(Operations):
    def __init__(self, immich_api: ImmichApi):
        self.immich_api = immich_api

    def readdir(self, path, fh):
        return self._parse_path(path)

    def getattr(self, path, fh=None):
        # TODO: if path '/people/<person_name>/<photo_id>' return photo metadata
        return dict(st_mode=(stat.S_IFDIR | 0o755), st_nlink=2)

    def _parse_path(self, path):
        parts = path.lstrip("/").split("/")
        if parts == [""]:
            return self._main_menu()
        elif parts[0] == "by-date":
            return self._get_by_date(parts)
        elif parts[0] == "people":
            return self._get_people(parts)
        elif parts[0] == "albums":
            return self._get_albums(parts)
        else:
            return [".", ".."]

    def _main_menu(self):
        return ["by-date", "people", "albums", ".", ".."]

    def _get_by_date(self, path):
        return [".", ".."]

    def _get_albums(self, path):
        return [".", ".."]

    def _get_people(self, path):
        if len(path) == 1:
            people = self.immich_api.get_people()
            return people + [".", ".."]
        elif len(path) == 2:
            person_name = path[1]
            photos = self.immich_api.get_buckets_by_person(person_name)
            return photos + [".", ".."]
        else:
            person_name = path[1]
            bucket_name = path[2]
            photos = self.immich_api.get_photos_by_person(person_name, bucket_name)
            return photos + [".", ".."]


if __name__ == "__main__":
    import sys

    immich_api = ImmichApi()
    print("Mounting Immich FUSE...")
    mountpoint = sys.argv[1]
    FUSE(ImmichFuse(immich_api), mountpoint, nothreads=True, foreground=True)
