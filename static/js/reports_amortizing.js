$( function() {
    $('.button').click( function() {
        // получаем значения введенные пользователем
        var org = $('select#id_org option:selected').val();
        var cont = $('.pm_counter').val();

        if ( org && cont ) {
            $.ajax({
                method: 'POST',
                url: '/reports/api/',
                data:  {'type': 'amortizing', 'org': org, 'cont': cont },
                beforeSend: function( xhr, settings ){
                    $('.spinner').css('display', 'inline');
                    csrftoken = getCookie('csrftoken');
                    if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                        xhr.setRequestHeader('X-CSRFToken', csrftoken);
                    }
                }  
            }).done(function( msg ) {
                $('.spinner').css('display', 'none');
                setTimeout(function() {}, 3000);
                console.log(msg);
                //window.location.href = '/basket/';
            });
        }
    
    });


});
