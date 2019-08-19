import sys

if sys.version_info[0] <= 2:
	import onedrivesdk_python2
	sys.modules[__name__] = sys.modules['onedrivesdk_python2']
else:
	import onedrivesdk_python3
	sys.modules[__name__] = sys.modules['onedrivesdk_python3']
