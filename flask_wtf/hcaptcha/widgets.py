from flask import Markup, current_app, json
from werkzeug.urls import url_encode

JSONEncoder = json.JSONEncoder

HCAPTCHA_SCRIPT = 'https://hcaptcha.com/1/api.js'
HCAPTCHA_TEMPLATE = '''
<script src='%s' async defer></script>
<div class="h-captcha" %s></div>
'''

__all__ = ['HcaptchaWidget']


class HcaptchaWidget:

    def hcaptcha_html(self, public_key):
        html = current_app.config.get('HCAPTCHA_HTML')
        if html:
            return Markup(html)
        params = current_app.config.get('HCAPTCHA_PARAMETERS')
        script = HCAPTCHA_SCRIPT
        if params:
            script += '?' + url_encode(params)

        attrs = current_app.config.get('HCAPTCHA_DATA_ATTRS', {})
        attrs['sitekey'] = public_key
        snippet = ' '.join(['data-{}="{}"'.format(k, attrs[k]) for k in attrs])
        return Markup(HCAPTCHA_TEMPLATE % (script, snippet))

    def __call__(self, field, error=None, **kwargs):
        """Returns the hcaptcha input HTML."""

        try:
            public_key = current_app.config['HCAPTCHA_PUBLIC_KEY']
        except KeyError:
            raise RuntimeError('HCAPTCHA_PUBLIC_KEY config not set')

        return self.hcaptcha_html(public_key)
