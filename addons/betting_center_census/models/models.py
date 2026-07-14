from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class BettingCenterCensus(models.Model):
    _name = 'betting.center.census'
    _description = 'Registro de Centros de Apuestas (IOBPAS)'
    _rec_name = 'census_code'
    _order = 'create_date desc'


    person_type = fields.Selection([
        ('natural', 'Natural'),
        ('legal', 'Jurídica')
    ], string='Tipo de Persona', required=True, default='natural')

    full_name = fields.Char(string='Nombres y Apellidos')
    identity_card = fields.Char(string='Cédula de Identidad')
    rif_natural = fields.Char(string='R.I.F. (Vigente)')
    civil_status = fields.Selection([
        ('soltero', 'Soltero(a)'),
        ('casado', 'Casado(a)'),
        ('divorciado', 'Divorciado(a)'),
        ('viudo', 'Viudo(a)')
    ], string='Estado Civil')
    nationality = fields.Char(string='Nacionalidad')

    business_name = fields.Char(string='Razón Social')
    rif_legal = fields.Char(string='R.I.F. Jurídico')
    registry_number = fields.Char(string='Nº Registro Mercantil')
    social_objective = fields.Text(string='Objeto Social')
    legal_representative = fields.Char(string='Representante Legal')
    rep_identity_card = fields.Char(string='Cédula del Representante')


    commercial_name = fields.Char(string='Nombre Comercial', required=True)
    address = fields.Text(string='Dirección Exacta', required=True)
    municipality = fields.Char(string='Municipio')
    parish = fields.Char(string='Parroquia')
    municipal_license = fields.Char(string='N° Licencia Municipal')
    phone = fields.Char(string='Teléfono / Celular')
    email = fields.Char(string='Correo Electrónico')


    commercializer = fields.Char(string='Comercializadora')
    software = fields.Char(string='Software de Apuestas')
    terminals_count = fields.Integer(string='N° de Terminales')

    game_animalitos = fields.Boolean(string='Animalitos')
    game_traditional = fields.Boolean(string='Lotería Tradicional')
    game_other_check = fields.Boolean(string='Comercializa Otros')
    game_other_text = fields.Char(string='Especificación de Otros')


    req_id_rif = fields.Binary(string='1. Cédula y RIF', attachment=True)
    req_funds_origin = fields.Binary(string='2. Origen Lícito de Fondos', attachment=True)
    req_property = fields.Binary(string='3. Propiedad/Arrendamiento', attachment=True)
    req_conalot = fields.Binary(string='4. Aval CONALOT', attachment=True)
    req_photos = fields.Binary(string='5. Fotos del Local', attachment=True)
    req_charter = fields.Binary(string='6. Documento Constitutivo', attachment=True)
    req_shareholders = fields.Binary(string='7. Relación de Accionistas', attachment=True)
    req_islr = fields.Binary(string='8. Declaración ISLR', attachment=True)
    req_economic_license = fields.Binary(string='9. Licencia Actividades Económicas', attachment=True)
    req_mercantile_registry = fields.Binary(string='10. Registro Mercantil', attachment=True)


    payment_reference = fields.Char(string='Referencia de Pago')
    payment_date = fields.Date(string='Fecha de Pago')
    payment_amount = fields.Monetary(string='Monto (Bs.)', currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)

    sworn_declaration = fields.Boolean(string='Declaración Jurada Aceptada')
    
    census_code = fields.Char(string='Código de Registro', readonly=True, copy=False, default='Nuevo')
    reception_date = fields.Date(string='Fecha de Recepción', default=fields.Date.context_today, readonly=True)
    receiver_user_id = fields.Many2one('res.users', string='Funcionario Receptor', default=lambda self: self.env.user, readonly=True)
    user_id = fields.Many2one('res.users', string='Usuario Odoo Vinculado', readonly=True)
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('review', 'En Revisión'),
        ('approved', 'Aprobado'),
        ('rejected', 'Rechazado')
    ], string='Estado', default='draft', tracking=True)

    @api.model
    def create(self, vals):
        if vals.get('census_code', 'Nuevo') == 'Nuevo':
            vals['census_code'] = self.env['ir.sequence'].next_by_code('betting.center.census.seq') or 'Nuevo'
        return super(BettingCenterCensus, self).create(vals)

    def action_approve_and_create_user(self):
        self.ensure_one()
        if self.state != 'review':
            return False

        if not self.email:
            raise ValidationError(_("Se requiere un correo válido para crear el usuario."))

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