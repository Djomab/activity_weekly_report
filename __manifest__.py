{
    "name": "Rapport d'activité",
    "version": "18.0.1.0.0",
    "category": "Operations / Reporting",
    "summary": "Gestion des rapports d'activité hebdomadaires par service et direction",
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
        "security/activity_report_rules.xml",
        
        # Vues
        "views/activity_report_views.xml",
        "views/activity_report_menu.xml",
        "views/activity_report_line_views.xml",
        "wizards/activity_report_reject_wizard_views.xml",
        
        # DROITS D'ACCÈS
        "security/ir.model.access.csv",

        # MAIL
        # "data/mail_templates.xml",
        # "data/cron_reminder.xml",
    ],

    "application": True,
    "installable": True,
    "auto_install": False,
}