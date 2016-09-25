from urllib import urlencode
from urllib2 import urlopen, HTTPError
from datetime import date
import json

airport_codes = json.loads(open('final_codes.json').read())

def lambda_handler(event, context):
    try:
        intentType = str(event['request']['type'])
        if intentType == 'LaunchRequest':
            return deltaHelp()
        intentName = str(event['request']['intent']['name'])
        if intentName == 'getFlights':
            return getFlights(event, context)
        elif intentName == 'getFlightStatus':
            return getFlightStatus(event, context)
        elif intentName == 'getTSAWaitTimes':
            return getTSAWaitTimes(event, context)
        elif intentName == 'deltaHelp':
            return deltaHelp()
    except Exception as e:
        print e
        return construct_response('Sorry, there was an error. Please try again!')

def getAirportCode(city):
    return airport_codes[city.title()] if len(city) > 3 else city

def getFlights(event, context):
    depDate = event['request']['intent']['slots']['DepartureDate']['value']
    retDate = None#\
        # event['request']['intent']['slots']['ReturnDate'] or None
    origin = getAirportCode(event['request']['intent']['slots']['Origin']['value'])
    dest = getAirportCode(event['request']['intent']['slots']['Destination']['value'])

    data = {
        'apikey': 'zCQj3XGAs1q2tQ3RKGdk3XLJ4dQqp2NF',
        'retDate': retDate,
        'depDate': depDate,
        'origin': origin,
        'dest': dest
    }

    url = ('https://demo30-test.apigee.net/v1/hack/search/flight' +
           '?origin={origin}' +
           '&destination={dest}' +
           '&departDate={depDate}' +
           ('&returnDate={retDate}' if retDate else "") +
           '&apikey={apikey}').format(**data)

    # print url
    r = urlopen(url)
    result = json.load(r)
    if 'itineraries' not in result:
        raise Exception("Query failed " + url)

    itineraries = result['itineraries'][:5]

    out = ("There are flights available from {origin} to {dest}" +
           " on {depDate}.").format(
            origin=result['origin']['name'],
            dest=result['destination']['name'],
            depDate=depDate
            )

    for it in itineraries:
        stops = it['slice']['stops']
        stops = str(stops) if stops != '0' else "non"

        fare = str(it['bestFare']['fareValue'])

        flights = it['slice']['flights']

        departTime = flights[0]['departTime']
        arrivalTime = flights[-1]['arriveTime']
        day = ("" if flights[0]['departDate'] == flights[-1]['arriveDate']
               else (" on " + str(flights[-1]['arriveDate'])))

        duration = it['slice']['duration']

        message = ("For {fare} dollars, there is a {stops} stop flight " +
                   "leaving at {depTime} local time and reaching at " +
                   "{arrTime} local time{day}. Total travel time is " +
                   "{duration}."
                   ).format(
                    fare=fare,
                    stops=stops,
                    depTime=departTime,
                    arrTime=arrivalTime,
                    day=day,
                    duration=duration
                   )

        out += (" " + message)
    out += " For more information please visit www.delta.com."
    return construct_response(out)
    
def getFlightStatus(event, context):
    flightId = str(event['request']['intent']['slots']['FlightID']['value'])
    flightDate = str(event['request']['intent']['slots']['FlightDate']['value'])
   
    data = {
        'apikey' : 'zCQj3XGAs1q2tQ3RKGdk3XLJ4dQqp2NF',
        'flightNumber' : flightId,
        'flightDate' : flightDate
        }
    url = 'https://demo30-test.apigee.net/v1/hack/status?flightNumber={flightNumber}&flightOriginDate={flightDate}&apikey={apikey}'.format(**data)

    res = urlopen(url)
    jsonOutput = json.load(res)

    response = ""
    try:
        connectingFlights = jsonOutput['flightStatusResponse']['statusResponse']['flightStatusTO']['flightStatusLegTOList']
        connectingFlights = connectingFlights if isinstance(connectingFlights, list) else [connectingFlights]
        
        for flight in connectingFlights:
            response += "Your flight from " + flight['departureCityName'] + " to " + flight['arrivalCityName'] + " is " + flight['arrivalLocalTimeEstimatedActualString'] + ". "
    except:
        errorMessage = jsonOutput['flightStatusResponse']['errorMessage']
        response += errorMessage.replace('us', 'them')
    
    return construct_response(response)
    
def getTSAWaitTimes(event, context):
    airport = str(event['request']['intent']['slots']['Airport']['value'])
    data = {
        'apikey' : 'zCQj3XGAs1q2tQ3RKGdk3XLJ4dQqp2NF',
        'airport' : airport
        }
    url = 'https://demo30-test.apigee.net/v1/hack/tsa?airport={airport}&apikey={apikey}'.format(**data)

    try:
        r = urlopen(url)
    except HTTPError as err:
        if err.code == 400:
            return construct_response('Sorry, something went wrong. Please try again!')
    
    jsonOutput = json.load(r)
    response = ""
    if len(jsonOutput['WaitTimeResult']) == 0:
        response = 'Sorry, I am unsure of the wait time'
    else:
        waittime = jsonOutput['WaitTimeResult'][0]
        response += "Earlier at " + waittime['createdDatetime'].split(' ')[1].split(':')[0] + ' ' +  waittime['createdDatetime'].split(' ')[2] + " the wait time was " + waittime['waitTime'].replace('-', ' to ') + 'utes'
    
    return construct_response(response)
    
def deltaHelp():
    out = 'Hi there! I am your personal assistant for anything Delta. You can ask me to find you flights. Or, to get the status of your next flight. Or to tell you the most recent TSA wait time, so you can get to the airport on time. So how can I help you today?'
    return construct_response(out)
    
def construct_response(output):
    return {
        'version': '1.0',
        'sessionAttributes': {},
        'response': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': output
            }
        }
    }