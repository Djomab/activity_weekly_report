from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
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
        required=True,
        tracking=True
    )

    week_end = fields.Date(
        string="Fin de semaine",
        required=True,
        tracking=True
    )

    year = fields.Integer(
        string="Année",
        compute="_compute_year",
        store=True,
        index=True
    )

    state = fields.Selection(
        [
            ("draft", "Brouillon"),
            ("submitted", "Soumis"),
            ("validated", "Validé"),
            ("rejected", "Rejeté"),
        ],
        default="draft",
        tracking=True,
        required=True
    )

    line_ids = fields.One2many(
        "activity.weekly.report.line",
        "report_id",
        string="Activités réalisées"
    )

    blocking_points = fields.Text(
        string="Points bloquants",
        tracking=True
    )

    arbitration_required = fields.Boolean(
        string="Arbitrage DG requis",
        tracking=True
    )

    corrective_actions = fields.Text(
        string="Actions correctives",
        tracking=True
    )

    rejection_reason = fields.Text(
        string="Motif de rejet",
        tracking=True
    )

    # NOUVEAU : % de réalisation global
    global_progress = fields.Float(
        string="% Réalisation global",
        compute="_compute_global_progress",
        store=True,
        help="Pourcentage moyen de réalisation de toutes les activités"
    )

    # --------------------
    # CONTRAINTES SQL
    # --------------------
    
    _sql_constraints = [
        (
            'unique_report_per_week',
            'UNIQUE(department_id, week_start)',
            'Un rapport existe déjà pour ce service et cette semaine.'
        )
    ]

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

    @api.depends("line_ids.progress")
    def _compute_global_progress(self):
        """Calcule le pourcentage moyen de réalisation de toutes les activités"""
        for rec in self:
            if rec.line_ids:
                total_progress = sum(rec.line_ids.mapped('progress'))
                rec.global_progress = total_progress / len(rec.line_ids)
            else:
                rec.global_progress = 0.0

    # --------------------
    # CONTRAINTES
    # --------------------

    @api.constrains('week_start', 'week_end')
    def _check_week_dates(self):
        """Vérifie que la date de fin est postérieure à la date de début"""
        for rec in self:
            if rec.week_start and rec.week_end:
                if rec.week_end < rec.week_start:
                    raise ValidationError("La date de fin doit être postérieure à la date de début.")

    # --------------------
    # ACTIONS
    # --------------------

    def action_submit(self):
        """Soumettre le rapport pour validation"""
        for rec in self:
            # Validation : au moins une activité
            if not rec.line_ids:
                raise UserError("Vous devez renseigner au moins une activité.")
            
            # Validation : vérifier que les activités sont dans la période
            for line in rec.line_ids:
                if line.date_start and (line.date_start < rec.week_start or line.date_start > rec.week_end):
                    raise UserError(
                        f"L'activité '{line.name}' a une date de début ({line.date_start}) "
                        f"hors de la période du rapport ({rec.week_start} - {rec.week_end})."
                    )
            
            # Changement d'état
            rec.state = "submitted"
            
            # Message dans le chatter
            rec.message_post(
                body=f"Rapport soumis pour validation par {self.env.user.name}.",
                subject="Rapport soumis"
            )

    def action_validate(self):
        """Valider le rapport"""
        for rec in self:
            rec.state = "validated"
            rec.message_post(
                body=f"Rapport validé par {self.env.user.name}.",
                subject="Rapport validé",
                message_type='notification'
            )

    def action_reject(self):
        """Rejeter le rapport"""
        for rec in self:
            rec.state = "rejected"
            
            reason = rec.rejection_reason or "Aucune raison spécifiée"
            rec.message_post(
                body=f"Rapport rejeté par {self.env.user.name}.<br/>Motif : {reason}",
                subject="Rapport rejeté",
                message_type='notification'
            )

    def action_back_to_draft(self):
        """Repasser le rapport en brouillon après un rejet"""
        for rec in self:
            if rec.state != "rejected":
                raise UserError("Seuls les rapports rejetés peuvent être remis en brouillon.")
            
            rec.state = "draft"
            rec.message_post(
                body="Rapport remis en brouillon pour correction.",
                subject="Retour en brouillon"
            )

    def action_open_reject_wizard(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'activity.report.reject.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_report_id': self.id},
        }