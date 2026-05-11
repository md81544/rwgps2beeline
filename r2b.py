#!/usr/bin/env python3
# rwgps_to_beeline.py
# Converts a RideWithGPS GPX track to a Beeline-compatible waypoint-only GPX
# using the Ramer-Douglas-Peucker algorithm to thin the track to turn points.
#
# Usage: r2b.py input.gpx output.gpx [--waypoints N]
# Waypoints default to DEFAULT_WAYPOINTS (defined below)

import sys
import argparse
import xml.etree.ElementTree as ET
from rdp import rdp

NS = "http://www.topografix.com/GPX/1/1"
DEFAULT_WAYPOINTS = 10
ET.register_namespace("", NS)

def tag(name):
    return f"{{{NS}}}{name}"

def find_epsilon(points, target, tolerance=1):
    """Binary search for epsilon that produces approximately target waypoints."""
    lo, hi = 0.0, 1.0

    # Expand hi until we get few enough points
    while len(rdp(points, epsilon=hi)) > target:
        hi *= 2

    for _ in range(50):  # max binary search iterations; convergence typically happens in ~15
        mid = (lo + hi) / 2
        count = len(rdp(points, epsilon=mid))
        if abs(count - target) <= tolerance:
            return mid
        if count > target:
            lo = mid
        else:
            hi = mid

    return (lo + hi) / 2

def convert(input_path, output_path, target_waypoints):
    tree = ET.parse(input_path)
    root = tree.getroot()

    points = []
    for trk in root.findall(tag("trk")):
        for trkseg in trk.findall(tag("trkseg")):
            for trkpt in trkseg.findall(tag("trkpt")):
                lat = float(trkpt.get("lat"))
                lon = float(trkpt.get("lon"))
                points.append((lon, lat))

    if not points:
        print("No track points found — ensure input is a RideWithGPS GPX track export")
        sys.exit(1)

    print(f"Input:  {len(points)} track points")

    if target_waypoints >= len(points):
        print(f"Warning: requested {target_waypoints} waypoints but input only has {len(points)} points — using all")
        simplified = points
    else:
        epsilon = find_epsilon(points, target_waypoints)
        simplified = rdp(points, epsilon=epsilon)
        print(f"Output: {len(simplified)} waypoints (converged on epsilon={epsilon:.6f})")

    new_root = ET.Element("gpx")
    new_root.set("xmlns", NS)
    new_root.set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
    new_root.set("xsi:schemaLocation",
        "http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd")
    new_root.set("version", "1.1")
    new_root.set("creator", "Beeline")

    for lon, lat in simplified:
        wpt = ET.SubElement(new_root, "wpt")
        wpt.set("lat", f"{lat:.10f}")
        wpt.set("lon", f"{lon:.10f}")

    ET.indent(new_root, space="  ")
    new_tree = ET.ElementTree(new_root)
    with open(output_path, "wb") as f:
        f.write(b'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n')
        new_tree.write(f, encoding="utf-8", xml_declaration=False)

    print(f"Written to {output_path}")

def positive_int(value):
    n = int(value)
    if n <= 0:
        raise argparse.ArgumentTypeError(f"waypoints must be a positive integer, got {n}")
    return n

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Convert a RideWithGPS GPX track to a Beeline-compatible waypoint GPX")
    parser.add_argument("input",  help="Input GPX file (RideWithGPS track export)")
    parser.add_argument("output", help="Output GPX file (Beeline-compatible)")
    parser.add_argument("--waypoints", type=positive_int, default=DEFAULT_WAYPOINTS,
                    metavar="N", help=f"Target number of waypoints (default: {DEFAULT_WAYPOINTS})")
    args = parser.parse_args()

    convert(args.input, args.output, args.waypoints)