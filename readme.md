This nagios check script checks log file for any warning or above log level messages, and reports back the results to Nagios/icinga.

#Usage
```./check_bbsis_log.py [--file log_file_location]```

If ```--file``` is not supplied, the script checks several per-defined location, depending on how the script is called.

#log format it checks
The log file has to be in the following format in order for this script to check:

```"%(asctime)s - %(name)s - %(levelname)s - %(message)s"```

For example:
```2017-03-07 01:00:15,173 - follett_sftp - INFO - custom string...```