## R2B
This small Python script allows you to plan a route in RideWithGPS (RWGPS) and convert the GPX to a format that can be used to import into Beeline.

Beeline CAN import RWGPS routes directly, but it's annoying if you go off-route because of, say, roadworks - Beeline simply tells you you're off-route and won't re-route you.

This script simply converts an RWGPS route into a series of waypoints, which Beeline can generate a route from, which then acts like you planned it in the (subpar) Beeline route planner.

# Requirements
This script uses the pip `rdp` package. You will need to install this first. If you're on a Mac with Homebrew you can run it in a `venv` to locally install `rdp`.

### Usage
* Plan a route in RWGPS
* Export that route as a "GPS Track" - leave all the options presented as defaults.
* Run the script against that GPX file, for example `./r2b.py test.gpx test_beeline.gpx <epsilon value>`
* The epsilon value defaults to 0.001 if not specified. This may create too many waypoints (which can get annoying) so increase this as required, for example maybe 0.01).
* Import the new GPX created into the Beeline route planner
* Select "Waypoints Only" as the import option
* This will show the waypoints in the planner with straight lines between them
* Choose "Fast", "Fun", or "Relaxed" to route between them. Hopefully one of the routes is similar to the route you planned in RWGPS. Experiment with the epsilon to get the best balance between number of waypoints and route fit.
