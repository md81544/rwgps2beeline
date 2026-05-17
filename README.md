## R2B
This small Python script allows you to plan a route in RideWithGPS (RWGPS) and and convert the GPX to a format that can be used to import into Beeline.

This has also been tested successfully with GPX exports from **Komoot**. Please feel free to contact me if you want to try other route planners' output (or let me know if you found it worked with others, and I'll create/update a compatibility list).

Beeline CAN import other route planners'  routes directly, but it's annoying if you go off-route because of, say, roadworks - Beeline simply tells you you're off-route and won't re-route you.

This script simply converts an externally-generated GPX route into a series of waypoints, which Beeline can generate a route from, which then acts like you planned it in the (subpar) Beeline route planner.

### Usage
* Plan a route in RWGPS
* Export that route as a "GPS Track" - leave all the options presented as defaults.
* Run the script against that GPX file, for example `python3 ./r2b.sh test.gpx test_beeline.gpx [--waypoints 10]`
* The number of waypoints generated defaults to **approximately** 10. You can change via the `--waypoints` flag.
* Import the new GPX created into the Beeline route planner
* Select "Waypoints Only" as the import option
* This will show the waypoints in the planner with straight lines between them
* Choose "Fast", "Fun", or "Relaxed" to route between them. Hopefully one of the routes is similar to the route you planned in RWGPS. Experiment with the number of waypoints to generate to get best route fit with your original route.
