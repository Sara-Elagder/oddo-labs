from odoo import models, fields, api


class MedicalDoctor(models.Model):
    _name = "hms.doctor"
    _description = "Hospital Medical Staff"
    _order = "last_name, first_name"

    # Personal information
    first_name = fields.Char(required=True)
    last_name = fields.Char(required=True)
    full_name = fields.Char(compute="_compute_full_name", store=False)
    image = fields.Binary(string="Doctor's Photo")

    # Professional details
    specialty = fields.Selection(
        [
            ("cardiology", "Cardiology"),
            ("neurology", "Neurology"),
            ("orthopedics", "Orthopedics"),
            ("pediatrics", "Pediatrics"),
            ("general", "General Medicine"),
        ],
        string="Medical Specialty",
    )

    # Relationships
    department_id = fields.Many2one(
        "hms.department", string="Department", ondelete="restrict"
    )
    patient_ids = fields.Many2many("hms.patient", string="Patients")

    # Statistics
    patient_count = fields.Integer(
        compute="_compute_patient_count", string="Patient Count"
    )

    # Display name
    def name_get(self):
        result = []
        for doctor in self:
            name = f"Dr. {doctor.first_name} {doctor.last_name}"
            result.append((doctor.id, name))
        return result

    @api.depends("patient_ids")
    def _compute_patient_count(self):
        for doctor in self:
            doctor.patient_count = len(doctor.patient_ids)

    @api.depends("first_name", "last_name")
    def _compute_full_name(self):
        for doctor in self:
            doctor.full_name = (
                f"{doctor.first_name or ''} {doctor.last_name or ''}".strip()
            )
