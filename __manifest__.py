{
    "name": "Rapport d’activité",
    "version": "18.0.1.0.0",
    "category": "Operations / Reporting",
    "summary": "Gestion des rapports d’activité hebdomadaires par service et direction",
    "description": """
Module Odoo permettant aux chefs de service de saisir leurs rapports d’activité
hebdomadaires, avec suivi des activités, workflow de validation, visibilité
hiérarchique par direction et tableaux de bord pour la Direction Générale.

Fonctionnalités clés :
- Rapport hebdomadaire par service
- Suivi détaillé des activités (dates, statut, priorité, % réalisation)
- Workflow : brouillon → soumis → validé / rejeté
- Hiérarchie Direction / Service via hr.department
- Accès par profil : Chef de service, Directeur, DG
- Notifications et historique via chatter
- Compatible Odoo Enterprise 18.0 / Odoo SH
    """,
    "author": "Djogona Mahamat Belna",
    "website": "https://www.codalec-gabon.com",
    "license": "LGPL-3",
    "depends": [
        "base",
        "mail",
        "hr",
    ],
    "data": [
        # Sécurité
        "security/activity_report_groups.xml",
        "security/ir.model.access.csv",
        "security/activity_report_rules.xml",

        # Vues
        "views/activity_report_views.xml",
        "views/activity_report_menu.xml",
        #"views/activity_report_line_views.xml",

        # (à venir)
        # "data/mail_templates.xml",
        # "data/cron_reminder.xml",
    ],
    "application": True,
    "installable": True,
    "auto_install": False,
}
