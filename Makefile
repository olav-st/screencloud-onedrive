SOURCES += modules/onedrivesdk
SOURCES += modules/onedrivesdk_python2
SOURCES += modules/onedrivesdk_python3
SOURCES += modules/requests
SOURCES += modules/urllib3
SOURCES += modules/chardet
SOURCES += modules/certifi
SOURCES += modules/idna
SOURCES += modules/qsettings_session.py

SOURCES += icon.png
SOURCES += main.py
SOURCES += metadata.xml
SOURCES += settings.ui

ZIP = current.zip

all: $(ZIP)

$(ZIP): $(SOURCES)
	zip -r $@ $^
