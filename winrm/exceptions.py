from __future__ import unicode_literals

import logging
import xmltodict

LOGGER = logging.getLogger(__name__)

class WinRMError(Exception):
    """"Generic WinRM error"""
    code = 500


class WinRMTransportError(Exception):
    """WinRM errors specific to transport-level problems (unexpcted HTTP error codes, etc)"""

    @property
    def protocol(self):
        return self.args[0]

    @property
    def code(self):
        return self.args[1]

    @property
    def message(self):
        return 'Bad HTTP response returned from server. Code {status_code}: {reason}'.format(
            status_code=self.code, reason=self.winrm_fault_reason)

    @property
    def response_text(self):
        return self.args[2]

    @property
    def response_dict(self):
        try:
            return xmltodict.parse(self.response_text)
        except (xmltodict.expat.ExpatError, TypeError):
            return None

    @property
    def winrm_fault_code(self):
        if isinstance(self.response_dict, dict):
            try:
                return self.response_dict['s:Envelope']['s:Body']['s:Fault']['s:Code']['s:Value']
            except (KeyError, AttributeError, TypeError) as exc:
                LOGGER.warning("Unable to find fault code: {exc}".format(exc=exc))
        return None

    @property
    def winrm_fault_subcode(self):
        if isinstance(self.response_dict, dict):
            try:
                return self.response_dict['s:Envelope']['s:Body']['s:Fault']['s:Code']['s:Subcode']['s:Value']
            except (KeyError, AttributeError, TypeError) as exc:
                LOGGER.warning("Unable to find fault sub code: {exc}".format(exc=exc))
        return None

    @property
    def winrm_fault_reason(self):
        if isinstance(self.response_dict, dict):
            try:
                return self.response_dict['s:Envelope']['s:Body']['s:Fault']['s:Reason']['s:Text']['#text']
            except (KeyError, AttributeError, TypeError) as exc:
                LOGGER.warning("Unable to find fault sub code: {exc}".format(exc=exc))
        return None

    def __str__(self):
        return self.message


class WinRMOperationTimeoutError(Exception):
    """
    Raised when a WinRM-level operation timeout (not a connection-level timeout) has occurred. This is
    considered a normal error that should be retried transparently by the client when waiting for output from
    a long-running process.
    """
    code = 500


class AuthenticationError(WinRMError):
    """Authorization Error"""
    code = 401


class BasicAuthDisabledError(AuthenticationError):
    message = 'WinRM/HTTP Basic authentication is not enabled on remote host'


class InvalidCredentialsError(AuthenticationError):
    pass
