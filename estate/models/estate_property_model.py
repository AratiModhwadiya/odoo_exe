from odoo import models, fields, api


class PropertyModel(models.Model) :
    _name = "property.model"
    _description = "Property Model"
    _order = "name"

    name = fields.Char(string="Property Type")
    # property_type = fields.Selection(string="Property Type",
    #              selection=[('house', 'House'), ('2bhk_apartment', '2BHK Apartment')])
    property_ids = fields.One2many("estate.model", "property_type_id", string="Properties")
    sequence = fields.Integer("Sequence", default=10)

    offer_count = fields.Integer(string="Offers Count", compute="_compute_offer")
    offer_ids = fields.One2many("offer.model", string="Offers", compute="_compute_offer")

    _sql_constraints = [
        ("check_name", "unique(name)", "The property name must be unique"),
    ]

    def _compute_offer(self) :

        # This solution is quite complex. It is likely that the trainee would have done a search in
        # a loop.
        data = self.env["offer.model"].read_group(
            [("property_id.state", "!=", "canceled"), ("property_type_id", "!=", False)],
            ["ids:array_agg(id)", "property_type_id"],
            ["property_type_id"],
        )
        mapped_count = {d["property_type_id"][0] : d["property_type_id_count"] for d in data}
        mapped_ids = {d["property_type_id"][0] : d["ids"] for d in data}
        for prop_type in self :
            prop_type.offer_count = mapped_count.get(prop_type.id, 0)
            prop_type.offer_ids = mapped_ids.get(prop_type.id, [])

    # def action_view_offers(self) :
    #     res = self.env.ref("estate.estate_property_offer_action").read()[0]
    #     res["domain"] = [("id", "in", self.offer_ids.ids)]
    #     return res

    def action_view_offers(self) :
        ''' Redirect the user to the invoice(s) paid by this payment.
        :return:    An action on account.move.
        '''
        self.ensure_one()

        action = {
            'name' : ("Offers"),
            'type' : 'ir.actions.act_window',
            'res_model' : 'offer.model',
            'context' : {'create' : False},
        }
        if len(self.offer_ids) == 1 :
            action.update({
                'view_mode' : 'form',
                'res_id' : self.offer_ids.id,
            })
        else :
            action.update({
                'view_mode' : 'list,form',
                'domain' : [('id', 'in', self.offer_ids.ids)],
            })
        return action
