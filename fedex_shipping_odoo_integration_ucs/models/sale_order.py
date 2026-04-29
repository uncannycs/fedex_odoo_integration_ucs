from odoo import models, fields, api, _
import logging
_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = "sale.order"

    fdx_tp_account_number = fields.Char(copy=False, string='FedEx Third-Party Billing Account',
                                                              help="Enter the third-party account number for FedEx billing.")
    fdx_tp_billing = fields.Boolean(string="FedEx Third-Party Billing", copy=False, default=False,
                                                          help="Enable this to allow third-party billing for FedEx shipments.")
