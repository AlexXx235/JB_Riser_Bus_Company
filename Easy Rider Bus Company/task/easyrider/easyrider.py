import json
from validate import *


def count_stops(json_data):
    data = json.loads(json_data)
    lines_dict = dict()
    for stop in data:
        bus_id = stop['bus_id']
        if bus_id in lines_dict:
            lines_dict[bus_id] += 1
        else:
            lines_dict[bus_id] = 1
    for line in lines_dict.keys():
        print(f'bus_id: {line}, stops: {lines_dict[line]}')


if __name__ == '__main__':
    json_data = input()
    validate_on_demand(json_data)