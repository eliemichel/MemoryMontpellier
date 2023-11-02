"""
This script is a bit messy, because it handles data that is a bit messy itself.
"""

from pathlib import Path
import json
from dataclasses import dataclass, field
from typing import List, Dict
from collections import defaultdict
from urllib.request import urlretrieve

#---------------------------------------------

def main():
    traces = loadData("MMM_MMM_LigneTram.json")
    stations = loadData("MMM_MMM_ArretsTram.json")
    #communes = loadData("base-comparateur-de-territoires.geojson")

    stations_with_ids = populateStationIds(stations)

    metadata = generateMetadata(stations_with_ids, traces)
    exportData(metadata, "memory-pour-mtpl-metadata.json")

    new_stations = generateNewStations(stations_with_ids, metadata)
    exportData(new_stations, "memory-pour-mtpl-stations.geojson")

    new_traces = generateNewTraces(traces, metadata)
    exportData(new_traces, "memory-pour-mtpl-trainline-traces.geojson")

    new_communes = { "type": "FeatureCollection", "features": [] }#generateCommunes(communes)
    exportData(new_communes, "memory-pour-mtpl-communes.geojson")


#---------------------------------------------

DATA_ROOT = Path(__file__).parent.parent.joinpath("data")

def loadData(filename):
    with open(DATA_ROOT.joinpath("raw", filename), encoding="utf-8") as f:
        return json.load(f)

def exportData(data, filename):
    with open(DATA_ROOT.joinpath(filename), "w", encoding="utf-8") as f:
        return json.dump(data, f)

#---------------------------------------------

def generateMetadata(stations_with_ids, traces):
    station_count_per_line = defaultdict(int)
    connected_stations = defaultdict(list)
    for station in stations_with_ids['features']:
        props = station['properties']
        for trainline in props["lignes_passantes"].split(";"):
            trainline = int(trainline.strip())
        station_count_per_line[trainline] += 1
        connected_stations[props["description"]].append(props["id"])

    ordered_trainlines = [
        1,
        2,
        3,
        4,
    ]

    trainline_logo_style = {
        1: { "text-color": "#ffffff", "shape": "tram" },
        2: { "text-color": "#ffffff", "shape": "tram" },
        3: { "text-color": "#373a4f", "shape": "tram" },
        4: { "text-color": "#ffffff", "shape": "tram" },
    }

    trainline_color = {}
    for feature in traces['features']:
        props = feature['properties']
        trainline = props["num_exploitation"]
        trainline_color[trainline] = props["code_couleur"]

    #total_inhabitants = 0
    #total_surface = 0
    #for feature in new_communes["features"]:
    #    props = feature["properties"]
    #    total_inhabitants += props["population"]
    #    total_surface += props["superficie"]
    #print(f"Nombre total d'habitants: {total_inhabitants}")
    #print(f"Supercifie total (en km2): {total_surface}")

    return {
        "primary-station": {
            id: connected_ids[0]
            for connected_ids in connected_stations.values()
            if len(connected_ids) > 1
            for id in connected_ids
        },
        "secondary-stations": {
            connected_ids[0]: connected_ids[1:]
            for connected_ids in connected_stations.values()
            if len(connected_ids) > 1
        },
        "trainlines": {
            trainline: {
                "station-count": station_count_per_line[trainline],
                "logo": f"{trainline}.svg",
                "logo-style": trainline_logo_style[trainline],
                "color": trainline_color[trainline],
            }
            for trainline in ordered_trainlines
        },
        "ordered-trainlines": ordered_trainlines,
        "communes": {
            "total-communes": 1,#len(new_communes["features"]),
            "total-inhabitants": 1,#total_inhabitants,
            "total-surface": 1,#total_surface,
        },
    }

#---------------------------------------------

def filterGeojsonProperties(geojson, filterProperties):
    return {
        "type": geojson["type"],
        "features": [
            {
                "type": entry["type"],
                "geometry": entry["geometry"],
                "properties": new_props,
            }
            for entry in geojson["features"]
            for new_props in filterProperties(entry["properties"].copy())
        ],
    }

#---------------------------------------------

def populateStationIds(stations):
    next_id = 0
    for ft in stations["features"]:
        props = ft["properties"]
        props["id"] = next_id
        next_id += 1
    return stations

#---------------------------------------------

def generateNewStations(stations, metadata):
    def filterProperties(props):
        props["trainlines"] = [
            int(trainline.strip())
            for trainline in props["lignes_passantes"].split(";")
        ]
        first_trainline = props["trainlines"][0]
        props["color"] = metadata["trainlines"][first_trainline]["color"]
        return [props]

    return filterGeojsonProperties(stations, filterProperties)

#---------------------------------------------

def generateNewTraces(traces, metadata):
    def filterProperties(props):
        if props["num_exploitation"] == 1:
            props["line-offset"] = 1
        if props["num_exploitation"] == 4:
            props["line-offset"] = -1
        return [props]

    return filterGeojsonProperties(traces, filterProperties)

#---------------------------------------------

def generateCommunes(communes):
    def filterProperties(props):
        return [{
            "nom": props["libgeo"],
            "code": props["codgeo"],
            "population": props["p20_pop"],
            "superficie": props["superf"], # en km2
            "center": json.loads(props["geo_point"]) if type(props["geo_point"]) == str else props["geo_point"],
        }]

    return filterGeojsonProperties(communes, filterProperties)

#---------------------------------------------

if __name__ == '__main__':
    main()
