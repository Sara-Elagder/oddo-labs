from odoo import api, fields, models
from odoo.exceptions import ValidationError
import re
from datetime import date


class HmsPatient(models.Model):
    _name = "hms.patient"
    _description = "HMS Patient Record"

    # Personal Information
    first_name = fields.Char(required=True)
    last_name = fields.Char(required=True)
    email = fields.Char()
    birth_date = fields.Date()
    age = fields.Integer(compute="_calculate_patient_age", store=False)
    address = fields.Text()

    # Medical Information
    cr_ratio = fields.Float()
    pcr = fields.Boolean()
    history = fields.Html()
    blood_type = fields.Selection(
        [
            ("a", "A"),
            ("b", "B"),
            ("ab", "AB"),
            ("o", "O"),
        ],
        string="Blood Type",
    )

    # Media
    image = fields.Binary()

    # Relationships
    department_id = fields.Many2one(
        "hms.department", string="Department", domain="[('is_opened', '=', True)]"
    )
    department_capacity = fields.Integer(
        related="department_id.capacity", readonly=True
    )
    doctor_ids = fields.Many2many("hms.doctor", string="Doctors")
    log_ids = fields.One2many("hms.patient.log", "patient_id", string="Logs")

    # Status
    STATES = [
        ("undetermined", "Undetermined"),
        ("good", "Good"),
        ("fair", "Fair"),
        ("serious", "Serious"),
    ]
    state = fields.Selection(STATES, default="undetermined", string="State")

    # Constraints
    _sql_constraints = [
        ("unique_email", "UNIQUE(email)", "This email address is already registered!")
    ]

    # Display name in lists
    def name_get(self):
        result = []
        for rec in self:
            full_name = f"{rec.first_name} {rec.last_name}"
            result.append((rec.id, full_name))
        return result

    # Age calculation
    @api.depends("birth_date")
    def _calculate_patient_age(self):
        today = fields.Date.today()
        for patient in self:
            if patient.birth_date:
                delta = today - patient.birth_date
                patient.age = delta.days // 365
            else:
                patient.age = 0

    # Auto PCR check for young patients
    @api.onchange("age", "birth_date")
    def _trigger_pcr_check(self):
        if self.age and self.age < 30:
            self.pcr = True
            return {
                "warning": {
                    "title": "PCR Check",
                    "message": "PCR has been automatically checked as patient age is below 30.",
                }
            }

    # Email validation
    @api.constrains("email")
    def _validate_email_format(self):
        email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        for record in self:
            if record.email and not re.match(email_regex, record.email):
                raise ValidationError("Please enter a valid email address")

    # Log state changes
    def write(self, vals):
        result = super(HmsPatient, self).write(vals)
        if "state" in vals:
            self.env["hms.patient.log"].create(
                {
                    "patient_id": self.id,
                    "description": f'Status changed to {vals["state"]}',
                    "created_by": self.env.user.id,
                }
            )
        return result

    # State change actions
    def set_good(self):
        self.state = "good"

    def set_fair(self):
        self.state = "fair"

    def set_serious(self):
        self.state = "serious"

    def set_undetermined(self):
        self.state = "undetermined"


class PatientLog(models.Model):
    _name = "hms.patient.log"
    _description = "Patient Log"
    _order = "date desc"

    patient_id = fields.Many2one("hms.patient", string="Patient")
    description = fields.Text(string="Description")
    date = fields.Datetime(string="Date", default=fields.Datetime.now)
    created_by = fields.Many2one(
        "res.users", string="Created By", default=lambda self: self.env.user
    )
