$( function() {
    $('.generate_report').click( function() {
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
                // таймаут на 3 секунды
                setTimeout(function() {}, 3000); 
                console.log(msg.html);
                $('div.ajax-content').html(msg.html);
                //window.location.href = '/basket/';
            });
        }
    
    });


});
