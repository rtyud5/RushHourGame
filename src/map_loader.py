import json
from utils import Vehicle

# Hàm load_map đọc JSON trả về dict id->Vehicle
# JSON format:
# { "vehicles": [ {id, orientation, row, col, length}, ... ] }
def load_map(path):
    data = json.load(open(path))
    vehicles = {}
    for v in data['vehicles']:
        vehicles[v['id']] = Vehicle(
            v['id'], v['orientation'], v['row'], v['col'], v['length'])
    return vehicles