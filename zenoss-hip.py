#!/usr/bin/env python

import requests
import json
import requests.exceptions
import argparse
import datetime
import sys

TIME=datetime.datetime.utcnow()
LOG_FILE='/var/log/zenoss-hippy.log'

#HipChat specific global variables
ROOM_ID=''
API_TOKEN=''

def log_this(log_message):
	log = open(LOG_FILE, 'a')
	log.write(log_message)
	log.close()

#Post a message in HipChat using HipChat API v2
def post_alert(msg_type, msg_severity, msg_body):

	#Decide what meesage color to use
	#depending on the message type and severity
	msg_color='gray'
	if msg_type == 'incident' and msg_severity == 'Critical':
		msg_color = 'red'
	elif msg_type == 'incident' and msg_severity == 'Error':
		msg_color = 'yellow'
	elif msg_type == 'incident' and msg_severity == 'Warning':
		msg_color = 'purple'
	else:
		msg_color = 'green'

	# Send the message to HipChat
	headers = {
        		'Content-type': 'application/json',
    	}
    	parameters = {
    		'color':msg_color,
    		'notify':True,
    		'message':msg_body,
    	}
    	data = json.dumps(parameters)
    	try:
	    	response = requests.post(
	    		'https://api.hipchat.com/v2/room/{0}/notification?auth_token={1}'.format(ROOM_ID, API_TOKEN),
	    		headers=headers,
	    		data=data,
	    	)
	    	response.raise_for_status()
	    	log_this( '{0} : Successfully posted a message'.format(TIME) )
	except requests.exceptions.ConnectionError as e:
    		log_this( '{1} : There is a problem with your network. {0}'.format(e, TIME) )
    		sys.exit(0)
	except requests.exceptions.InvalidURL as e:
		log_this( "{1} : {0}".format(e, TIME) )
		sys.exit(0)
	except requests.exceptions.HTTPError as e:
    		log_this( '{1} : An error occured. {0}'.format(e, TIME) )
    		sys.exit(0)
    	except Exception as e:
    		log_this( '{1} : Unexpected error: {0}'.format(e, TIME) )
    		sys.exit(0)

def construct_message(alrt_type, alrt_body):
	message = None

	if alrt_type == 'incident':
		message = '[casc-zenoss] SYSTEMS - {1} {2} <br /> Device: {1} <br /> Component: {3} <br /> Severity: {0} <br /> Time: {4} <br /> Message: <br /> {5} <br /> <a href="{6}">Event Detail</a> <br /> <a href="{7}">Acknowledge</a> <br /> <a href="{8}">Close</a> <br /> <a href="{9}">Device Events</a>'.format(alrt_body[0], alrt_body[1], alrt_body[2], alrt_body[3], alrt_body[4], alrt_body[5], alrt_body[6], alrt_body[7], alrt_body[8], alrt_body[9])
	else:
		message = '[casc-zenoss] SYSTEMS - CLEAR: {3} {0} <br /> Event: {1} <br /> Cleared by: {0} <br /> At: {2} <br /> Device: {3} <br /> Component: {4} <br /> Severity: {5} <br /> Message: <br /> {6} <br /> <a href="{7}">Undelete</a>'.format(alrt_body[2], alrt_body[3], alrt_body[4], alrt_body[1], alrt_body[5], alrt_body[0], alrt_body[6], alrt_body[7])

	post_alert(alrt_type, alrt_body[0], message)

parser = argparse.ArgumentParser(
	description="Sends an incident/clear message from Zenoss to a HipChat Room",
	usage="\nFor incidents: python zenoss-hip.py '${evt/severityString}' '${evt/device}' '${evt/summary}' '${evt/component}' '${evt/lastTime}' '${evt/message}' '${urls/eventUrl}' '${urls/ackUrl}' '${urls/closeUrl}' '${urls/eventsUrl}' -t incident \
		\n\nFor clears: python zenoss-hip.py '${evt/severityString}' '${evt/device}' '${clearEvt/summary}' '${evt/summary}' '${clearEvt/firstTime}' '${evt/component}' '${evt/message}' '${urls/reopenUrl}' -t clear"
)
parser.add_argument(
	'alert', 
	nargs='+', 
	type=str
)
parser.add_argument(
	'-t', 
	'--type', 
	nargs=1, 
	default='incident', 
	type=str, 
	choices=['incident', 'clear'], 
	required=True, 
	dest='alrt_type'
)
args = parser.parse_args()

construct_message(args.alrt_type[0], args.alert)
