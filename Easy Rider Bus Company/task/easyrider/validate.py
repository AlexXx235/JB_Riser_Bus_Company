import re
import json

bus_ids = [128, 256, 512]
stop_name_suffixes = [
    'Road',
    'Avenue',
    'Boulevard',
    'Street'
]
stop_name_pattern = r'^[A-Z].*(Avenue|Boulevard|Street|Road)$'
stop_type_pattern = r'[SFO]?$'
time_pattern = r'[0-2]\d:[0-5]\d$'


def simple_validate_stop_name(stop_name):
    if type(stop_name) is not str:
        return False
    elif stop_name.strip() == '':
        return False
    return True


def format_validate_data(json_data):
    data = json.loads(json_data)
    error_keys = [
        'stop_name',
        'stop_type',
        'a_time'
    ]
    errors = dict.fromkeys(error_keys, 0)
    for obj in data:
        if re.match(stop_name_pattern, obj['stop_name']) is None:
            errors['stop_name'] += 1
        if re.match(stop_type_pattern, obj['stop_type']) is None:
            # print(obj['stop_type'])
            errors['stop_type'] += 1
        if re.match(time_pattern, obj['a_time']) is None:
            # print(obj['a_time'])
            errors['a_time'] += 1
    print(f'Format validation: {sum(errors.values())} errors')
    for error in error_keys:
        print(f'{error}: {errors[error]}')


def validate_json_data(json_data):
    data = json.loads(json_data)
    errors_keys = [
        'bus_id',
        'stop_id',
        'stop_name',
        'next_stop',
        'stop_type',
        'a_time'
    ]
    errors = dict.fromkeys(errors_keys, 0)
    for obj in data:
        if type(obj['bus_id']) is not int:
            errors['bus_id'] += 1
        if type(obj['stop_id']) is not int:
            errors['stop_id'] += 1
        if simple_validate_stop_name(obj['stop_name']) is False:
            errors['stop_name'] += 1
        if type(obj['next_stop']) is not int:
            errors['next_stop'] += 1
        if re.match(stop_type_pattern, obj['stop_type']) is None:
            errors['stop_type'] += 1
        if type(obj['a_time']) is not str:
            errors['a_time'] += 1
        elif re.match(time_pattern, obj['a_time']) is None:
            errors['a_time'] += 1
    print(f'Total and required field validation: {sum(errors.values())} errors')
    for error in errors_keys:
        print(error + ': ' + str(errors[error]))


def validate_lines_connections(json_data):
    data = json.loads(json_data)
    start_stops = set()
    stops = set()
    transfer_stops = set()
    finish_stops = set()
    bus_lines = {}
    for bus_stop in data:
        bus_id = bus_stop['bus_id']
        stop_name = bus_stop['stop_name']
        stop_type = bus_stop['stop_type']
        if stop_type != 'O':
            if stop_name in stops:
                transfer_stops.add(stop_name)
            else:
                stops.add(stop_name)
        if bus_id not in bus_lines:
            bus_lines[bus_id] = {'start': None, 'stop': None}
        if stop_type == 'S' and bus_lines[bus_id]['start'] is None:
            bus_lines[bus_id]['start'] = stop_name
            start_stops.add(stop_name)
        if stop_type == 'F' and bus_lines[bus_id]['stop'] is None:
            bus_lines[bus_id]['stop'] = stop_name
            finish_stops.add(stop_name)
    for line in bus_lines.keys():
        if bus_lines[line]['start'] is None or bus_lines[line]['stop'] is None:
            print(f'There is no start or end stop for the line: {line}.')
            return
    print(f'Start stops: {len(start_stops)} {sorted(list(start_stops))}')
    print(f'Transfer stops: {len(transfer_stops)} {sorted(list(transfer_stops))}')
    print(f'Finish stops: {len(finish_stops)} {sorted(list(finish_stops))}')


def a_times_are_not_correct(prev, curr):
    prev_h, prev_m = map(int, prev.split(':'))
    curr_h, curr_m = map(int, curr.split(':'))
    if curr_h < prev_h:
        return True
    elif curr_h == prev_h:
        if prev_m >= curr_m:
            return True
    return False


def validate_arriving_time(json_data):
    data = json.loads(json_data)
    current_line = data[0]['bus_id']
    prev_time = '00:00'
    correct = True
    incorrect_line = False
    print('Arrival time test:')
    for stop in data:
        curr_time = stop['a_time']
        if stop['bus_id'] != current_line:
            current_line = stop['bus_id']
            incorrect_line = False
            prev_time = '00:00'
        if incorrect_line:
            continue
        elif a_times_are_not_correct(prev_time, curr_time):
            correct = False
            incorrect_line = True
            print(f"bus_id line {stop['bus_id']}: "
                  f"wrong time on Station {stop['stop_name']}")
            continue
        prev_time = curr_time
    if correct:
        print('OK')


def validate_on_demand(json_data):
    data = json.loads(json_data)
    on_demand_stops = set()
    other_stops = set()
    for stop in data:
        if stop['stop_type'] == 'O':
            on_demand_stops.add(stop['stop_name'])
        else:
            other_stops.add(stop['stop_name'])
    print('On demand stops test:')
    result = on_demand_stops & other_stops
    if len(result) == 0:
        print('OK')
    else:
        print(f'Wrong stop type: {sorted(list(result))}')


