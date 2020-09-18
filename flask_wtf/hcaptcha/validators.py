from urllib import request as http

import json

from flask import current_app, request
from werkzeug.urls import url_encode
from wtforms import ValidationError

from .._compat import to_bytes, to_unicode

HCAPTCHA_VERIFY_SERVER = 'https://hcaptcha.com/siteverify'
HCAPTCHA_ERROR_CODES = {
    'missing-input-secret': 'The secret parameter is missing.',
    'invalid-input-secret': 'The secret parameter is invalid or malformed.',
    'missing-input-response': 'The response parameter is missing.',
    'invalid-input-response': 'The response parameter is invalid or malformed.',
    'bad-request': 'The request is invalid or malformed',
    'invalid-or-already-seen-response': 'The response parameter has already been checked, or has another issue.',
    'sitekey-secret-mismatch': 'The sitekey is not registered with the provided secret.'
}

__all__ = ["Hcaptcha"]


class Hcaptcha:
    """Validates an HCaptcha"""

    def __init__(self, message=None):
        if message is None:
            message = HCAPTCHA_ERROR_CODES['missing-input-response']
        self.message = message

    def __call__(self, form, field):
        if current_app.testing:
            return True

        if request.json:
            response = request.json.get('h-captcha-response', '')
        else:
            response = request.form.get('h-captcha-response', '')
        remote_ip = request.remote_addr

        if not response:
            raise ValidationError(field.gettext(self.message))

        if not self._validate_hcaptcha(response, remote_ip):
            field.recaptcha_error = 'incorrect-captcha-sol'
            raise ValidationError(field.gettext(self.message))

    def _validate_hcaptcha(self, response, remote_addr):
        """Performs the actual validation."""
        try:
            private_key = current_app.config['HCAPTCHA_PRIVATE_KEY']
        except KeyError:
            raise RuntimeError("No HCAPTCHA_PRIVATE_KEY config set")

        data = url_encode({
            'secret':     private_key,
            'remoteip':   remote_addr,
            'response':   response
        })

        http_response = http.urlopen(HCAPTCHA_VERIFY_SERVER, to_bytes(data))

        if http_response.code != 200:
            return False

        json_resp = json.loads(to_unicode(http_response.read()))

        if json_resp["success"]:
            return True

        for error in json_resp.get("error-codes", []):
            if error in HCAPTCHA_ERROR_CODES:
                raise ValidationError(HCAPTCHA_ERROR_CODES[error])

        return False
