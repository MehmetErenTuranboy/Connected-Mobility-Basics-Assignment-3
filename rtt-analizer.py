import json
import random
import matplotlib.pyplot as plt
from cmb3.finder_ import TypeFinder
from cmb3.config import Filter
import pandas as pd
import geopy.distance
from scipy.stats import ttest_ind
from scipy.stats import t
import numpy as np
from scipy.signal import savgol_filter

# Open the JSON file and load the data
with open('RIPE-Atlas-measurement-49989906.json') as f:
    data = json.load(f)

datacenter_url = "us-west.azure.cloudharmony.net"

with open('all_probes.json', 'r') as f:
    probes = json.loads(f.read())["objects"]

datacenters = pd.read_csv("datacenters.csv")
datacenter = datacenters[datacenters["URL"] == datacenter_url]
datacenter_lat = datacenter["Latitude"].to_list()[0]
datacenter_long = datacenter["Longitude"].to_list()[0]

probe_types = {}
probe_types_average_distance = {}

for probe_ in data:
    prb_id = probe_["prb_id"]
    if prb_id not in probe_types:
        probe_type = TypeFinder.find_probe_type(probes, prb_id)
        probe_types[prb_id] = probe_type
        found_probe_from_all_probes = TypeFinder.find_probe_by_id(probes, prb_id)
        probe_types_average_distance[prb_id] = geopy.distance.geodesic((datacenter_lat, datacenter_long), (
            found_probe_from_all_probes["latitude"], found_probe_from_all_probes["longitude"])).km

# Shuffle the data and select 200 random samples
# random.seed(42)
# random.shuffle(data)
data = data[:2000]

# Extract the timestamp values
timestamps = [obj['timestamp'] for obj in data]

# Traverse through the data to get the RTT values and probe types
rtt_values = []
probe_types_list = []
counter = 0
rtt_dict = {}
rtt_dict_x = {}
for obj in data:
    prb_id = obj["prb_id"]
    # rtt_values.extend()
    probe_type = probe_types[prb_id]
    # probe_types_list.extend())

    if prb_id in rtt_dict:
        rtt_dict[prb_id].extend([result.get("rtt", 0) for result in obj["result"]])
    else:
        rtt_dict[prb_id] = []

    if prb_id in rtt_dict_x:
        rtt_dict_x[prb_id].extend([obj["timestamp"]] * len(obj["result"]))
    else:
        rtt_dict_x[prb_id] = []
# Create a dictionary to store RTT values for each probe type
"""rtt_dict = {}"""
"""for probe_type in probe_types:
    rtt_dict[probe_type] = [rtt_values[i] for i in range(len(probe_types_list)) if probe_types_list[i] == probe_type]"""

# Create a plot of the RTT values for each probe type
colors = {'cellular': 'r', 'wifi': 'g', 'starlink': 'b', 'home': 'c'}
for key, value in rtt_dict_x.items():
    min__ = min(value)
    rtt_dict_x[key] = [d - min__ for d in value]
for probe_id, value in probe_types.items():
    if probe_id in rtt_dict:
        # y = gaussian_filter1d(rtt_dict[probe_id], sigma=5)
        window = 49
        order = 1
        y_sf = savgol_filter(rtt_dict[probe_id], window, order)

        plt.plot(rtt_dict_x[probe_id], y_sf, color=np.random.rand(3, ),
                 label=f"{probe_types[probe_id]}-{int(probe_types_average_distance[probe_id])}")
smallest = 10000000
for rtts, value in rtt_dict_x.items():
    if len(value) < smallest:
        smallest = len(value)

test_dict = {}
tested_or_not = {}
for probe_id1, value1 in rtt_dict.items():
    for probe_id2, value2 in rtt_dict.items():
        if probe_id1 == probe_id2 or f"{probe_id1}-{probe_id2}" in tested_or_not or f"{probe_id2}-{probe_id1}" in tested_or_not:
            continue
        t_stat, p = ttest_ind(value1[:smallest], value2[:smallest])
        print(f't={t_stat}, p={p}, pairs={probe_types[probe_id1]}-{probe_types[probe_id2]}, '
              f'distances={int(probe_types_average_distance[probe_id1])}-{int(probe_types_average_distance[probe_id2])} km')
        tested_or_not[f"{probe_id1}-{probe_id2}"] = ""

plt.xlabel("Seconds")
plt.ylabel("RTT (ms)")
plt.title(f"RTT Values from RIPE Atlas Measurement for {datacenter_url} ")
# plt.xticks(range(len(timestamps)), timestamps, rotation=90)
plt.legend()
plt.show()


class TypeFinder:
    @staticmethod
    def find_probe_type(probe_id):
        with open('all_probes.json', 'r') as f:
            probes = json.loads(f.read())["objects"]
        probe = list(filter(lambda p: p["id"] == probe_id, probes))[0]
        for key, value in Filter.filters.items():
            for fo in value["filters"]:
                filtered = list(
                    filter(lambda p: fo["method"](Filter.make_argument(p[value["input"]]), fo["tags"]), [probe]))
                if len(filtered) >= 1:
                    return key
