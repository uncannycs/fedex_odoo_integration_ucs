# -*- coding:utf-8 -*-
import requests
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class ResCompany(models.Model):
    _inherit = "res.company"
    use_fdx_delivery = fields.Boolean(copy=False, string="Enable FedEx Shipping",
                                                 help="Activate to use FedEx as your shipping carrier.",
                                                 default=False)
    fdx_api_endpoint = fields.Char(string="FedEx API Endpoint", copy=False, default="https://apis-sandbox.fedex.com")
    fdx_client_key = fields.Char(string="FedEx API Key", copy=False)
    fdx_secret_key = fields.Char(string="FedEx API Secret", copy=False)
    fdx_acc_number = fields.Char(copy=False, string='FedEx Account No.',
                                       help="Your FedEx account number obtained during FedEx developer registration.")
    fdx_auth_token = fields.Char(string="FedEx Auth Token", copy=False)

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
