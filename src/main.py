#!/usr/bin/env python3
from fuse import FUSE

from immich_api import ImmichApi
from immich_fuse import ImmichFuse
import sys


if __name__ == "__main__":
    immich_api = ImmichApi()
    print("Mounting Immich FUSE...")
    mountpoint = sys.argv[1]
    FUSE(ImmichFuse(immich_api), mountpoint, nothreads=True, foreground=True)
