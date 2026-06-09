from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class BettingCenterCensus(models.Model):
    _name = 'betting.center.census'
    _description = 'Betting Center Census (IOBPAS)'
    _rec_name = 'census_code'
    _order = 'create_date desc'

    # =================================================================
    # I. SUBJECT DATA (APPLICANT)
    # =================================================================
    person_type = fields.Selection([
        ('natural', 'Natural'),
        ('legal', 'Legal')
    ], string='Person Type', required=True, default='natural')

    # A. Natural Person
    full_name = fields.Char(string='Full Name')
    identity_card = fields.Char(string='Identity Card')
    rif_natural = fields.Char(string='R.I.F. (Valid)')
    marital_status = fields.Selection([
        ('single', 'Single'),
        ('married', 'Married'),
        ('divorced', 'Divorced'),
        ('widowed', 'Widowed')
    ], string='Marital Status')
    nationality = fields.Char(string='Nationality')

    # B. Legal Person
    business_name = fields.Char(string='Business Name')
    rif_legal = fields.Char(string='Legal R.I.F.')
    registry_number = fields.Char(string='Mercantile Registry No.')
    social_objective = fields.Text(
        string='Social Objective',
        help='Must be exclusive to lottery game exploitation'
    )
    legal_representative = fields.Char(string='Legal Representative')
    rep_identity_card = fields.Char(string='Representative ID')

    # =================================================================
    # II. ESTABLISHMENT DATA (BETTING CENTER)
    # =================================================================
    commercial_name = fields.Char(string='Commercial Name', required=True)
    address = fields.Text(string='Exact Address', required=True)
    municipality = fields.Char(string='Municipality')
    parish = fields.Char(string='Parish')
    municipal_license = fields.Char(string='Municipal License No.')
    phone = fields.Char(string='Phone Number')
    email = fields.Char(string='Email')

    # =================================================================
    # III. OPERATIONAL AND TECHNICAL INFORMATION
    # =================================================================
    commercial_partner = fields.Char(string='Commercial Partner')
    betting_software = fields.Char(string='Software Used')
    terminal_count = fields.Integer(string='Number of Terminals')

    # Games
    game_animalitos = fields.Boolean(string='Animalitos')
    game_traditional_lottery = fields.Boolean(string='Traditional Lottery')
    game_others = fields.Char(string='Others')

    # =================================================================
    # IV. REQUIREMENTS (PDF ATTACHMENTS)
    # =================================================================
    req_id_rif = fields.Binary(string='ID & RIF Copy', attachment=True)
    req_bank_cert = fields.Binary(string='Bank Certification', attachment=True)
    req_funds_declaration = fields.Binary(string='Lawful Origin of Funds', attachment=True)
    req_property_doc = fields.Binary(string='Property/Lease Agreement', attachment=True)
    req_contract_partner = fields.Binary(string='Partner Contract', attachment=True)

    # Additional Legal
    req_charter_doc = fields.Binary(string='Constitutive Document', attachment=True)
    req_shareholders = fields.Binary(string='Shareholder List', attachment=True)
    req_tax_declaration = fields.Binary(string='Last Tax Declaration', attachment=True)
    req_bank_cert_legal = fields.Binary(string='Legal Bank Certification', attachment=True)

    # =================================================================
    # V. PAYMENT CONSTANCY
    # =================================================================
    payment_reference = fields.Char(string='Reference Number')
    payment_date = fields.Date(string='Payment Date')
    payment_amount = fields.Monetary(string='Amount', currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)

    # =================================================================
    # VI. DECLARATION AND SIGNATURE
    # =================================================================
    sworn_declaration = fields.Boolean(string='Sworn Declaration Accepted')
    signature = fields.Binary(string='Applicant Signature', attachment=True)

    # =================================================================
    # INTERNAL USE
    # =================================================================
    census_code = fields.Char(string='Census Code', readonly=True, copy=False, default='New')
    reception_date = fields.Date(string='Reception Date', default=fields.Date.context_today, readonly=True)
    receiver_user_id = fields.Many2one('res.users', string='Receiver', default=lambda self: self.env.user, readonly=True)
    user_id = fields.Many2one('res.users', string='Linked Odoo User', readonly=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('review', 'Under Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], string='Status', default='draft', tracking=True)

    @api.model
    def create(self, vals):
        if vals.get('census_code', 'New') == 'New':
            vals['census_code'] = self.env['ir.sequence'].next_by_code('betting.center.census.seq') or 'New'
        return super(BettingCenterCensus, self).create(vals)

    def action_approve_and_create_user(self):
        self.ensure_one()
        if self.state != 'review':
            return False

        if not self.email:
            raise ValidationError(_("A valid email is required to create a user."))

        login = self.rif_natural if self.person_type == 'natural' else self.rif_legal
        name = self.full_name if self.person_type == 'natural' else self.legal_representative
        
        existing_user = self.env['res.users'].sudo().search([('login', '=', login)], limit=1)
        
        if existing_user:
            user = existing_user
        else:
            user = self.env['res.users'].sudo().create({
                'name': name,
                'login': login,
                'email': self.email,
                'groups_id': [(6, 0, [self.env.ref('base.group_portal').id])]
            })
            user.sudo().action_reset_password()

        self.write({'state': 'approved', 'user_id': user.id})
        return True

    def action_reject(self):
        self.ensure_one()
        self.write({'state': 'rejected'})