# -*- coding:utf-8 -*-
import requests
import binascii
import json
import logging
from datetime import datetime
# from odoo.exceptions import Warning, ValidationError
from odoo.exceptions import ValidationError
from odoo import models, fields, api, _

_logger = logging.getLogger(__name__)


class DeliveryCarrier(models.Model):
    _inherit = "delivery.carrier"

    delivery_type = fields.Selection(selection_add=[('fdx_delivery', 'FedEx Shipping')],
                                     ondelete={'fdx_delivery': 'set default'})
    fdx_rate_request_type = fields.Selection([('LIST', 'LIST'),
                                           ('INCENTIVE', 'INCENTIVE'),
                                           ('ACCOUNT', 'ACCOUNT'),
                                           ('PREFERRED', 'PREFERRED')],
                                          string="FedEx Rate Type",
                                          default='ACCOUNT',
                                          help="LIST - Retrieves FedEx published list rates along with account-specific rates. PREFERRED - Returns rates in the preferred currency. ACCOUNT - Returns account-specific rates (Default). INCENTIVE - One-time discount rate. Contact your FedEx representative for details.")
    fdx_wt_uom = fields.Selection([('LB', 'LB'),
                                         ('KG', 'KG')], default='LB', string="Shipment Weight Unit",
                                        help="Unit of measurement for shipment weight.")

    fdx_shipping_service = fields.Selection(
        [('FEDEX_2_DAY', 'FedEx 2-Day'),  # for US Use: 33122 Florida Doral
         ('FEDEX_2_DAY_AM', 'FedEx 2-Day AM'),  # for US Use: 33122 Florida Doral
         ('FEDEX_INTERNATIONAL_PRIORITY_EXPRESS', 'FedEx Intl Priority Express'),
         # ('FEDEX_INTERNATIONAL_PRIORITY', 'FEDEX_INTERNATIONAL_PRIORITY'),
         # ('FEDEX_CUSTOM_CRITICAL_CHARTER_AIR', 'FedEx Custom Critical Air'),
         # ('FEDEX_CUSTOM_CRITICAL_AIR_EXPEDITE', 'FedEx Custom Critical Air Expedite'),
         # ('FEDEX_CUSTOM_CRITICAL_AIR_EXPEDITE_EXCLUSIVE_USE', 'FedEx Custom Critical Air Expedite Exclusive Use'),
         # ('FEDEX_CUSTOM_CRITICAL_AIR_EXPEDITE_NETWORK', 'FedEx Custom Critical Air Expedite Network'),
         # ('FEDEX_CUSTOM_CRITICAL_POINT_TO_POINT', 'FedEx Custom Critical Point To Point'),
         # ('FEDEX_CUSTOM_CRITICAL_SURFACE_EXPEDITE', 'FedEx Custom Critical Surface Expedite'),
         # ('FEDEX_CUSTOM_CRITICAL_SURFACE_EXPEDITE_EXCLUSIVE_USE',
         #  'FedEx Custom Critical Surface Expedite Exclusive Use'),
         ('FEDEX_EXPRESS_SAVER', 'FedEx Express Economy'),  # for US Use: 33122 Florida Doral
         ('FIRST_OVERNIGHT', 'FedEx First Overnight'),  # for US
         ('FEDEX_FIRST_OVERNIGHT_EXTRA_HOURS', 'FedEx First Overnight® Extra Hours'),
         ('FEDEX_GROUND', 'FedEx Ground Service'),  # When Call the service given the error "Customer not eligible for service"
         # ('GROUND_HOME_DELIVERY', 'FedEx Home Delivery'),
         # ('FEDEX_CARGO_AIRPORT_TO_AIRPORT', 'FedEx International Airport-to-Airport'),
         ('FEDEX_INTERNATIONAL_CONNECT_PLUS', 'FedEx Intl Connect Plus®'),
         ('INTERNATIONAL_ECONOMY', 'FedEx Intl Economy'),
         # ('INTERNATIONAL_ECONOMY_DISTRIBUTION', 'FedEx International Economy DirectDistributionSM'),
         ('INTERNATIONAL_FIRST', 'FedEx Intl First'),
         # ('FEDEX_CARGO_MAIL', 'FedEx International MailService®'),
         # ('FEDEX_CARGO_INTERNATIONAL_PREMIUM', 'FedEx International Premium™'),
         # ('INTERNATIONAL_PRIORITY_DISTRIBUTION', 'FedEx International Priority DirectDistribution®'),
         ('FEDEX_INTERNATIONAL_PRIORITY', 'FedEx Intl Priority®'),
         ('FEDEX_INTERNATIONAL_PRIORITY_PLUS', 'FedEx Intl Priority Plus®'),
         ('PRIORITY_OVERNIGHT', 'FedEx Priority Overnight'),  # for US
         # ('PRIORITY_OVERNIGHT_EXTRA_HOURS', 'FedEx Priority Overnight® EH'),
         ('SAME_DAY', 'FedEx Same Day'),
         ('SAME_DAY_CITY', 'FedEx Same Day City'),
         # ('SMART_POST', 'FedEx SmartPost'),  # When Call the service given the error "Customer not eligible for service"
         ('FEDEX_STANDARD_OVERNIGHT_EXTRA_HOURS', 'FedEx Std Overnight® Extra Hours'),  # WORKING FOR us ADDRESS
         ('STANDARD_OVERNIGHT', 'FedEx Standard Overnight'),  # for US Use: 33122 Florida Doral
         ('TRANSBORDER_DISTRIBUTION_CONSOLIDATION', 'FedEx Temp-Assure Air®'),
         # ('FEDEX_CUSTOM_CRITICAL_TEMP_ASSURE_VALIDATED_AIR', 'Temp-Assure Validated Air®'),
         # ('FEDEX_CUSTOM_CRITICAL_WHITE_GLOVE_SERVICES', 'White Glove Services®'),
         ('FEDEX_REGIONAL_ECONOMY', 'FedEx Regional Economy'),
         ('FEDEX_REGIONAL_ECONOMY_FREIGHT', 'FedEx Regional Economy Freight'),
         ('INTERNATIONAL_PRIORITY', 'FedEx Intl Priority'),
         ('EUROPE_FIRST_INTERNATIONAL_PRIORITY', 'FedEx Europe First Intl Priority'),
         ('FEDEX_DISTANCE_DEFERRED', 'FedEx Distance Deferred'),
         # for domestic UK pickup  Error : Customer is eligible.
         ('FEDEX_NEXT_DAY_AFTERNOON', 'FedEx Next Day PM'),  # for domestic UK pickup
         ('FEDEX_NEXT_DAY_EARLY_MORNING', 'FedEx Next Day Early AM'),  # for domestic UK pickup
         ('FEDEX_NEXT_DAY_END_OF_DAY', 'FedEx Next Day EOD'),  # for domestic UK pickup
         ('FEDEX_NEXT_DAY_FREIGHT', 'FedEx Next Day Freight'),  # for domestic UK pickup
         ('FEDEX_NEXT_DAY_MID_MORNING', 'FedEx Next Day Mid AM'),  # for domestic UK pickup
         ], string="FedEx Service", help="Choose the FedEx delivery service for this carrier.")
    fdx_default_package_type_id = fields.Many2one('stock.package.type', string="FedEx Package Type")
    fdx_pickup_method = fields.Selection([('CONTACT_FEDEX_TO_SCHEDULE', 'CONTACT_FEDEX_TO_SCHEDULE'),
                                          ('DROPOFF_AT_FEDEX_LOCATION', 'DROPOFF_AT_FEDEX_LOCATION'),
                                          ('USE_SCHEDULED_PICKUP', 'USE_SCHEDULED_PICKUP')],
                                         string="FedEx Pickup Method",
                                         default='USE_SCHEDULED_PICKUP',
                                         help="How the shipment will be handed over for FedEx collection.")
    fdx_label_stock = fields.Selection([
        # These values display a thermal format label
        ('PAPER_4X6', 'Paper 4X6 '),
        ('PAPER_4X8', 'Paper 4X8'),
        ('PAPER_4X9', 'Paper 4X9'),
        ('PAPER_4X675', 'PAPER_4X675'),
        ('PAPER_7X47', 'PAPER_7X47'),
        ('PAPER_85X11_BOTTOM_HALF_LABEL', 'PAPER_85X11_BOTTOM_HALF_LABEL'),
        ('PAPER_85X11_TOP_HALF_LABEL', 'PAPER_85X11_TOP_HALF_LABEL'),
        ('PAPER_LETTER', 'PAPER_LETTER'), ('STOCK_4X6', 'STOCK_4X6'),
        ('STOCK_4X675_LEADING_DOC_TAB', 'STOCK_4X675_LEADING_DOC_TAB'),
        ('STOCK_4X675_TRAILING_DOC_TAB', 'STOCK_4X675_TRAILING_DOC_TAB'),
        ('STOCK_4X8', 'STOCK_4X8'),
        ('STOCK_4X9', 'STOCK_4X9'),
        ('STOCK_4X9_LEADING_DOC_TAB', 'STOCK_4X9_LEADING_DOC_TAB'),
        ('STOCK_4X9_TRAILING_DOC_TAB', 'STOCK_4X9_TRAILING_DOC_TAB'),
        ('STOCK_4X85_TRAILING_DOC_TAB', 'STOCK_4X85_TRAILING_DOC_TAB'),
        ('STOCK_4X105_TRAILING_DOC_TAB', 'STOCK_4X105_TRAILING_DOC_TAB')], string="FedEx Label Stock",
        help="Specifies the paper stock type for label printing. Note: ZPL format requires STOCK type only.")
    fdx_label_format = fields.Selection([('PDF', 'PDF'),
                                                       ('PNG', 'PNG'), ('ZPLII', 'ZPLII')], string="Label Output Format")

    fdx_dropoff_method = fields.Selection([('BUSINESS_SERVICE_CENTER', 'Business Service Center'),
                                            ('DROP_BOX', 'Drop Box'),
                                            ('REGULAR_PICKUP', 'Regular Pickup'),
                                            ('REQUEST_COURIER', 'Request Courier'),
                                            ('STATION', 'Station')],
                                           string="FedEx Drop-off Method",
                                           default='REGULAR_PICKUP',
                                           help="How the shipment will be tendered for FedEx collection.")
    fdx_cod_collection_type = fields.Selection([('ANY', 'ANY'),
                                              ('CASH', 'CASH'),
                                              ('COMPANY_CHECK', 'COMPANY_CHECK'),
                                              ('GUARANTEED_FUNDS', 'GUARANTEED_FUNDS'),
                                              ('PERSONAL_CHECK', 'PERSONAL_CHECK'),
                                              ], default='ANY', string="COD Collection Method",
                                             help="Method of payment collection for Cash on Delivery shipments.")
    fdx_billing_type = fields.Selection([('SENDER', 'SENDER'),
                                           ('RECIPIENT', 'RECIPIENT'),
                                           ('THIRD_PARTY', 'THIRD_PARTY')], default='SENDER',
                                          string="FedEx Billing Method",
                                          help="Select who will be billed for the FedEx shipment.")
    fdx_use_onerate = fields.Boolean("FedEx One Rate Service", default=False)
    fdx_cod = fields.Boolean('COD')
    fdx_require_signature = fields.Boolean(string="Require Signature")
    fdx_signature_type = fields.Selection([('INDIRECT', 'INDIRECT'),
                                          ('DIRECT', 'DIRECT'),
                                          ('ADULT', 'ADULT')], string="Signature Type")
    fdx_insurance = fields.Boolean(string="Shipment Insurance",
                                     help="Enable insurance coverage for FedEx shipments.",
                                     default=True)

    def get_fdx_address(self, address_id):
        return {
            "address": {
                "city": address_id.city or "",
                "stateOrProvinceCode": address_id.state_id and address_id.state_id.code or "",
                "postalCode": "{0}".format(address_id.zip or ""),
                "countryCode": address_id.country_id and address_id.country_id.code or ""
            }
        }

    def fdx_delivery_rate_shipment(self, order):
        order_lines_without_weight = order.order_line.filtered(
            lambda line_item: not line_item.product_id.type in ['service',
                                                                'digital'] and not line_item.product_id.weight and not line_item.is_delivery)
        for order_line in order_lines_without_weight:
            raise ValidationError("Please define weight in product : \n %s" % (order_line.product_id.name))

        # Shipper and Recipient Address
        shipper_address_id = order.warehouse_id.partner_id
        recipient_address_id = order.partner_shipping_id
        company_id = self.company_id

        # check sender Address
        if not shipper_address_id.zip or not shipper_address_id.city or not shipper_address_id.country_id:
            raise ValidationError("Please Define Proper Sender Address!")

        # check Receiver Address
        if not recipient_address_id.zip or not recipient_address_id.city or not recipient_address_id.country_id:
            raise ValidationError("Please Define Proper Recipient Address!")

        total_weight = sum([(line.product_id.weight * line.product_uom_qty) for line in order.order_line]) or 0.0
        if not company_id.fdx_auth_token:
            raise ValidationError("Please enter correct credentials data!")
        try:
            api_url = "{0}/rate/v1/rates/quotes".format(company_id.fdx_api_endpoint)
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Authorization': 'Bearer {0}'.format(company_id.fdx_auth_token)
            }
            request_data = {
                "accountNumber": {"value": "{0}".format(company_id.fdx_acc_number)},
                "requestedShipment": {
                    "shipper": self.get_fdx_address(shipper_address_id),
                    "recipient": self.get_fdx_address(recipient_address_id),
                    "pickupType": self.fdx_pickup_method,
                    "serviceType": self.fdx_shipping_service,
                    "packagingType": self.fdx_default_package_type_id.shipper_package_code,
                    "rateRequestType": ["{0}".format(self.fdx_rate_request_type)],
                    "shipDateStamp": datetime.now().strftime('%Y-%m-%d'),
                    "totalWeight": ((total_weight) or 0),
                    "requestedPackageLineItems": [
                        {
                            "weight": {
                                "units": "{0}".format(self.fdx_wt_uom),
                                "value": (total_weight)
                            }, "dimensions": {
                            "length": self.fdx_default_package_type_id.packaging_length or '',
                            "width": self.fdx_default_package_type_id.width or '',
                            "height": self.fdx_default_package_type_id.height or '',
                            "units": 'IN' if self.fdx_wt_uom == 'LB' else 'CM'
                        }
                        }
                    ]
                }
            }
            if self.fdx_use_onerate:
                request_data.get("requestedShipment").update(
                    {"shipmentSpecialServices": {"specialServiceTypes": ["FEDEX_ONE_RATE"]}})
            if self.fdx_cod:
                request_data.get("requestedShipment").update(
                    {"shipmentSpecialServices": {"specialServiceTypes": ["COD"],
                                                 "shipmentCODDetail": {
                                                     "codCollectionType": self.fdx_cod_collection_type,
                                                     "codCollectionAmount": {
                                                         "amount": order.amount_total,
                                                         "currency": order.company_id.currency_id.name or "USD"
                                                     }}}})

            response_data = requests.request("POST", api_url, headers=headers, data=json.dumps(request_data))
            if response_data.status_code in [200, 201]:
                response_data = response_data.json()
                if response_data.get('output') and response_data.get('output').get('rateReplyDetails'):
                    for rateReplyDetail in response_data.get('output').get('rateReplyDetails'):
                        if self.fdx_shipping_service == rateReplyDetail.get("serviceType"):
                            for rate_info in rateReplyDetail.get('ratedShipmentDetails'):
                                return {'success': True, 'price': float(rate_info.get('totalNetFedExCharge')) or 0.0,
                                        'error_message': False, 'warning_message': False}
                else:
                    return {'success': False, 'price': 0.0, 'error_message': response_data,
                            'warning_message': False}
            else:
                return {'success': False, 'price': 0.0, 'error_message': response_data.text,
                        'warning_message': False}
        except Exception as e:
            return {'success': False, 'price': 0.0, 'error_message': e, 'warning_message': False}

    def get_fdx_shipping_address(self, address_id):
        address_dict = self.get_fdx_address(address_id)
        address_dict.update({"contact": {"personName": "Test",
                                         "emailAddress": address_id.email or "",
                                         "phoneNumber": "%s" % (address_id.phone or ""),
                                         "companyName": address_id.name}})
        address_dict.get("address").update({"streetLines": [address_id.street]})
        return address_dict

    def prepare_fdx_package(self, package_count=False, shipping_weight=False, packaging_length=False, width=False,
                              height=False, package_desscription=False):
        return {
            "sequenceNumber": "%s" % (package_count),
            "weight": {
                "units": "{0}".format(self.fdx_wt_uom),
                "value": shipping_weight
            },
            "dimensions": {
                "length": packaging_length or "",
                "width": width or "",
                "height": height or "",
                "units": 'IN' if self.fdx_wt_uom == 'LB' else 'CM'
            },
            "groupPackageCount": 1,
            "itemDescription": "%s" % (package_desscription),
        }

    def fdx_delivery_send_shipping(self, pickings):
        shipper_address_id = pickings.picking_type_id and pickings.picking_type_id.warehouse_id and pickings.picking_type_id.warehouse_id.partner_id
        receiver_id = pickings.partner_id
        company_id = self.company_id
        package_list = []
        package_count = 0
        total_bulk_weight = pickings.weight_bulk
        for package_id in pickings.package_ids:
            package_count = package_count + 1
            length = package_id.package_type_id.packaging_length if package_id.package_type_id.packaging_length else self.fdx_default_package_type_id.packaging_length or ""
            width = package_id.package_type_id.width if package_id.package_type_id.width else self.fdx_default_package_type_id.width or ""
            height = package_id.package_type_id.height if package_id.package_type_id.height else self.fdx_default_package_type_id.height or ""
            package_list.append(
                self.prepare_fdx_package(package_count, package_id.shipping_weight, length, width, height,
                                           package_id.name))
            if self.fdx_require_signature:
                package_list[-1].update({"packageSpecialServices": {
                    "specialServiceTypes": [
                        "SIGNATURE_OPTION"
                    ],
                    "signatureOptionType": self.fdx_signature_type or ''
                }})
        if total_bulk_weight:
            package_count = package_count + 1
            length = self.fdx_default_package_type_id.packaging_length or ""
            width = self.fdx_default_package_type_id.width or ""
            height = self.fdx_default_package_type_id.height or ""
            package_list.append(
                self.prepare_fdx_package(package_count, total_bulk_weight, length, width, height, pickings.name))
            if self.fdx_require_signature:
                package_list[-1].update({"packageSpecialServices": {
                    "specialServiceTypes": [
                        "SIGNATURE_OPTION"
                    ],
                    "signatureOptionType": self.fdx_signature_type or ''
                }})
        try:
            order = pickings.sale_id
            request_data = {
                "mergeLabelDocOption": "LABELS_AND_DOCS",
                "labelResponseOptions": "LABEL",
                "accountNumber": {"value": "{0}".format(company_id.fdx_acc_number)},
                "shipAction": "CONFIRM",
                "requestedShipment": {
                    "shipper": self.get_fdx_shipping_address(shipper_address_id),
                    "recipients": [self.get_fdx_shipping_address(receiver_id)],
                    "pickupType": self.fdx_pickup_method,
                    "serviceType": self.fdx_shipping_service,
                    "packagingType": self.fdx_default_package_type_id.shipper_package_code,
                    "totalWeight": pickings.shipping_weight,
                    "shippingChargesPayment": {
                        "paymentType": self.fdx_billing_type},
                    "labelSpecification": {
                        "labelFormatType": "COMMON2D",
                        "labelOrder": "SHIPPING_LABEL_FIRST",
                        "labelStockType": self.fdx_label_stock,
                        "imageType": self.fdx_label_format
                    },
                    # Insurance And Declared Value

                    "rateRequestType": ["{0}".format(self.fdx_rate_request_type)],
                    "preferredCurrency": pickings.sale_id.company_id.currency_id.name,
                    "totalPackageCount": package_count,
                    "requestedPackageLineItems": package_list
                }}
            # Insurance And Declared Value
            if self.fdx_insurance:
                request_data.get("requestedShipment").update({"customsClearanceDetail": {
                    "commodities": [
                        {
                            "totalCustomsValue": {
                                "amount": order.tax_totals.get('amount_total'),
                                "currency": pickings.sale_id and pickings.sale_id.company_id.currency_id.name or "USD"
                            }
                        }
                    ],
                    "insuranceCharge": {
                        "amount": order.tax_totals.get('amount_total'),
                        "currency": pickings.sale_id and pickings.sale_id.company_id.currency_id.name or "USD"
                    }
                }, })
            if self.fdx_billing_type != 'SENDER':
                request_data.get("requestedShipment").get('shippingChargesPayment').update(
                    {"payor": {"responsibleParty": {"accountNumber": {
                        "value": order.fdx_tp_account_number}}}})
            if self.fdx_use_onerate:
                request_data.get("requestedShipment").update(
                    {"shipmentSpecialServices": {"specialServiceTypes": ["FEDEX_ONE_RATE"]}})
            if self.fdx_cod:
                request_data.get("requestedShipment").update(
                    {"shipmentSpecialServices": {"specialServiceTypes": ["COD"],
                                                 "shipmentCODDetail": {
                                                     "codCollectionType": self.fdx_cod_collection_type,
                                                     "codCollectionAmount": {
                                                         "amount": pickings.sale_id and pickings.sale_id.amount_total,
                                                         "currency": pickings.sale_id and pickings.sale_id.company_id.currency_id.name or "USD"
                                                     }}}})
            if shipper_address_id.country_id.code != receiver_id.country_id.code:
                comodities_packages = []

                for package_id in pickings.package_ids:
                    for stock_quant_package in package_id.quant_ids:
                        product_id = stock_quant_package.product_id
                        # move_line_id = self.env['stock.move.line'].search([('product_id', '=', product_id.id)])
                        find_sale_line_id = pickings.sale_id.order_line.filtered(
                            lambda x: x.product_template_id.product_variant_id == product_id)

                        comodities_packages.append({
                            "description": "%s" % (package_id.name),
                            "countryOfManufacture": self.company_id and self.company_id.country_id.code,
                            "quantity": stock_quant_package.quantity,
                            "quantityUnits": "PCS",
                            "unitPrice": {
                                "amount": find_sale_line_id.price_subtotal / find_sale_line_id.product_qty,
                                "currency": self.company_id and self.company_id.currency_id.name
                            },
                            "customsValue": {
                                "amount": find_sale_line_id.price_subtotal / find_sale_line_id.product_qty,
                                "currency": self.company_id and self.company_id.currency_id.name
                            },
                            "weight": {
                                "units": self.fdx_wt_uom,
                                "value": stock_quant_package.quantity * product_id.weight
                            }
                        })
                if total_bulk_weight:
                    for move_line in pickings.move_line_ids:
                        if move_line.product_id and not move_line.result_package_id:
                            product_id = move_line.product_id
                            # move_line_id = self.env['stock.move.line'].search([('product_id', '=', product_id.id)])
                            find_sale_line_id = pickings.sale_id.order_line.filtered(
                                lambda x: x.product_template_id.product_variant_id == product_id)
                            comodities_packages.append({
                                "description": "%s" % (pickings.name),
                                "countryOfManufacture": self.company_id and self.company_id.country_id.code,
                                "quantity": move_line.quantity,
                                "quantityUnits": "PCS",
                                "unitPrice": {
                                    "amount": find_sale_line_id.price_subtotal / find_sale_line_id.product_qty,
                                    "currency": self.company_id and self.company_id.currency_id.name
                                },
                                "customsValue": {
                                    "amount": find_sale_line_id.price_subtotal / find_sale_line_id.product_qty,
                                    "currency": self.company_id and self.company_id.currency_id.name
                                },
                                "weight": {
                                    "units": self.fdx_wt_uom,
                                    "value": move_line.quantity * product_id.weight
                                }
                            })
                request_data.get("requestedShipment").update({"customsClearanceDetail": {
                    "dutiesPayment": {
                        "paymentType": "SENDER"
                    },
                    "isDocumentOnly": True,
                    "commodities": comodities_packages
                },
                    "shippingDocumentSpecification": {
                        "shippingDocumentTypes": [
                            "COMMERCIAL_INVOICE"
                        ],
                        "commercialInvoiceDetail": {
                            "documentFormat": {
                                "docType": "PDF",
                                "stockType": "PAPER_LETTER"
                            }
                        }
                    }
                })
            api_url = "{0}/ship/v1/shipments".format(company_id.fdx_api_endpoint)
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Authorization': 'Bearer {0}'.format(company_id.fdx_auth_token)
            }
            response_data = requests.request("POST", api_url, headers=headers, data=json.dumps(request_data))
            attachments = []
            if response_data.status_code in [200, 201]:
                response_data = response_data.json()
                _logger.info("Shipment Response Data %s" % response_data)
                if response_data.get('output') and response_data.get('output').get('transactionShipments'):
                    for transaction_shipment in response_data.get('output').get('transactionShipments'):
                        carrier_tracking_ref = transaction_shipment.get('masterTrackingNumber')
                        for piece_respone in transaction_shipment.get('pieceResponses'):
                            for package_document in piece_respone.get('packageDocuments'):
                                if package_document.get('contentType') == 'ACCEPTANCE_LABEL':
                                    label_type = 'FDX_Return_Label'
                                else:
                                    label_type = 'FDX_Label'
                                label_binary_data = binascii.a2b_base64(package_document.get('encodedLabel'))
                                attachments.append(
                                    ('%s.%s.%s' % (label_type,
                                                   piece_respone.get('packageSequenceNumber') or carrier_tracking_ref,
                                                   self.fdx_label_format),
                                     label_binary_data))
                        if shipper_address_id.country_id.code != receiver_id.country_id.code:
                            commercial_label = binascii.a2b_base64(
                                response_data.get('output').get('transactionShipments')[0].get('shipmentDocuments')[
                                    0].get(
                                    'encodedLabel'))
                            if commercial_label:
                                attachments.append(
                                    ('commercial invoice -%s.%s' % (
                                        carrier_tracking_ref,
                                        self.fdx_label_format),
                                     commercial_label))
                        msg = (_('<b>Shipment created!</b><br/>'))
                        pickings.message_post(body=msg, attachments=attachments)
                        return [{'exact_price': 0,
                                 'tracking_number': carrier_tracking_ref}]
                else:
                    raise ValidationError(response_data)
            else:
                raise ValidationError(response_data.text)
        except Exception as e:
            raise ValidationError(e)

    def fdx_delivery_get_tracking_link(self, pickings):
        res = ""
        for picking in pickings:
            link = "https://www.fedex.com/apps/fedextrack/?action=track&trackingnumber="
            res = '%s %s' % (link, picking.carrier_tracking_ref)
        return res

    def fdx_delivery_cancel_shipment(self, picking):
        try:
            request_data = {"accountNumber": {
                "value": self.company_id.fdx_acc_number
            },
                "senderCountryCode": "US",
                "deletionControl": "DELETE_ALL_PACKAGES",
                "trackingNumber": "%s" % (picking.carrier_tracking_ref)
            }
            api_url = "{0}/ship/v1/shipments/cancel".format(self.company_id.fdx_api_endpoint)
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Authorization': 'Bearer {0}'.format(self.company_id.fdx_auth_token)
            }
            response_data = requests.request("PUT", api_url, headers=headers, data=json.dumps(request_data))
            if response_data.status_code in [200, 201]:
                response_data = response_data.json()
                if response_data.get('output') and response_data.get('output').get('cancelledShipment'):
                    return True
                else:
                    raise ValidationError(response_data)
            else:
                raise ValidationError(response_data.text)
        except Exception as e:
            raise ValidationError(e)
