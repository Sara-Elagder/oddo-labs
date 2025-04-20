from odoo import api, fields, models


class HospitalDepartment(models.Model):
    _name = "hms.department"
    _description = "HMS Department"
    _rec_name = "name"

    # Basic info
    name = fields.Char(string="Department Name", required=True, index=True)
    is_opened = fields.Boolean(string="Active Department", default=True)

    # Capacity management
    capacity = fields.Integer(
        string="Patient Capacity", help="Maximum number of patients"
    )

    # Relationships
    patients_ids = fields.One2many(
        comodel_name="hms.patient", inverse_name="department_id", string="Patients"
    )
    doctor_ids = fields.One2many(
        comodel_name="hms.doctor", inverse_name="department_id", string="Doctors"
    )

    # Statistics (computed fields)
    patient_count = fields.Integer(
        string="Patient Count", compute="_compute_patient_count", store=False
    )

    @api.depends("patients_ids")
    def _compute_patient_count(self):
        for department in self:
            department.patient_count = len(department.patients_ids)
