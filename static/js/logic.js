
function getCookie(name) {
    /* https://docs.djangoproject.com/en/1.8/ref/csrf/ */
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}


$( function(){
    $('.add_items').click( function(e) {
        /* Выполняем проверку на принадлежность орг. юниту*/
        var user_ou = $('.user_ou').text();
        if (user_ou.length == 0) {
            $('.error_msg').css('display', 'block');
            $('.error_msg').text('Не определена принадлежность пользователя организации!');
            e.preventDefault(); // отменяем переход по ссылке
            setTimeout(function() { $('.error_msg').css('display', 'none'); }, 15000);
        } else {
            window.location.href = '/add_items/';
        }

    });

    $('.tr_for_use').click( function() {
        var selected = [];
        $('.checkboxes input:checked').each(function() {
            if ($(this).attr('value')) {
                selected.push( $(this).attr('value') );
            }
        });

        if ( selected.length !== 0 ) {
            var get_path = selected.join('s')
            var loc = '/transfe_for_use/?select=' + get_path;
            window.location.href = loc;
        }
        //console.log(JSON.stringify(selected));

    }); 

    $('.tr_to_recycle_bin').click( function() {
        var selected = [];
        $('.checkboxes input:checked').each(function() {
            if ($(this).attr('value')) {
                selected.push( $(this).attr('value') );
            }
        });

        if ( selected.length !== 0 ) {
            var get_path = selected.join('s')
            var loc = '/transfe_to_basket/?select=' + get_path + '&atype=5';
            window.location.href = loc;
        }
    });

    $('.tr_empty_to_recycle_bin').click( function() {
        var selected = [];
        $('.checkboxes input:checked').each(function() {
            if ($(this).attr('value')) {
                selected.push( $(this).attr('value') );
            }
        });

        if ( selected.length !== 0 ) {
            var get_path = selected.join('s')
            var loc = '/transfe_to_basket/?select=' + get_path + '&atype=6';
            window.location.href = loc;
        }
    });



    $('.turf').click( function() {
        var selected = [];
        $('.checkboxes input:checked').each(function() {
            if ($(this).attr('value')) {
                selected.push( $(this).attr('value') );
            }
        });

        if ( selected.length !== 0 ) {
            $.ajax({
                method: 'POST',
                url: '/api/turf_cartridge/',
                data:  {len: selected.length , 'selected[]': selected},
                beforeSend: function( xhr, settings ){
                    $('.spinner').css('display', 'inline');
                    csrftoken = getCookie('csrftoken');
                    if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                        xhr.setRequestHeader('X-CSRFToken', csrftoken);
                    }
                }  
            }).done(function( msg ) {
                $('.spinner').css('display', 'none');
                window.location.href = '/basket/';
            });
        }
    });


    $('.tr_to_stock').click( function() {
        var selected = [];
        $('.checkboxes input:checked').each(function() {
            if ($(this).attr('value')) {
                selected.push( $(this).attr('value') );    
            }
        });

        if ( selected.length !== 0 ) {
            var get_path = selected.join('s')
            var loc = '/transfer_to_stock/?select=' + get_path;
            window.location.href = loc;
        }
    });

    $('.from_firm_to_stock').click( function() {
        var selected = [];
        $('.checkboxes input:checked').each(function() {
            if ($(this).attr('value')) {
                selected.push( $(this).attr('value') );    
            }
        });

        if ( selected.length !== 0 ) {
            var get_path = selected.join('s')
            var loc = '/from_firm_to_stock/?select=' + get_path;
            window.location.href = loc;
        }

    });

    $('.from_basket_to_stock').click( function() {
        var selected = [];
        $('.checkboxes input:checked').each(function() {
            if ($(this).attr('value')) {
                selected.push( $(this).attr('value') );    
            }
        });

        if ( selected.length !== 0 ) {
            var get_path = selected.join('s')
            var loc = '/from_basket_to_stock/?select=' + get_path;
            window.location.href = loc;
        }

    });

    $('.tr_to_firm').click( function() {
        var selected = [];
        $('.checkboxes input:checked').each(function() {
            if ($(this).attr('value')) {
                selected.push( $(this).attr('value') );    
            }
        });

        if ( selected.length !== 0 ) {
            var get_path = selected.join('s')
            var loc = '/transfer_to_firm/?select=' + get_path;
            window.location.href = loc;
        }

    });

    $('.edit_firm').click( function() {
        var selected = [];
        $('.checkboxes input:checked').each(function() {
            selected.push( $(this).attr('value') );
        });


        if ( selected.length !== 0 ) {
            var get_path = selected.join('s')
            var loc = '/edit_firm/?select=' + get_path;
            window.location.href = loc;
        }

    });

    $('.del_firm').click( function() {
        var selected = [];
        $('.checkboxes input:checked').each(function() {
            selected.push( $(this).attr('value') );
        });

        if ( selected.length !== 0 ) {
            var get_path = selected.join('s')
            var loc = '/del_firm/?select=' + get_path;
            window.location.href = loc;
        }

    });

    $('.del_node').click( function() {
        var selected = [];
        $('.checkboxes input:checked').each(function() {
            selected.push( $(this).attr('value') );
        });

        if ( selected.length !== 0 ) {
            $.ajax({
                method: 'POST',
                url: '/api/del_node/',
                data:  {len: selected.length , 'selected[]': selected},
                beforeSend: function( xhr, settings ){
                    $('.spinner').css('display', 'inline');
                    csrftoken = getCookie('csrftoken');
                    if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                        xhr.setRequestHeader('X-CSRFToken', csrftoken);
                    }
                }  
            }).done(function( msg ) {
                $('.spinner').css('display', 'none');

                window.location.href = '/tree_list/';
                //alert( 'Data Saved: ' + msg );
            });
            
        }

    });

    $('.edit_user').click( function() {
        var selected = [];
        $('.checkboxes input:checked').each(function() {
            selected.push( $(this).attr('value') );
        });

        if (selected.length == 1) {
            window.location.href = '/manage_users/edit_user/?id=' + selected[0];
        }
    });


    var getUrlParameter = function getUrlParameter(sParam) {
        /*
        http://stackoverflow.com/questions/19491336/get-url-parameter-jquery
         */
        var sPageURL = decodeURIComponent(window.location.search.substring(1)),
            sURLVariables = sPageURL.split('&'),
            sParameterName,
            i;

        for (i = 0; i < sURLVariables.length; i++) {
            sParameterName = sURLVariables[i].split('=');

            if (sParameterName[0] === sParam) {
                return sParameterName[1] === undefined ? true : sParameterName[1];
            }
        }
    };

    $('.city_selector').change(function() {
        var loc = '';
        var page = ''
        var page_num = getUrlParameter('page');

        if (page_num) {
            page = '&page=' + page_num;
        };

        if ($(this).val()) {
            loc = '/toner_refill/?city=' + $(this).val() + page;
        } else {
            loc = '/toner_refill/';
        }
        window.location.href = loc;

    });

    /* выбор всех чекбоксов при нажатии на чекбокс классом  */
    $('.check_all').click( function() {
        var select_checkboxes = $('.checkboxes .checkbox');
        if ( $('.check_all').prop('checked') ) {
            select_checkboxes.each(function() {
                $(this).prop('checked', true);
            })
        } else {
            select_checkboxes.each(function() {
                $(this).prop('checked', false);
            })
        }
    
    });

    /* Действие над строкой в таблице (редактирование, просмотр) */
    $('.cartridge_action').each( function() {
        var mainSelect = $(this);
        mainSelect.bind('change', function() {
            var cart_id = mainSelect.attr('data');
            var cart_action = mainSelect.children(':selected').attr('value');
            switch (cart_action) {
                case 'view_events':
                    window.location.href = '/events/view_cartridge_events/?id=' + cart_id;
                    break;
                case 'edit':
                    window.location.href = '/edit_cartridge_comment/?id=' + cart_id;
                    break;
                default:

            }
        });
    });

});