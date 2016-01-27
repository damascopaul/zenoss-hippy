#!/usr/bin/env python

# Posts zenoss alerts to a hipchat room

import requests
import json
import requests.exceptions
import argparse
import datetime
import sys

# import the stuff that zendmd needs and create the dmd context
import Globals
from Products.ZenUtils.ZenScriptBase import ZenScriptBase
from transaction import commit
dmd = ZenScriptBase(connect=True, noopts=True).dmd
 
# import the stuff that zep needs
from Products.Zuul import getFacade, listFacades
from zenoss.protocols.jsonformat import from_dict
from zenoss.protocols.protobufs.zep_pb2 import EventSummary
from Products.ZenEvents.events2.proxy import EventSummaryProxy

sync = dmd.zport._p_jar.sync
zep = getFacade('zep')
TIME=datetime.datetime.utcnow()
LOG_FILE='/var/log/zenoss-hippy.log'

#HipChat specific global variables
ROOM_ID=''
API_TOKEN=''

def log_this(log_message):
	log = open(LOG_FILE, 'a')
	log.write(log_message+"\n")
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

def get_alert(alrt_evid, alrt_type, alrt_urls):
	message = None

	try:
		filter_zep = zep.createEventFilter(uuid=alrt_evid)
		for summary in zep.getEventSummariesGenerator(filter=filter_zep):

			sync()

	        		evt = EventSummaryProxy(from_dict(EventSummary, summary))

			if evt.severity == 5:
				severity_string='Critical'
			elif evt.severity == 4:
				severity_string='Error'
			elif evt.severity == 3:
				severity_string='Warning'
			elif evt.severity == 2:
				severity_string='Info'
			elif evt.severity == 1:
				severity_string='Debug'

		  	if alrt_type == 'incident':
				message = """[casc-zenoss] SYSTEMS - {1} {2} <br /> Device: {1} <br /> Component: {3} <br /> Severity: {0} <br /> Time: {4} <br /> Message: <br /> {5} <br /> <a href="{6}">Event Detail</a> <br /> <a href="{7}">Acknowledge</a> <br /> <a href="{8}">Close</a> <br /> <a href="{9}">Device Events</a>""".format(severity_string, evt.device, evt.summary, evt.component, evt.lastTime, evt.message, alrt_urls[0], alrt_urls[1], alrt_urls[2], alrt_urls[3])
			else:
				message = """[casc-zenoss] SYSTEMS - CLEAR: {0} {7} <br /> Event: {1} <br /> Cleared by: {7} <br /> At: {2} <br /> Device: {0} <br /> Component: {3} <br /> Severity: {4} <br /> Message: <br /> {5} <br /> <a href="{6}">Undelete</a>""".format(evt.device, evt.summary, alrt_urls[2], evt.component, severity_string, evt.message, alrt_urls[0], alrt_urls[1])

		if message != None:
			post_alert(alrt_type, severity_string, message)
		else:
			raise Exception("Invalid region name: {0}".format(regions[x]))
	except Exception as e:
		log_this( '{1} : Unexpected error: {0}'.format(e, TIME) )
    		sys.exit(0)

parser = argparse.ArgumentParser(
	description="",
	usage=""
)
parser.add_argument(
	'urls',
	nargs='+',
	type=str
)
parser.add_argument(
	'-e', 
	'--evid', 
	nargs=1, 
	type=str, 
	required=True, 
	dest='evid'
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

alrt_message = get_alert(args.evid[0], args.alrt_type[0], args.urls)
