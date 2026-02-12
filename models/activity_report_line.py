from odoo import models, fields, api
from odoo.exceptions import ValidationError


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

    progress = fields.Float(
        string="% Réalisation",
        default=0.0,
        digits=(5, 2)  # 5 chiffres au total, 2 après la virgule (ex: 100.00)
    )

    duration = fields.Float(
        string="Durée (jours)",
        compute="_compute_duration",
        store=True
    )

    # --------------------
    # COMPUTES
    # --------------------

    @api.depends("date_start", "date_end")
    def _compute_duration(self):
        for rec in self:
            if rec.date_start and rec.date_end:
                rec.duration = (rec.date_end - rec.date_start).days + 1
            else:
                rec.duration = 0.0

    # --------------------
    # ONCHANGES
    # --------------------

    @api.onchange('status')
    def _onchange_status(self):
        """Quand le statut passe à 'Terminé', mettre automatiquement le progrès à 100%"""
        if self.status == 'done':
            self.progress = 100.0

    # --------------------
    # CONTRAINTES
    # --------------------

    @api.constrains('progress')
    def _check_progress(self):
        """Vérifie que le pourcentage est entre 0 et 100"""
        for rec in self:
            if not (0 <= rec.progress <= 100):
                raise ValidationError("Le pourcentage de réalisation doit être entre 0 et 100.")

    @api.constrains('date_start', 'date_end')
    def _check_dates(self):
        """Vérifie que la date de fin est >= date de début"""
        for rec in self:
            if rec.date_start and rec.date_end and rec.date_end < rec.date_start:
                raise ValidationError("La date de fin doit être postérieure ou égale à la date de début.")