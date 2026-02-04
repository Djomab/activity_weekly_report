from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import timedelta


class ActivityWeeklyReport(models.Model):
    _name = "activity.weekly.report"
    _description = "Rapport d'activité"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "week_start desc"

    name = fields.Char(
        string="Référence",
        compute="_compute_name",
        store=True
    )

    department_id = fields.Many2one(
        "hr.department",
        string="Service",
        required=True,
        tracking=True
    )

    direction_id = fields.Many2one(
        "hr.department",
        string="Direction",
        related="department_id.parent_id",
        store=True
    )

    employee_id = fields.Many2one(
        "hr.employee",
        string="Responsable",
        compute="_compute_employee",
        store=True
    )

    user_id = fields.Many2one(
        "res.users",
        string="Utilisateur",
        default=lambda self: self.env.user,
        readonly=True
    )

    week_start = fields.Date(
        string="Début de semaine",
        required=True
    )

    week_end = fields.Date(
        string="Fin de semaine",
        required=True
    )

    year = fields.Integer(
        string="Année",
        compute="_compute_year",
        store=True
    )

    state = fields.Selection(
        [
            ("draft", "Brouillon"),
            ("submitted", "Soumis"),
            ("validated", "Validé"),
            ("rejected", "Rejeté"),
        ],
        default="draft",
        tracking=True
    )

    line_ids = fields.One2many(
        "activity.weekly.report.line",
        "report_id",
        string="Activités réalisées"
    )

    blocking_points = fields.Text(
        string="Points bloquants"
    )

    arbitration_required = fields.Boolean(
        string="Arbitrage DG requis"
    )

    corrective_actions = fields.Text(
        string="Actions correctives"
    )

    # --------------------
    # COMPUTES
    # --------------------

    @api.depends("department_id", "week_start")
    def _compute_name(self):
        for rec in self:
            if rec.department_id and rec.week_start:
                week = rec.week_start.isocalendar()[1]
                rec.name = f"Rapport S{week} - {rec.department_id.name}"
            else:
                rec.name = "Rapport hebdomadaire"

    @api.depends("week_start")
    def _compute_year(self):
        for rec in self:
            rec.year = rec.week_start.year if rec.week_start else False

    @api.depends("department_id")
    def _compute_employee(self):
        for rec in self:
            rec.employee_id = rec.department_id.manager_id if rec.department_id else False

    # --------------------
    # ACTIONS
    # --------------------

    def action_submit(self):
        for rec in self:
            if not rec.line_ids:
                raise UserError("Vous devez renseigner au moins une activité.")
            rec.state = "submitted"

    def action_validate(self):
        self.write({"state": "validated"})

    def action_reject(self):
        self.write({"state": "rejected"})
