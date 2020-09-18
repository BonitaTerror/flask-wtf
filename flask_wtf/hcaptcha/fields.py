from wtforms.fields import Field

from . import widgets
from .validators import Hcaptcha

__all__ = ["HcaptchaField"]


class HcaptchaField(Field):
    widget = widgets.HcaptchaWidget()

    # error message if hcaptcha validation fails
    hcaptcha_error = None

    def __init__(self, label='', validators=None, **kwargs):
        validators = validators or [Hcaptcha()]
        super().__init__(label, validators, **kwargs)
