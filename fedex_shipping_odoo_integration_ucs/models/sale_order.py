from odoo import models, fields, api, _
import logging
_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = "sale.order"

    fdx_tp_account_number = fields.Char(copy=False, string='FexEx Third-Party Account Number',
                                                              help="Please Enter the Third Party account number ")
    fdx_tp_billing = fields.Boolean(string="FedEx Third Party Payment", copy=False, default=False,
                                                          help="when this fields is true,then we can visible fedex_third party account number")
