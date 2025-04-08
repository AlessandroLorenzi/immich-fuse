import stat
from fuse import Operations
import re
from immich_api import ImmichApi


class ImmichFuse(Operations):
    def __init__(self, immich_api: ImmichApi):
        self.immich_api = immich_api
        self.assets = {}

    def readdir(self, path, fh):
        return self._parse_path(path)

    def getattr(self, path, fh=None):
        asset_id = self._path_to_asset_id(path)
        if asset_id is None:
            return dict(st_mode=(stat.S_IFDIR | 0o755), st_nlink=2)

        asset_stats = self.immich_api.get_asset_stats(asset_id)
        return self._asset_stats_to_file_info(asset_stats)

    def open(self, path, flags):
        """
        Open the file and return the file handle.
        """
        # if path != TODO:
        #     raise FileNotFoundError()
        return 0

    def read(self, path, size, offset, fh):
        """
        Read the file and return the data.
        """
        asset_id = self._path_to_asset_id(path)

        if offset == 0:
            self.assets[asset_id] = self.immich_api.get_asset(asset_id)

        chunk = self.assets[asset_id][offset : offset + size]

        # Clean up the asset if the offset is at the end of the file
        file_size = len(self.assets[asset_id])
        if offset + size >= file_size:
            del self.assets[asset_id]

        return chunk

    def _asset_stats_to_file_info(self, asset_stats):
        """
        Convert asset stats to file information.
        """
        return dict(
            st_mode=(stat.S_IFREG | 0o644),
            st_nlink=1,
            st_size=asset_stats["file_size_in_byte"],
            st_ctime=asset_stats["date_time_original"],
            st_mtime=asset_stats["modifify_date"],
            st_atime=asset_stats["modifify_date"],
        )

    def _parse_path(self, path):
        """
        Parse the path and return the appropriate directory listing.
        """
        parts = path.lstrip("/").split("/")
        if parts == [""]:
            return self._main_menu()
        elif parts[0] == "by-date":
            return self._get_by_date(parts)
        elif parts[0] == "people":
            return self._get_people(parts)
        elif parts[0] == "favs":
            return self._get_favs(parts)
        else:
            return [".", ".."]

    def _main_menu(self):
        """
        Directories in main directory, sort of main menu of the Immich FUSE filesystem.
        """
        return ["by-date", "people", "favs", ".", ".."]

    def _get_by_date(self, path):
        """
        Manage the by-date directory, fetch buckets and assets.
        """
        if len(path) == 1:
            assets = self.immich_api.get_buckets()
            return assets + [".", ".."]
        elif len(path) == 2:
            bucket_name = path[1]
            assets = self.immich_api.get_assets(bucket_name)
            return assets + [".", ".."]

    def _get_favs(self, path):
        """
        Manage the favs directory, fetch buckets and assets.
        """
        if len(path) == 1:
            assets = self.immich_api.get_buckets(favs="true")
            return assets + [".", ".."]
        elif len(path) == 2:
            bucket_name = path[1]
            assets = self.immich_api.get_assets(bucket_name, favs="true")
            return assets + [".", ".."]

    def _get_people(self, path):
        """
        Manage the `people` directory, fetch people list, their buckets and assets.
        """
        if len(path) == 1:
            people = self.immich_api.get_people()
            return people + [".", ".."]
        elif len(path) == 2:
            person_name = path[1]
            assets = self.immich_api.get_buckets(person_name=person_name)
            return assets + [".", ".."]
        elif len(path) == 3:
            person_name = path[1]
            bucket_name = path[2]
            assets = self.immich_api.get_assets(
                person_name=person_name, bucket_name=bucket_name
            )
            return assets + [".", ".."]
        raise FileNotFoundError()

    def _path_to_asset_id(self, path) -> str:
        """
        Match the asset id from the file path.
        """
        match = re.match(r"^/people/([^/]+)/([^/]+)/([0-9abcdef-]+)_([^/]+)$", path)
        if match:
            _, _, asset_id, _ = match.groups()
            return asset_id

        match = re.match(r"^/by-date/([^/]+)/([0-9abcdef-]+)_([^/]+)$", path)
        if match:
            _, asset_id, _ = match.groups()
            return asset_id

        match = re.match(r"^/favs/([^/]+)/([0-9abcdef-]+)_([^/]+)$", path)
        if match:
            _, asset_id, _ = match.groups()
            return asset_id

        return None
