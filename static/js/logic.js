
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


var getUrlParameter = function getUrlParameter(sParam) {
    // http://stackoverflow.com/questions/19491336/get-url-parameter-jquery
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


$( function(){

    $('.no_follow').click( function(event) {
        event.preventDefault();
        event.stopPropagation();
    });

    $('table.checkboxes tr:not(:first)').click(function(event) {
    // улучшитель юзабилити таблиц, при клике по строке выбрается чекбокс    
        if (event.target.type !== 'checkbox') {
            $(':checkbox', this).trigger('click');
        }
    });

    $('.add_items').click( function(e) {
        /* Выполняем проверку на принадлежность орг. юниту*/
        /*var user_ou = $('.user_ou').text();
        if (user_ou.length == 0) {
            $('.error_msg').css('display', 'block');
            $('.error_msg').text('Не определена принадлежность пользователя организации!');
            e.preventDefault(); // отменяем переход по ссылке
            setTimeout(function() { $('.error_msg').css('display', 'none'); }, 15000);
        } else {
            window.location.href = '/add_items/';
        } */
        var cart_name = $('#id_cartName option:selected').val();
        var docum     = $('#id_doc option:selected').val();        
        var cont      = parseInt($('#id_cartCount').val());        
        if (!cart_name) {
            $('.cart_name_error').show();
        } else {
            $('.cart_name_error').hide();
        }  // cart_count_error

        if (!cont) {
            $('.cart_count_error').show();
        } else {
            $('.cart_count_error').hide();
        }  

        if (cart_name && cont) {
            $.ajax({
                method: 'POST',
                url: '/api/ajax_add_session_items/',
                data:  {'cartName': cart_name, 'doc': docum, 'cartCount': cont },
                beforeSend: function( xhr, settings ){
                    $('.spinner').css('display', 'inline');
                    csrftoken = getCookie('csrftoken');
                    if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                        xhr.setRequestHeader('X-CSRFToken', csrftoken);
                    }
                },
                success: function( msg ) {
                    $('.spinner').css('display', 'none');
                    $('.session_data').html(msg.html);
                    $('.success_msg').show();
                    $('.success_msg').html(msg.mes);
                    setTimeout(function() { $('.success_msg').hide(); }, 12000);

                },
                error: function() {
                    $('.error_msg').show();
                    $('.error_msg').html('Server error :(');
                    $('.spinner').css('display', 'none');
                    setTimeout(function() { $('.error_msg').hide(); }, 12000);
                },
            });            
        }


    });

    $('.clear_session').click( function() {
        $.ajax({
            method: 'POST',
            url: '/api/clear_session/',
            data:  {'tst': 'tst'},
            beforeSend: function( xhr, settings ){
                $('.spinner').css('display', 'inline');
                csrftoken = getCookie('csrftoken');
                if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader('X-CSRFToken', csrftoken);
                }
            },
            success: function( msg ) {
                $('.spinner').css('display', 'none');
                $('.session_data').html('');
                $('.ajax_messages').show();
                $('.success_msg').html(msg.mes);

            },
            error: function() {
                $('.ajax_messages').show();
                $('.success_msg').html('Server error :(');
                $('.spinner').css('display', 'none');
            },
        });
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
            var loc = '/transfer_to_firm/?select=' + get_path + '&back=' + window.location.pathname;
            window.location.href = loc;
        }

    });

    $('.back').click( function() {
        var loc = getUrlParameter('back')
        window.location.href = loc;
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
                    window.location.href = '/events/view_cartridge_events/?id=' + cart_id + '&back=' + window.location.pathname;
                    break;
                case 'edit':
                    window.location.href = '/edit_cartridge_comment/?id=' + cart_id + '&back=' + window.location.pathname;
                    break;
                case 'view_delivery':
                    var doc_id =  mainSelect.find(":selected").attr('data');
                    window.location.href = '/docs/delivery/?show=' + doc_id;
                    break;
                default:

            }
        });
    });

    $('.events_see_more').click( function( event ) {
        event.preventDefault();
        event.stopPropagation();
        var button_next = $(this);
        $.ajax({
            method: 'POST',
            url: '/events/api/show_event_page/',
            data:  {next_page: button_next.attr('next_page')},
            beforeSend: function( xhr, settings ){
                $('.spinner').css('display', 'inline');
                csrftoken = getCookie('csrftoken');
                if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader('X-CSRFToken', csrftoken);
                }
            }  
        }).done(function( msg ) {
            $('.spinner').css('display', 'none');
            if (msg.stop_pagination === '0') {
                $('.all_events_view tr:last').after(msg.html_content);
                var next_page = button_next.attr('next_page');
                next_page = parseInt(next_page,10);
                next_page += 1;
                button_next.attr({'next_page': next_page});
            } else {
                $('.events_see_more').remove();                
            }
        });
    });

    $('.edit_doc').click( function() {
        // редактируем документ
        var selected = $('.checkboxes input:checked').attr('value');
        if ( selected ) {
            var get_doc_id = selected;
            var loc = window.location.pathname + '?select=' + get_doc_id;
            window.location.href = loc;
        }
    });

    $('.cansel_doc').click( function() {
        // отмена произведенных изменений
        var loc = window.location.pathname;
        window.location.href = loc;
    });

    $('.delete_doc').click( function() {
        var selected = $('.checkboxes input:checked').attr('value');
        if ( selected ) {
            var ansver = window.confirm('Вы уверены в том, что хотите удалить документ?');
            if ( ansver ) {
                var loc = window.location.pathname;
                window.location.href = '?delete=' + selected ;
            }
        }

    });

    $('.all_filled input').click( function() {
        // выбор колонки с заправками и очистками
        var select_checkboxes = $('.filled');
        if ( $('.all_filled input').prop('checked') ) {
            select_checkboxes.each(function() {
                $(this).prop('checked', true);
            })
        } else {
            select_checkboxes.each(function() {
                $(this).prop('checked', false);
            })
        }    
    });

    $('.all_fotoreceptor input').click( function() {
        // выбор колонки с фоторецепторами
        var select_checkboxes = $('.fotoreceptor');
        if ( $('.all_fotoreceptor input').prop('checked') ) {
            select_checkboxes.each(function() {
                $(this).prop('checked', true);
            })
        } else {
            select_checkboxes.each(function() {
                $(this).prop('checked', false);
            })
        }    
    });

    $('.all_rakel input').click( function() {
        // выбор колонки с ракелями
        var select_checkboxes = $('.rakel');
        if ( $('.all_rakel input').prop('checked') ) {
            select_checkboxes.each(function() {
                $(this).prop('checked', true);
            })
        } else {
            select_checkboxes.each(function() {
                $(this).prop('checked', false);
            })
        }    
    });

    $('.all_chip input').click( function() {
        // выбор колонки с чипами
        var select_checkboxes = $('.chip');
        if ( $('.all_chip input').prop('checked') ) {
            select_checkboxes.each(function() {
                $(this).prop('checked', true);
            })
        } else {
            select_checkboxes.each(function() {
                $(this).prop('checked', false);
            })
        }    
    });

    $('.all_magnit input').click( function() {
        // выбор колонки с чипами
        var select_checkboxes = $('.magnit');
        if ( $('.all_magnit input').prop('checked') ) {
            select_checkboxes.each(function() {
                $(this).prop('checked', true);
            })
        } else {
            select_checkboxes.each(function() {
                $(this).prop('checked', false);
            })
        }    
    });

});