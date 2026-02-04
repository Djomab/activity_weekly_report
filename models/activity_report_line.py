from odoo import models, fields, api


class ActivityWeeklyReportLine(models.Model):
    _name = "activity.weekly.report.line"
    _description = "Activité du rapport hebdomadaire"
    _order = "priority desc, date_start"

    report_id = fields.Many2one(
        "activity.weekly.report",
        string="Rapport",
        required=True,
        ondelete="cascade"
    )

    name = fields.Char(
        string="Intitulé",
        required=True
    )

    date_start = fields.Date(
        string="Début"
    )

    date_end = fields.Date(
        string="Fin"
    )

    status = fields.Selection(
        [
            ("todo", "À faire"),
            ("in_progress", "En cours"),
            ("done", "Terminé"),
            ("blocked", "Bloqué"),
        ],
        default="todo"
    )

    priority = fields.Selection(
        [
            ("0", "Basse"),
            ("1", "Normale"),
            ("2", "Haute"),
            ("3", "Critique"),
        ],
        default="1"
    )

    progress = fields.Integer(
        string="% Réalisation",
        default=0
    )

    duration = fields.Float(
        string="Durée (jours)",
        compute="_compute_duration",
        store=True
    )

    @api.depends("date_start", "date_end")
    def _compute_duration(self):
        for rec in self:
            if rec.date_start and rec.date_end:
                rec.duration = (rec.date_end - rec.date_start).days + 1
            else:
                rec.duration = 0.0
