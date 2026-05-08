#!/usr/bin/env python3
# rwgps_to_beeline.py
# Converts a RideWithGPS GPX track to a Beeline-compatible waypoint-only GPX
# using the Ramer-Douglas-Peucker algorithm to thin the track to turn points.
#
# Usage: python3 rwgps_to_beeline.py input.gpx output.gpx [epsilon]
# epsilon is in degrees, default 0.001 (~100m). Increase to get fewer points.
#
# Requires pip package rdp

import sys
import xml.etree.ElementTree as ET
from rdp import rdp

NS = "http://www.topografix.com/GPX/1/1"
ET.register_namespace("", NS)

def tag(name):
    return f"{{{NS}}}{name}"

def convert(input_path, output_path, epsilon):
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

    simplified = rdp(points, epsilon=epsilon)
    print(f"Output: {len(simplified)} waypoints (epsilon={epsilon})")

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

if __name__ == "__main__":
    if len(sys.argv) not in (3, 4):
        print(f"Usage: {sys.argv[0]} input.gpx output.gpx [epsilon]")
        print( "       epsilon in degrees, default 0.001 (~100m). Increase for fewer waypoints.")
        sys.exit(1)

    epsilon = abs(float(sys.argv[3]) if len(sys.argv) == 4 else 0.001)
    convert(sys.argv[1], sys.argv[2], epsilon)
