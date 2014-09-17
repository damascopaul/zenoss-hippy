zenoss-hip.py
=============

Python script to post Zenoss alert and clear messages to HipChat using HipChat API v2.

###Requirements

####Python Libraries
Make sure the following Python libraries are installed on your system:
* ```requests``` - available in https://github.com/kennethreitz/requests

###Configuration

Set the global variables before running the script.

Global variable      | Description
-------------------- | -----------
LOG_FILE				 | The file where the logs will be written
ROOM_ID				 | The room ID in HipChat where the alert messages will be posted
API_TOKEN				 | The HipChat API v2 token.

###Usage

####Zenoss Notification
Login to your Zenoss web console. Then go to ```Events > Triggers > Notifications```. Create a new notification and select ```command``` as its action. Go to the content tab of your notification and paste the command below on the Command field.

``` 
python /path/to/zenoss-hippy/zenoss-hip.py '${urls/eventUrl}' '${urls/ackUrl}' '${urls/closeUrl}' '${urls/eventsUrl}' -e '${evt/uuid}' -t incident
```

Then, on the Clear Command field, paste the command found below.

```
python /path/to/zenoss-hippy/zenoss-hip.py '${urls/reopenUrl}' -e '${evt/uuid}' -t clear
```

Note: Change ```/path/to/zenoss-hippy/zenoss-hip.py``` to the path where you placed the script.

####Log File

The default location for the log file is ```/var/log/zenoss-hippy.log```. You will need to create the log file and set the proper access permissions.

#####Create the logfile
```$ sudo touch /var/log/zenoss-hippy.log```

#####Set the proper file permissions
```$ sudo chown zenoss:zenoss /var/log/zenoss-hippy.log```

```$ sudo chmod 660 /var/log/zenoss-hippy.log```