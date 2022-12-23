import os
import sys
import json
import requests
import argparse
from datetime import datetime, date

#############################################################################

def Usage():
    print("[Info]  Usage:")
    print()
    print("\tStarting Location")
    print("\t\t['-o', '--origin']")
    print("\t\t\t1. IATA Airport Code")
    print()
    print("\tDesired Location | Default: Everywhere")
    print("\t\t['-d', '--destination']")
    print("\t\t\t1. Everywhere")
    print("\t\t\t2. IATA Airport Code")
    print("\t\t\t3. Country Code")
    print()
    print("\tStarting Travel Date | Optional unless '--return-date' is provided")
    print("\t\t['-td', '--travel-date']")
    print()
    print('\tReturning Travel Date | Optional')
    print("\t\t['-rd', '--return-date']")
    print()
    print("[Info]  Examples:")
    print("\t-- JFK to anywhere for any dates --")
    print("\t{} -o JFK -d Everywhere".format(sys.argv[0]))
    print()
    print("\t-- JFK to LAX airport, traveling on 2022-12-23 and returning any date --")
    print("\t{} -o JFK -d LAX -td 2022-12-23".format(sys.argv[0]))
    print()
    print("\t-- JFK to anywhere in Europe, traveling on 2022-12-23 and returning 2022-12-24 --")
    print("\t{} -o JFK -d EU -td 2022-12-23 -rd 2022-12-24".format(sys.argv[0]))
    exit()

#############################################################################

def HandleArguments():
    parser = argparse.ArgumentParser(description='Flight Search Parameters', add_help=False)
    parser.add_argument('-o','--origin') # Required
    parser.add_argument('-d','--destination') # Optional
    parser.add_argument('-td','--travel-date') # Optional unless --return-date is passed
    parser.add_argument('-rd','--return-date') # Optional
    parser.add_argument('-1w','--1-way', action='store_true') # Optional
    parser.add_argument('-h','--help', action='store_true') # Usage
    args = vars(parser.parse_args())
    
    if args['help']:
        Usage()
    elif not args['origin']:
        Usage()
    elif not args['destination']:
        args['destination'] = 'Everywhere'

    error = 0
    if args['destination'].lower() == 'everywhere':
        args['destination'] = 'Everywhere'
        args['country'] = False
    elif args['destination'].lower() == 'anywhere':
        args['destination'] = 'Everywhere'
        args['country'] = False
    elif len(args['destination']) == 2:
        rc = ValidateCountryCode(args['destination'])
        if not rc:
            print("[Error] Country code not found: '--destination {}'".format(args['destination']))
            error += 1
        else:
            args['country'] = True
    elif len(args['destination']) == 3:
        rc = ValidateAirportCode(args['destination'])
        if not rc:
            if args['destination'].lower() == 'any' or args['destination'].lower() == 'all':
                args['destination'] = 'Everywhere'
                args['country'] = False
            else:
                print("[Error] Airport code not found: '--destination {}'".format(args['destination']))
                error += 1
        else:
            args['country'] = False
    else:
        print("[Error] Input Variable misuse: '--destination {}'".format(args['destination']))
        print("\tInput must be ['Everywhere', 'Airport Code', 'Country Code']")
        error += 1

    if args['travel_date']:
        error += ValidateDate("today", args['travel_date'])

    if args['return_date']:
        if not args['travel_date']:
            print("[Error] Paramater '--return-date' requires paramater: '--travel-date'")
            error += 1
        else:
            error += ValidateDate(args['travel_date'],args['return_date'])

    if error > 0:
        print('[Info]  See Usage: {} --help'.format(sys.argv[0]))

    # print(json.dumps(args,indent=2))
    exit()

    return args

#############################################################################

def ValidateDate(start_date, end_date):
    date_format = '%Y-%m-%d'

    if start_date == 'today':
        start_date = datetime.today().strftime(date_format)
    
    try:
        start_date = datetime.strptime(start_date, date_format)
        end_date = datetime.strptime(end_date, date_format)
    except Exception as e:
        print("[Error] Date Format YYYY-MM-DD Required:\n\t{}".format(str(e)))
        return 1

    result = end_date - start_date
    
    if result.days < 0:
        print("[Error] Invalid Date: start_date({}) - end_date({}) = {} days".format(start_date.strftime(date_format), end_date.strftime(date_format), result.days))
        return 1
    
    return 0
#############################################################################

def ValidateCountryCode(cc):
    with open('CountryCodes.json', encoding='utf-8') as f:
        new_data = json.load(f)
        cc_data = new_data['data']

    for country in cc_data:
        if country['countryCode'] == cc:
            return True
        
    return False

#############################################################################

def ValidateAirportCode(ac):
    with open('AirportCodes.json', encoding='utf-8') as f:
        ac_data = json.load(f)

    if ac in ac_data.keys():
        return True
        
    return False

#############################################################################

def RequestFlightInfo(origin, destination, b_country):
    headers = {
    	"X-RapidAPI-Key": "535d57f80amsh5f8e4e6d3163c02p14a247jsnfe8adde18dea",
    	"X-RapidAPI-Host": "skyscanner50.p.rapidapi.com"
    }

    querystring = {
        "origin": origin,
        "currency":"USD",
        "countryCode":"US",
        "market":"en-US"
    }

    if destination != 'Everywhere' and not b_country:
        url = "https://skyscanner50.p.rapidapi.com/api/v1/searchFlights"
        querystring["destination"] = destination
        querystring["adults"] = "1"
        querystring["date"] = "2022-12-29"
        querystring["returnDate"] = "2022-12-29"
        
    elif destination == 'Everywhere':
        url = "https://skyscanner50.p.rapidapi.com/api/v1/searchFlightEverywhere"
        querystring["anytime"] = "true"
        querystring["oneWay"] = "false"
        querystring["travelDate"] = "2022-12-23" # Required when anytime = false
        querystring["returnDate"] = "2022-12-23" # Optional

    elif b_country:
        url = "https://skyscanner50.p.rapidapi.com/api/v1/searchFlightEverywhereDetails"
        querystring["CountryId"] =  destination,
        querystring["anytime"] = "true"
        querystring["oneWay"] = "false"
        querystring["travelDate"] = "2022-12-23" # Required when anytime = false
        querystring["returnDate"] = "2022-12-23" # Optional

    response = requests.request("GET", url, headers=headers, params=querystring)

#############################################################################

## Everywhere in Country
# url = "https://skyscanner50.p.rapidapi.com/api/v1/searchFlightEverywhereDetails"

## Everywhere
# url = "https://skyscanner50.p.rapidapi.com/api/v1/searchFlightEverywhere"

## Everywhere in Country
# querystring = {"origin":"JFK","CountryId":"US","anytime":"true","oneWay":"false","currency":"USD","countryCode":"US","market":"en-US"}

## Everywhere
# querystring = {"origin":"JFK","anytime":"true","oneWay":"false","currency":"USD","countryCode":"US","market":"en-US"}

# headers = {
# 	"X-RapidAPI-Key": "535d57f80amsh5f8e4e6d3163c02p14a247jsnfe8adde18dea",
# 	"X-RapidAPI-Host": "skyscanner50.p.rapidapi.com"
# }

# response = requests.request("GET", url, headers=headers, params=querystring)

#print(response.text)

initial_flight_data = HandleArguments()

with open('JFK_US.json') as f:
    data = json.load(f)

print(json.dumps(data,indent=2))