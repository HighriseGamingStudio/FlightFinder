import json

with open('AirportCodes.json') as json_file:
    old_data = json.load(json_file)

data = {}
for airport in old_data:
    if not old_data[airport]['iata']:
        continue
    else:
        airport_data = old_data[airport]
        iata = airport_data['iata']
        
        if iata in old_data.keys():
            print('[Error] {} already exists in key'.format(iata))
            exit()

        data[iata] = airport_data


with open('op.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)