# Aggregator

Mini website for pulling device list from a narrowed selection of network switches (`Netgear M4100`, `Netgear GS752TS` (stacked)).

The utility collects:

* device MACs

* port ID and description

The aggregated list shows the discovered devices along with port information from each switch so it can help indentify at which port to start debugging.

## Using

Self-contained `bottle.py` module is needed to run this utility. Download from http://bottlepy.org/ and place it in the src/ dir.

You need to supply valid device URL and login credentials in the respective `src/<device>/fetch.py` files. Edit the `base_url` and `*_switch_access` variables (`uname` and/or `pwd` fields) to provide the required infos.

The frontend is protected with HTTP basic auth. Set the appropiate username and password in `main.py`.

## Bugs

The switch adapter is a BeautifulSoup implementation, which tends to break after a while on `GS752TS` (stacked), but not the other switch(es). Possible solution is A) a new, SSH-based adapter or B) implement logout-login cycle on-the-fly.
