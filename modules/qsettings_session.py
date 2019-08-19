'''
------------------------------------------------------------------------------
 Copyright (c) 2015 Microsoft Corporation

 Permission is hereby granted, free of charge, to any person obtaining a copy
 of this software and associated documentation files (the "Software"), to deal
 in the Software without restriction, including without limitation the rights
 to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 copies of the Software, and to permit persons to whom the Software is
 furnished to do so, subject to the following conditions:

 The above copyright notice and this permission notice shall be included in
 all copies or substantial portions of the Software.

 THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 THE SOFTWARE.
------------------------------------------------------------------------------
'''
import onedrivesdk
from PythonQt.QtCore import QSettings
from time import time

class QSettingsSession(onedrivesdk.session.Session):

    def save_session(self, **save_session_kwargs):
        """Save the current session.
        IMPORTANT: This implementation should only be used for debugging.
        For real applications, the Session object should be subclassed and
        both save_session() and load_session() should be overwritten using
        the client system's correct mechanism (keychain, database, etc.).
        Remember, the access_token should be treated the same as a password.
        
        Args:
            save_session_kwargs (dicr): To be used by implementation
            of save_session, however save_session wants to use them. The
            default implementation (this one) takes a relative or absolute
            file path for pickle save location, under the name "path"
        """
        settings = QSettings()
        settings.beginGroup("uploaders")
        settings.beginGroup("onedrive")
        settings.beginGroup("session")
        settings.setValue("token-type", self.token_type)
        settings.setValue("expires-in", int(float(self._expires_at - time())))
        settings.setValue("scope", " ".join(self.scope))
        settings.setValue("access-token", self.access_token)
        settings.setValue("client-id", self.client_id)
        settings.setValue("auth-server-url", self.auth_server_url)
        settings.setValue("redirect-uri", self.redirect_uri)
        settings.setValue("refresh-token", self.refresh_token)
        settings.setValue("client-secret", self.client_secret)
        settings.endGroup()
        settings.endGroup()
        settings.endGroup()

    @staticmethod
    def load_session(**load_session_kwargs):
        settings = QSettings()
        settings.beginGroup("uploaders")
        settings.beginGroup("onedrive")
        settings.beginGroup("session")
        token_type = settings.value("token-type", None)
        expires_in = settings.value("expires-in", None)
        scope = settings.value("scope", None)
        access_token = settings.value("access-token", None)
        client_id = settings.value("client-id", None)
        auth_server_url = settings.value("auth-server-url", None)
        redirect_uri = settings.value("redirect-uri", None)
        refresh_token = settings.value("refresh-token", None)
        client_secret = settings.value("client-secret", None)
        settings.endGroup()
        settings.endGroup()
        settings.endGroup()

        return QSettingsSession(token_type, expires_in, scope, 
                                    access_token, client_id, auth_server_url, 
                                    redirect_uri, refresh_token=refresh_token, 
                                    client_secret=client_secret)
