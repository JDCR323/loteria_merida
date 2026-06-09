/** @odoo-module ignore **/
    
        setTimeout(function() {
            // Usamos el selector de Bootstrap directamente
            var myModal = document.getElementById('censusModal');
            console.log(myModal);
            myModal.shown()
            sessionStorage.setItem('censusModalShown', 'true');
        }, 2500);
    

