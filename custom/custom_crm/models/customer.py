from odoo import models, fields, api
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = "res.partner"

    related_patient_id = fields.Many2one("hms.patient", string="Related Patient")

    @api.constrains("email")
    def _check_email_not_in_patients(self):
        for rec in self:
            if rec.email:
                patient = self.env["hms.patient"].search([("email", "=", rec.email)])
                if patient:
                    raise ValidationError(
                        "This email already exists in the patient model!"
                    )

    def unlink(self):
        for rec in self:
            if rec.related_patient_id:
                raise ValidationError("Cannot delete a customer linked to a patient!")
        return super().unlink()

    @api.model
    def create(self, vals):
        if "vat" not in vals or not vals["vat"]:
            raise ValidationError("Tax ID is required for CRM Customers!")
        return super().create(vals)

    def write(self, vals):
        if "vat" in vals and not vals["vat"]:
            raise ValidationError("Tax ID is required for CRM Customers!")
        return super().write(vals)
