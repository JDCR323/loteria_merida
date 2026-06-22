import base64
from odoo import http
from odoo.http import request

class CensusWebsiteController(http.Controller):

    @http.route(['/census/register'], type='http', auth="public", website=True, csrf=True)
    def census_register_form(self, **post):
        if not post:
            return request.render('betting_center_census.template_register_census', {})

        vals = {
            'person_type': post.get('person_type', 'natural'),
            'commercial_name': post.get('commercial_name'),
            'address': post.get('address'),
            'municipality': post.get('municipality'),
            'parish': post.get('parish'),
            'municipal_license': post.get('municipal_license'),
            'phone': post.get('phone'),
            'email': post.get('email'),
            
            'commercializer': post.get('commercializer'),
            'software': post.get('software'),
            'terminals_count': int(post.get('terminals_count', 0)) if post.get('terminals_count') else 0,
            
            'game_animalitos': True if post.get('game_animalitos') else False,
            'game_traditional': True if post.get('game_traditional') else False,
            'game_other_check': True if post.get('game_other_check') else False,
            'game_other_text': post.get('game_other_text'),
            
            'payment_reference': post.get('payment_reference'),
            'payment_date': post.get('payment_date') or False,
            'payment_amount': float(post.get('payment_amount', 0.0)) if post.get('payment_amount') else 0.0,
            
            'sworn_declaration': True if post.get('sworn_declaration') else False,
            'state': 'review',
        }

        if vals['person_type'] == 'natural':
            vals.update({
                'full_name': post.get('full_name'),
                'identity_card': post.get('identity_card'),
                'rif_natural': post.get('rif_natural'),
                'civil_status': post.get('civil_status'),
                'nationality': post.get('nationality'),
            })
        else:
            vals.update({
                'business_name': post.get('business_name'),
                'rif_legal': post.get('rif_legal'),
                'registry_number': post.get('registry_number'),
                'social_objective': post.get('social_objective'),
                'legal_representative': post.get('legal_representative'),
                'rep_identity_card': post.get('rep_identity_card'),
            })

        attachments = [
            'req_id_rif', 'req_funds_origin', 'req_property', 'req_conalot',
            'req_photos', 'req_charter', 'req_shareholders', 'req_islr',
            'req_economic_license', 'req_mercantile_registry'
        ]
        
        for key in attachments:
            file_data = post.get(key)
            if file_data and hasattr(file_data, 'filename') and file_data.filename:
                vals[key] = base64.b64encode(file_data.read())

        new_record = request.env['betting.center.census'].sudo().create(vals)

        return request.render('betting_center_census.template_register_success', {
            'census_code': new_record.census_code
        })