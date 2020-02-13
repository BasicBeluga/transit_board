# transit-board
_arrivals-style board for your terminal_

usage: 
`python3 transit_board -t <transit system> -s <stop_id>`

On first time setup, or when route data gets stale, 
add the argument `-u` to download & update static route files.

You can find the json route resource definitions in the `route_links` directory

#### Transit Systems
* `bart` - San Francisco Bart (Hardcoded, no updates)
* `halifax_ns` - Halifax Transit (Uses new update system)

![](https://raw.githubusercontent.com/BasicBeluga/transit-board/master/example.jpg?token=AAHQJNEU3CTTV6LU5ALQAC25Q2NJO)

# TODO
* ~~Make auto updating happen~~ done december 1st 2019
* Add better menus with more ways to see the data (where is my vehicle currently)
* Support for static transit feeds in the live view
* Check out issues for more stuff I need to do
