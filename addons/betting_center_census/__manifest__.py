# -*- coding: utf-8 -*-
{
    'name': "Betting Center Census",

    'summary': "Manage and homologate betting centers census",

    'description': """
        Module to register, control, and approve betting centers (IOBPAS).
        Includes web portal integration for requirements upload and 
        automatic Odoo user generation upon approval.
    """,

    'author': "My Company",
    'website': "https://www.yourcompany.com",

    'category': 'Administration',
    'version': '1.0.0',

    # Dependencies
    'depends': ['base', 'website', 'portal', 'auth_signup'],

    # Data files
    'data': [
        'security/ir.model.access.csv',
        'views/betting_center_census_views.xml',
        'views/betting_center_templates.xml',
        'views/betting_center_census_home_views.xml',
        'views/ir_menu_views.xml',
    ],

    'assets': {
        'web.assets_frontend': [
            'betting_center_census/static/src/scss/modal.scss',
            'betting_center_census/static/src/js/modal_loader.js',
        ],
    },

    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}