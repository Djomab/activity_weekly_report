from odoo import models, fields, api
from odoo.exceptions import UserError
from markupsafe import Markup


class ActivityReportRejectWizard(models.TransientModel):
    _name = "activity.report.reject.wizard"
    _description = "Assistant de rejet de rapport"

    report_id = fields.Many2one(
        "activity.weekly.report",
        string="Rapport",
        required=True,
        readonly=True
    )

    rejection_reason = fields.Text(
        string="Motif du rejet",
        required=True,
    )

    def action_confirm_reject(self):
        """Confirmer le rejet avec le motif"""
        self.ensure_one()

        if not self.rejection_reason:
            raise UserError("Veuillez indiquer un motif de rejet.")

        # Message dans le chatter
        self.report_id.message_post(
            body=Markup(
                "<p><strong>Rapport rejeté par %s</strong></p>"
                "<p><strong>Motif :</strong> %s</p>"
            ) % (self.env.user.name, self.rejection_reason),
            subject="Rapport rejeté",
            message_type='notification',
            subtype_xmlid='mail.mt_note',
        )

        # Rejeter le rapport
        self.report_id.write({'state': 'rejected'})

        return {'type': 'ir.actions.act_window_close'}