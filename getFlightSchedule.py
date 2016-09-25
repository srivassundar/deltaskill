from datetime import date
from urllib2 import urlopen
from urllib import urlencode


def getFlightSchedule(event, context):

    depDate = event['request']['intent']['slots']['DepartureDate']['value']
    depCode = event['request']['intent']['slots']['DepartureCode']['value']
    arrCode = event['request']['intent']['slots']['ArrivalCode']['value']
    todayDate = date.today().strftime("%Y-%m-%d")

    data = {
        'apikey': 'zCQj3XGAs1q2tQ3RKGdk3XLJ4dQqp2NF',
        'todayDate': todayDate,
        'depDate': depDate,
        'depCode': depCode,
        'arrCode': arrCode
    }

    url = 'https://demo30-test.apigee.net/v1/hack/schedule' + \
        '?todayDate={todayDate}' + \
        '&departureDate={depDate}' + \
        '&departureAirportCode={depCode}' + \
        '&arrivalAirportCode={arrCode}' + \
        '&apikey={apikey}'.format(**data)

    # print url
    r = urlopen(url)
    result = r.json()['flightSchedulesResponse']
    if result['status'] = 'FAIL':
        return construct_response(
            "Sorry, there was an error. Please try again!")

    result = result['schedulesResponse']['flightScheduleTO']
    arrCity = result['arrivalCityName']
    depCity = result['departureCityName']
    flights = result['flightScheduleSliceTOList']

    out = "There are {numFlights} flights from {arrCity} to {depCity}" + \
        " on {depDate}.".format(
            numFlights=numFlights,
            arrCity=arrCity,
            depCity=depCity
            )

    return construct_response(out)


def construct_response(output):
    return return {
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
