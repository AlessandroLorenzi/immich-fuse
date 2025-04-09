# Immich FUSE

Interact with your Immich server using filesystem.

## Run 

```bash
mkdir mnt
./src/main.py ./mnt
```

## Directry Structure

The design of the directory structure is not stable. May change in the future, eg `YYYY/MM/DD` instead of the monthly bucket list.

### people

Search photos by people

* `ls people` - List all people in your Immich server.
* `ls people/username` - List all montly buckets.
* `ls people/username/YYYY-MM-DDT00:00:00.000Z` - List all photos in bucket.

### by-date

Search photos by date.

* `ls by-date` - List all montly buckets
* `ls by-date/YYYY-MM-DDT00:00:00.000Z` - List all photos in bucket.

### favs

Search favorite photos

* `ls favs` - List all montly buckets
* `ls favs/YYYY-MM-DDT00:00:00.000Z` - List all photos in bucket.
