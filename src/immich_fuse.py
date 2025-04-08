import stat
from fuse import Operations
import re
from immich_api import ImmichApi


class ImmichFuse(Operations):
    def __init__(self, immich_api: ImmichApi):
        self.immich_api = immich_api

    def readdir(self, path, fh):
        return self._parse_path(path)

    def getattr(self, path, fh=None):
        # if path '/people/<person_name>/<bucket>/<photo_name>' return photo metadata
        match = re.match(r"^/people/([^/]+)/([^/]+)/([0-9abcdef-]+)_([^/]+)$", path)
        if match:
            _, _, photo_id, _ = match.groups()
            asset_stats = self.immich_api.get_asset_stats(photo_id)
            return self._asset_stats_to_file_info(asset_stats)
            # return dict(st_mode=(stat.S_IFREG | 0o644), st_nlink=1)
        return dict(st_mode=(stat.S_IFDIR | 0o755), st_nlink=2)

    def _asset_stats_to_file_info(self, asset_stats):
        return dict(
            st_mode=(stat.S_IFREG | 0o644),
            st_nlink=1,
            st_size=asset_stats["file_size_in_byte"],
            st_ctime=asset_stats["date_time_original"],
            st_mtime=asset_stats["modifify_date"],
            st_atime=asset_stats["modifify_date"],
        )

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
