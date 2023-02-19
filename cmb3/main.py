import json
from scipy import spatial

import plotly.express as px
import pandas as pd

from config import Filter

with open('country_to_continent.json', 'r') as f:
    continent_map = json.loads(f.read())

with open('all_probes.json', 'r') as f:
    probes = json.loads(f.read())["objects"]

probes = list(filter(lambda p: p["latitude"] != None and p["status_name"] == "Connected", probes))

datacenter_df = pd.read_csv("datacenters.csv")


def find_closest_datacenter_with_condition(dc_condition_key, probe_key, probe, datacenters=datacenter_df):
    country_filtered_df = datacenters[datacenters[dc_condition_key] == probe[probe_key]]
    # datacenter_coords = [country_filtered_df["Latitude"].to_list(), country_filtered_df["Longitude"].to_list()]
    datacenter_coords = [[row["Latitude"], row["Longitude"]] for _, row in country_filtered_df.iterrows()]
    try:
        datacenter_kd_tree = spatial.KDTree(datacenter_coords)
        distance, index = datacenter_kd_tree.query([probe["latitude"], probe["longitude"]])
        found_datacenter = country_filtered_df.iloc[index]
        return found_datacenter
    except:
        # print()
        return None


def find_farthest_datacenter_with_condition(probe, datacenters=datacenter_df):
    max_distance = -1
    current_datacenter = None
    for _, row in datacenters.iterrows():
        current_distance = (row["Latitude"] - probe["latitude"]) ** 2 + (row["Longitude"] - probe["longitude"]) ** 2
        if current_distance > max_distance:
            max_distance = current_distance
            current_datacenter = row

    return current_datacenter


def find_farthest_datacenter(probe, datacenters=datacenter_df):
    max_distance = -1
    current_datacenter = None
    for _, row in datacenters.iterrows():
        current_distance = (row["Latitude"] - probe["latitude"]) ** 2 + (row["Longitude"] - probe["longitude"]) ** 2
        if current_distance > max_distance:
            max_distance = current_distance
            current_datacenter = row

    return current_datacenter


def find_closest_points(points1, points2):
    coordinates = [[x["latitude"], x["longitude"]] for x in points2]
    tree = spatial.KDTree(coordinates)
    all = {}

    for point in points1:
        distance, index = tree.query([point["latitude"], point["longitude"]])
        all[index] = distance

    # all = dict(sorted(all.items(), key=lambda item: item[1]))

    return [points2[index] for index in all]


def put_items(dict_, items, type):
    if type == "home":
        #ödevde istenen olay. kablolu ağlara en yakın wifi probeları bulun demişti
        items = find_closest_points(dict_["wifi"], items)

    for item in items:
        item["type"] = type
    dict_[key] = items


filtered_probes = {}

#4 iteration
for key, value in Filter.filters.items():
    filtered = probes

    #probe'a config.pydan okuduğu filtreleri uygular probeları filtreler
    for fo in value["filters"]:
        filtered = list(filter(lambda p: fo["method"](Filter.make_argument(p[value["input"]]), fo["tags"]), filtered))

    #probeları dict'e yazar
    put_items(filtered_probes, filtered, key)



filtered_values_list = []
for key, value in filtered_probes.items():
    filtered_values_list.extend(value)


#comment out to create world map of probes
"""df = pd.DataFrame(filtered_values_list)
fig = px.scatter_geo(df, lat='latitude', lon='longitude', hover_name="id", color="type")
fig.update_layout(title='World map', title_x=0.5)
fig.show()"""

# datacenter selection per probe


selection = {}

for datacenter, row in datacenter_df.iterrows():
    selection[row["URL"]] = []

for probe_type, value in filtered_probes.items():
    for probe in value:
        probe["continent"] = continent_map[probe["country_code"]]
        datacenters_in_different_country = datacenter_df[datacenter_df["Country"] != probe["country_code"]]
        datacenters_in_same_country = datacenter_df[datacenter_df["Country"] == probe["country_code"]]

        closest_country_dc = find_closest_datacenter_with_condition("Country", "country_code", probe)

        closest_continent_dc = find_closest_datacenter_with_condition("Continent", "continent", probe,
                                                                      datacenters_in_different_country)

        farthest_country_dc = find_farthest_datacenter_with_condition(probe, datacenters_in_same_country)

        farthest_global = find_farthest_datacenter_with_condition(probe)

        if closest_country_dc is not None:
            selection[closest_country_dc["URL"]].append(probe["id"])

        if closest_continent_dc is not None:
            selection[closest_continent_dc["URL"]].append(probe["id"])

        if farthest_country_dc is not None:
            selection[farthest_country_dc["URL"]].append(probe["id"])

        if farthest_global is not None:
            selection[farthest_global["URL"]].append(probe["id"])

with open('selection.json', 'w') as f:
    f.write(json.dumps(selection))
