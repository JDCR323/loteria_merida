/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.CensusInvitationModal = publicWidget.Widget.extend({
    selector: '#censusModal',

    start: function () {

        if (document.getElementById('censusModal')) {

            setTimeout(() => {
                document.querySelector('[data-bs-target="#censusModal"]').click();
            }, 1000);
        }
        return this._super.apply(this, arguments);
    },
});
