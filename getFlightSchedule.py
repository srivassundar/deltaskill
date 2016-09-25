from datetime import date
from urllib2 import urlopen
from urllib import urlencode


def getFlights(event, context):

    depDate = event['request']['intent']['slots']['DepartureDate']['value']
    retDate = \
        event['request']['intent']['slots']['ReturnDate']['value'] or None
    origin = event['request']['intent']['slots']['Origin']['value']
    dest = event['request']['intent']['slots']['Destination']['value']

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
        return construct_response(
            "Sorry, there was an error. Please try again!")

    itineraries = result['schedulesResponse']['itineraries'][:5]

    out = ("There are flights available from {origin} to {dest}" +
           " on {depDate}.").format(
            origin=result['origin']['name'],
            dest=result['destination']['name'],
            depCity=depCity
            )

    for it in itineraries:
        stops = it['slice']['stops']
        stops = str(stops) if stops else "non"

        fare = str(it['bestFare']['fareValue'])

        flights = it['slice']['flights']

        departTime = flight[0]['departTime']
        arrivalTime = flight[-1]['arriveTime']
        day = ("" if flight[0]['departDate'] == flight[-1]['arriveDate']
               else (" on " + str(flight[-1]['arriveDate'])))

        duration = it['slice']['duration']

        message = ("For {fare} dollars, there is a {stops} stop flight" +
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


if __name__ == '__main__':
    event, context = [], []
    lambda_handler(event, context)
