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

NS = "http://www.topografix.com/GPX/1/1"
DEFAULT_WAYPOINTS = 30
ET.register_namespace("", NS)

def perpendicular_distance(point, line_start, line_end):
    """Distance from point to a line defined by two points."""
    x0, y0 = point
    x1, y1 = line_start
    x2, y2 = line_end

    dx, dy = x2 - x1, y2 - y1

    # If the line is actually a point, return simple distance
    if dx == 0 and dy == 0:
        return ((x0 - x1) ** 2 + (y0 - y1) ** 2) ** 0.5

    return abs(dy * x0 - dx * y0 + x2 * y1 - y2 * x1) / (dx ** 2 + dy ** 2) ** 0.5

def rdp(points, epsilon):
    """Ramer-Douglas-Peucker polyline simplification."""
    if len(points) < 3:
        return points

    # Find the point with the maximum distance from the line start->end
    max_dist = 0.0
    max_idx = 0
    for i in range(1, len(points) - 1):
        dist = perpendicular_distance(points[i], points[0], points[-1])
        if dist > max_dist:
            max_dist = dist
            max_idx = i

    if max_dist > epsilon:
        # Significant point found — recurse on each half
        left  = rdp(points[:max_idx + 1], epsilon)
        right = rdp(points[max_idx:], epsilon)
        # Avoid duplicating the split point
        return left[:-1] + right
    else:
        # No significant points — discard everything in between
        return [points[0], points[-1]]

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
    parser.add_argument("-w", "--waypoints", type=positive_int, default=DEFAULT_WAYPOINTS,
                    metavar="N", help=f"Target number of waypoints (default: {DEFAULT_WAYPOINTS})")
    args = parser.parse_args()

    convert(args.input, args.output, args.waypoints)
