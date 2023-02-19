#this is used for managing the filters dynamically

class Filter:

    def any_(list, expected):
        result = any(tag in expected for tag in list)
        return result

    def not_any(list, expected):
        return not Filter.any_(list, expected)

    def all_(list, expected):
        return all(tag in expected for tag in list)

    def make_argument(i):
        if not isinstance(i, list):
            return [i]

        return i

    filters = {
        "cellular": {
            "input": "tags",
            "filters": [
                {
                    "method": any_,
                    "tags": ['4g', '5g', 'lte', '3g']
                }
            ]
        },
        "wifi": {
            "input": "tags",
            "filters": [
                {
                    "method": any_,
                    "tags": ['wi-fi', 'wireless-isp', 'fixed-wifi', 'system-wifi']
                }
            ]
        },
        "starlink": {
            "input": "asn_v4",
            "filters": [
                {
                    "method": any_,
                    "tags": [14593]
                },
            ]
        },
        "home": {
            "input": "tags",
            "filters": [
                {
                    "method": any_,
                    "tags": ['home']
                },
                {
                    "method": any_,
                    "tags": ['fibre', 'ftth', 'cable', 'dsl']
                },
                {
                    "method": not_any,
                    "tags": ['cellular', 'wi-fi', 'wifi', 'satellite']
                }
            ]
        }
    }


