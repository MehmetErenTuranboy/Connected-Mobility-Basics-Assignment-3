import json
from cmb3.config import Filter


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
    @staticmethod
    def find_probe_type(probes, probe_id):

        probe = list(filter(lambda p: p["id"] == probe_id, probes))[0]
        for key, value in Filter.filters.items():
            for fo in value["filters"]:
                filtered = list(
                    filter(lambda p: fo["method"](Filter.make_argument(p[value["input"]]), fo["tags"]), [probe]))
                if len(filtered) >= 1:
                    return key

    @staticmethod
    def find_probe_by_id(probes, probe_id):
        for probe in probes:
            if probe["id"] == probe_id:
                return probe
