# Immich FUSE

Interact with your Immich server using filesystem.

## Run 

```bash
mkdir mnt
./main.py ./mnt
```

## Direcotry Structure

### people

Search photos by people

> 👷🏼‍♂️ Work in progress

* `ls people` - List all people in your Immich server.
* `ls people/username` - List all photos of a person in your Immich server.

### by-date

Search photos by date, year, month, and day.

> Not yet implemented

* `ls by-date` - List all years
* `ls by-date/2023` - List all months
* `ls by-date/2023/01` - List all days
* `ls by-date/2023/01/01` - List all photos of a day

### albums

List all albums in your Immich server and photos of an album.

> Not yet implemented

* `ls albums` - List all albums
* `ls albums/album-name` - List all photos of an album
