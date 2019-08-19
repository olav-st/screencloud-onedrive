###############################
## Workaround for sys.argv errors ##
import sys
if not hasattr(sys, 'argv'):
    sys.argv  = ['']
###############################

import ScreenCloud
import time, string, sys
import onedrivesdk
from qsettings_session import QSettingsSession
from PythonQt.QtCore import QFile, QSettings, QUrl, QByteArray, QBuffer, QIODevice
from PythonQt.QtGui import QDesktopServices, QMessageBox
from PythonQt.QtUiTools import QUiLoader

CLIENT_ID = "9c873595-299c-49af-a8df-c0c857e202cc"
REDIRECT_URI = "https://login.microsoftonline.com/common/oauth2/nativeclient"
API_BASE_URL = "https://api.onedrive.com/v1.0/"
SCOPES = ["wl.signin", "wl.offline_access", "onedrive.appfolder"]

class OneDriveUploader():
    def __init__(self):
        self.uil = QUiLoader()
        self.loadSettings()

        http_provider = onedrivesdk.HttpProvider()
        auth_provider = onedrivesdk.AuthProvider(
            http_provider=http_provider,
            client_id=CLIENT_ID,
            scopes=SCOPES,
            session_type=QSettingsSession)

        try:
            auth_provider.load_session()
            self.loggedIn = True
        except:
            self.loggedIn = False

        self.client = onedrivesdk.OneDriveClient(API_BASE_URL, auth_provider, http_provider)

    def showSettingsUI(self, parentWidget):
        self.parentWidget = parentWidget
        self.settingsDialog = self.uil.load(QFile(workingDir + "/settings.ui"), parentWidget)
        self.settingsDialog.group_account.widget_authorize.button_authenticate.connect("clicked()", self.startAuthenticationProcess)
        self.settingsDialog.group_account.widget_loggedIn.button_logout.connect("clicked()", self.logout)
        self.settingsDialog.group_name.input_nameFormat.connect("textChanged(QString)", self.nameFormatEdited)
        self.settingsDialog.connect("accepted()", self.saveSettings)
        self.loadSettings()
        self.updateUi()
        self.settingsDialog.open()

    def updateUi(self):
        self.loadSettings()
        if not self.loggedIn:
            self.settingsDialog.group_account.widget_loggedIn.setVisible(False)
            self.settingsDialog.group_account.widget_authorize.setVisible(True)
            self.settingsDialog.group_account.widget_authorize.button_authenticate.setEnabled(True)
            self.settingsDialog.group_name.setEnabled(False)
            self.settingsDialog.group_clipboard.setEnabled(False)
        else:
            self.settingsDialog.group_account.widget_loggedIn.setVisible(True)
            self.settingsDialog.group_account.widget_authorize.setVisible(False)
            self.settingsDialog.group_account.widget_loggedIn.label_user.setText(self.displayName)
            self.settingsDialog.group_name.setEnabled(True)
            self.settingsDialog.group_clipboard.setEnabled(True)

        self.settingsDialog.group_clipboard.radio_publiclink.setChecked(self.copyLink)
        self.settingsDialog.group_clipboard.radio_dontcopy.setChecked(not self.copyLink)
        self.settingsDialog.group_name.input_nameFormat.setText(self.nameFormat)
        self.settingsDialog.adjustSize()


    def loadSettings(self):
        settings = QSettings()
        settings.beginGroup("uploaders")
        settings.beginGroup("onedrive")
        self.displayName = settings.value("display-name", "")
        self.copyLink = settings.value("copy-link", "true") in ['true', True]
        self.nameFormat = settings.value("name-format", "Screenshot at %H-%M-%S")
        settings.endGroup()
        settings.endGroup()

    def saveSettings(self):
        settings = QSettings()
        settings.beginGroup("uploaders")
        settings.beginGroup("onedrive")
        settings.setValue("display-name", self.displayName)
        settings.setValue("copy-link", self.settingsDialog.group_clipboard.radio_publiclink.checked)
        settings.setValue("name-format", self.settingsDialog.group_name.input_nameFormat.text)
        settings.endGroup()
        settings.endGroup()
        self.client.auth_provider.save_session()

    def isConfigured(self):
        self.loadSettings()
        return self.loggedIn

    def getFilename(self):
        self.loadSettings()
        return ScreenCloud.formatFilename(self.nameFormat)

    def upload(self, screenshot, name):
        self.loadSettings()
        if self.loggedIn:
            self.client.auth_provider.refresh_token()
        #Save to temporary file
        timestamp = time.time()
        try:
            tmpFilename = QDesktopServices.storageLocation(QDesktopServices.TempLocation) + "/" + ScreenCloud.formatFilename(str(timestamp))
        except AttributeError:
            from PythonQt.QtCore import QStandardPaths #fix for Qt5
            tmpFilename = QStandardPaths.writableLocation(QStandardPaths.TempLocation) + "/" + ScreenCloud.formatFilename(str(timestamp))
        screenshot.save(QFile(tmpFilename), ScreenCloud.getScreenshotFormat())
        #Workaround to get id of app folder
        import requests, json
        endpoint = "https://api.onedrive.com/v1.0/drives/me/special/approot"
        headers = {"Authorization": "Bearer " + self.client.auth_provider.access_token}
        response = requests.get(endpoint, headers=headers).json()
        appfolder_id = response["id"]
        #Upload
        uploaded_item = self.client.item(drive='me', id=appfolder_id).children[ScreenCloud.formatFilename(name)].upload(tmpFilename)
        print(uploaded_item, " ".join(dir(uploaded_item)), str(uploaded_item), uploaded_item.id, uploaded_item.image)
        if self.copyLink:
            permission = self.client.item(id=uploaded_item.id).create_link("view").post()
            ScreenCloud.setUrl(permission.link.web_url)

        return True

    def startAuthenticationProcess(self):
        self.settingsDialog.group_account.widget_authorize.button_authenticate.setEnabled(False)
        authorize_url = QUrl(self.client.auth_provider.get_auth_url(REDIRECT_URI))
        QDesktopServices.openUrl(authorize_url)
        try:
            code = raw_input("Copy everything in the address bar after \"code=\", and paste it below:")
        except NameError:
            code = input("Copy everything in the address bar after \"code=\", and paste it below:")
        if code:
            try:
                self.client.auth_provider.authenticate(code, REDIRECT_URI, None)
            except:
                if "win" in sys.platform: #Workaround for crash on windows
                    self.parentWidget.hide()
                    self.settingsDialog.hide()
                QMessageBox.critical(self.settingsDialog, "Failed to authenticate", "Failed to authenticate with OneDrive. Wrong code?")
                if "win" in sys.platform:
                    self.settingsDialog.show()
                    self.parentWidget.show()
        
        #Set display name
        self.displayName = self.client.drive.get().owner.user.display_name
        self.loggedIn = True

        self.saveSettings()
        self.updateUi()

    def logout(self):
        settings = QSettings()
        settings.beginGroup("uploaders")
        settings.beginGroup("onedrive")
        settings.beginGroup("session")
        settings.remove("")
        settings.endGroup()
        settings.endGroup()
        settings.endGroup()
        self.loggedIn = False
        self.loadSettings()
        self.updateUi()

    def nameFormatEdited(self, nameFormat):
        self.settingsDialog.group_name.label_example.setText(ScreenCloud.formatFilename(nameFormat))
