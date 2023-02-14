from odoo import models, fields, api
from dateutil import relativedelta
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare


class OfferModel(models.Model) :
    _name = "offer.model"
    _description = "Offer Model"
    _order = "price desc"

    price = fields.Float(string="Price")
    state = fields.Selection(string='Status', copy=False, default=False,
                             selection=[('accepted', 'Accepted'), ('refused', 'Refused')])
    partner_id = fields.Many2one("res.partner", string="Partner id", required=True)
    property_id = fields.Many2one("estate.model", string="Property id", required=True)

    validity = fields.Integer(string="Validity", default=7)
    date_deadline = fields.Date(string="Date Deadline", compute="_compute_date_deadline",
                                inverse="_inverse_date_deadline")

    property_type_id = fields.Many2one(
        "property.model", related="property_id.property_type_id", string="Property Type", store=True
    )

    @api.depends("create_date", "validity")
    def _compute_date_deadline(self) :
        for offer in self :
            if offer.create_date :
                date = offer.create_date.date()
            else :
                date = fields.Date.today()
            print(date)
            offer.date_deadline = date + relativedelta.relativedelta(days=offer.validity)

    @api.depends("create_date", "validity")
    def _inverse_date_deadline(self) :
        for offer in self :
            if offer.create_date :
                date = offer.create_date.date()
            else :
                date = fields.Date.today()
            print(date)
            offer.validity = (offer.date_deadline - date).days

    def action_accept(self) :
        if "accepted" in self.mapped("property_id.offer_ids.state") :
            raise UserError("An offer as already been accepted.")
        self.write(
            {
                "state" : "accepted",
            }
        )
        return self.mapped("property_id").write(
            {
                # "state" : "offer accepted",
                "selling_price" : self.price,
                "buyer" : self.partner_id,
            })

    def action_refuse(self) :
        return self.write(
            {
                "state" : "refused",
            }
        )

    _sql_constraints = [
        ("check_price", "CHECK(price > 0)", "The price must be strictly positive"),
    ]

    @api.model
    def create(self, vals) :
        if vals.get("property_id") and vals.get("price") :
            prop = self.env["estate.model"].browse(vals["property_id"])
            # We check if the offer is higher than the existing offers
            if prop.offer_ids :
                max_offer = max(prop.mapped("offer_ids.price"))
                if float_compare(vals["price"], max_offer, precision_rounding=0.01) <= 0 :
                    raise UserError("The offer must be higher than %.2f" % max_offer)
            prop.state = "offer received"
        return super().create(vals)
