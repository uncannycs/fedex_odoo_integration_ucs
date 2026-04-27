import requests
from odoo import models, fields, api
from odoo.exceptions import ValidationError

class ResCompany(models.Model):
    _inherit = "res.company"
    use_fdx_delivery = fields.Boolean(copy=False, string="Are You Use FedEx Shipping Provider.?",
                                                 help="If use fedEx shipping provider than value set TRUE.",
                                                 default=False)
    fdx_api_endpoint = fields.Char(string="FedEx API URL", copy=False, default="https://apis-sandbox.fedex.com")
    fdx_client_key = fields.Char(string="FedEx Client ID", copy=False)
    fdx_secret_key = fields.Char(string="FedEx Client Secret", copy=False)
    fdx_acc_number = fields.Char(copy=False, string='Account Number',
                                       help="The account number sent to you by Fedex after registering for Web Services.")
    fdx_auth_token = fields.Char(string="FedEx Access Token", copy=False)

    def auto_generate_fdx_auth_token(self):
        for company_id in self.search([('use_fdx_delivery', '!=', False)]):
            company_id.generate_fdx_auth_token()

    def generate_fdx_auth_token(self):
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        api_url = "%s/oauth/token" % (self.fdx_api_endpoint)
        if not self.fdx_client_key or not self.fdx_secret_key:
            raise ValidationError("Please enter correct credentials")
        data = {
            'client_id': self.fdx_client_key,
            'client_secret': self.fdx_secret_key,
            'grant_type': 'client_credentials',
        }
        try:
            response_data = requests.request("POST", api_url, headers=headers, data=data)
            if response_data.status_code in [200, 201]:
                response_data = response_data.json()
                if response_data.get('access_token'):
                    self.fdx_auth_token = response_data.get('access_token')
                    return {
                        'effect': {
                            'fadeout': 'slow',
                            'message': "Yeah! Token has been retrieved.",
                            'img_url': '/web/static/img/smile.svg',
                            'type': 'rainbow_man',
                        }
                    }
                else:
                    raise ValidationError(response_data)
        except Exception as e:
            raise ValidationError(e)
