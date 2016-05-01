
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

function pretty_del_table_row(jqrow) {
    return function(show_mes) {
        var i = 0;
        var counter = 0;
        counter = setInterval(function(){ 
            /* Реализум мигание строки в процессе удаления. */
            jqrow.toggleClass('red_bg');
            
            if (i >= 5) {
                clearInterval(counter);
                jqrow.remove();
                show_mes();
            }
            i++;
        }, 500);
    }
}


$( function(){

    // проверям существует ли блок dashboard_events
    // если да, то загружаем аяксом его контент 
    var dashboard_events = $('.dashboard_events');
    if (dashboard_events.length) {
        var time_zone_offset = new Date();
        time_zone_offset = time_zone_offset.getTimezoneOffset() / 60
        time_zone_offset = -1 * time_zone_offset; // меняем знак
        $.ajax({
            method: 'POST',
            url: '/api/view_events/',
            data:  {'time_zone_offset': time_zone_offset, 'detail': 0 },
            beforeSend: function( xhr, settings ){
                csrftoken = getCookie('csrftoken');
                if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader('X-CSRFToken', csrftoken);
                }
            },
            success: function( msg ) {
                $('.dashboard_events').css('background', 'none');
                $('.dashboard_events').html(msg.html);
            },
            error: function() {
                $('.dashboard_events').css('background', 'none');
        
            },
        });
    } 

    var show_all_events = $('.show_all_events');
    if (show_all_events.length) {
        var time_zone_offset = new Date();
        time_zone_offset = time_zone_offset.getTimezoneOffset() / 60
        time_zone_offset = -1 * time_zone_offset; // меняем знак
        $.ajax({
            method: 'POST',
            url: '/events/api/date_filter/',
            data:  {'time_zone_offset': time_zone_offset, 'detail': 1 },
            beforeSend: function( xhr, settings ){
                csrftoken = getCookie('csrftoken');
                if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader('X-CSRFToken', csrftoken);
                }
            },
            success: function( msg ) {
                $('.show_all_events').css('background', 'none');
                $('.show_all_events').html(msg.html);
            },
            error: function() {
                $('.show_all_events').css('background', 'none');
        
            },
        });
    }

    // Просмотр событий для одного картриджа
    var view_cart_events = $('.view_cart_events');
    if (view_cart_events.length) {
        var time_zone_offset = new Date();
        time_zone_offset = time_zone_offset.getTimezoneOffset() / 60
        time_zone_offset = -1 * time_zone_offset; // меняем знак
        cart_id = getUrlParameter('id');
        $.ajax({
            method: 'POST',
            url: '/events/api/view_cart_events/',
            data:  {'time_zone_offset': time_zone_offset, 'detail': 1, 'cart_id': cart_id },
            beforeSend: function( xhr, settings ){
                csrftoken = getCookie('csrftoken');
                if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader('X-CSRFToken', csrftoken);
                }
            },
            success: function( msg ) {
                $('.view_cart_events').css('background', 'none');
                $('.view_cart_events').html(msg.html);
            },
            error: function() {
                $('.view_cart_events').css('background', 'none');
        
            },
        });
    }

    $('.event_filter').click( function() {
        var filter_date = $('form.input_date').serializeArray();
        var start_date  = filter_date[1].value;
        var end_date    = filter_date[2].value;
        var time_zone_offset = new Date();
        time_zone_offset = time_zone_offset.getTimezoneOffset() / 60
        time_zone_offset = -1 * time_zone_offset; // меняем знак
        if (start_date || end_date) {
            $.ajax({
                method: 'POST',
                url: '/events/api/date_filter/',
                data:  {'start_date': start_date, 'end_date': end_date, 'time_zone_offset': time_zone_offset },
                beforeSend: function( xhr, settings ){
                    $('.spinner').show();
                    csrftoken = getCookie('csrftoken');
                    if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                        xhr.setRequestHeader('X-CSRFToken', csrftoken);
                    }
                },
                success: function( msg ) {
                    $('.spinner').hide();
                    $('.show_all_events').css('background', 'none');
                    $('.show_all_events').html(msg.html);
                    if (msg.stop_pagination === '1') {
                        $('.events_see_more').remove();
                    }
                },
                error: function( msg ) {
                    $('.show_all_events').css('background', 'none');
                },
            });    
        }
    });

    $('.no_follow').click( function(event) {
        event.preventDefault();
        event.stopPropagation();
    });

    $('.export_to_csv').click( function() {
        $('.download_doc').attr('href', '#');
        $('.download_doc').hide();
        var view  = $(this).attr('view');
        var gtype = $('.export_type option:selected').val();
        $.ajax({
            method: 'POST',
            url: '/docs/api/generate_csv/',
            data:  {'view': view, 'gtype': gtype },
            beforeSend: function( xhr, settings ){
                $('.export_spinner').show();
                csrftoken = getCookie('csrftoken');
                if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader('X-CSRFToken', csrftoken);
                }
            },
            success: function( msg ) {
                setTimeout(function() { }, 4000);
                $('.export_spinner').hide(); 
                $('.download_doc').attr('href', msg.url);
                $('.download_doc').show();
                var a_href = msg.url;
            },
            error: function() {
                $('.export_spinner').hide();
                $('.error_msg').show();
                $('.error_msg').html('<p>Server not available.</p>');
                setTimeout(function() { $('.error_msg').hide(); }, 12000);
            },
        });
    });

    $('.transfer_to_repair').click( function() {
        var transfer_to_firm = $('form.transfer_to_firm').serializeArray();
        var arg_obj = { 'numbers': transfer_to_firm[1]['value'], 'firm': transfer_to_firm[2]['value'], 'sum': transfer_to_firm[3]['value'], 'doc': transfer_to_firm[4]['value'] };
        $.ajax({
            method: 'POST',
            url: '/api/transfer_to_firm/',
            data:  arg_obj,
            beforeSend: function( xhr, settings ){
                $('.spinner').show();
                csrftoken = getCookie('csrftoken');
                if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader('X-CSRFToken', csrftoken);
                }
            },
            success: function( msg ) {
                $('.spinner').hide();
                if ( msg.success ) {
                    $('.error_msg').hide();
                    $('.success_msg').show().html(msg.success);
                    setTimeout(function() { $('.success_msg').hide(); }, 12000);
                }

                if ( msg.errors ) {
                    $('.success_msg').hide();
                    $('.transfer_to_firm').find('.form_error_text').remove();
                    for (var key in msg.errors) {
                        // Check for proper key in dictionary
                        if (key in {'numbers': 1, 'firm': 1, 'doc': 1, 'price': 1}) {
                            // Читаем сообщение об ошибке
                            error = msg.errors[key][0];
                            field = $('.transfer_to_firm').find('#id_' + key);
                            // Прикрепляем сообщение с ошибкой после поля
                            field.after('<div class="form_error_text" style="display: block;">' + error + '</div>');
                        }
                    }
                }
                
            },
            error: function() {
                $('.spinner').hide();
                $('.success_msg').hide();
                $('.error_msg').html('<p>Server not available.</p>');
                setTimeout(function() { $('.error_msg').hide(); }, 12000);
            },
        });
    });

    $('table.checkboxes tr:not(:first)').click(function(event) {
    // улучшитель юзабилити таблиц, при клике по строке выбирается чекбокс    
        if (event.target.type !== 'checkbox') {
            $(':checkbox', this).trigger('click');
        }

        if (event.target.type !== 'radio') {
            $(':radio', this).trigger('click');
        }

    });

    $('.add_items').click( function(e) {
        /* Выполняем проверку на принадлежность орг. юниту*/
        var cart_name = $('#id_cartName option:selected').val();
        var docum     = $('#id_doc option:selected').val();
        var cont      = parseInt($('#id_cartCount').val());
        var cart_type = $(this).attr('data'); 
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
                data:  {'cartName': cart_name, 'doc': docum, 'cartCount': cont, 'cart_type': cart_type },
                beforeSend: function( xhr, settings ){
                    $('.spinner').css('display', 'inline');
                    csrftoken = getCookie('csrftoken');
                    if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                        xhr.setRequestHeader('X-CSRFToken', csrftoken);
                    }
                },
                success: function( msg ) {
                    // Прячем ссылку закачки pdf файлов
                    $('.download_pdf').hide();

                    if (msg.error == '1') {
                        $('.spinner').hide(); 
                        $('.success_msg').hide();
                        $('.error_msg').show();
                        $('.error_msg').html(msg.mes);
                    }

                    if (msg.error == '0') {
                        $('.spinner').hide();
                        $('.error_msg').hide();
                        $('.session_data').html(msg.html);
                        $('.success_msg').show();
                        $('.success_msg').html(msg.mes);
                        setTimeout(function() { $('.success_msg').hide(); }, 12000);
                    }
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

    $('.users_use_cartridges').click( function() {
        var org        = $('#id_org option:selected').val();
        var start_date = $('#id_start_date').val();
        //console.log(org, diap);
        $.ajax({
            method: 'POST',
            url: '/reports/api/ajax_reports_users/',
            data:  {'org': org, 'start_date': start_date},
            beforeSend: function( xhr, settings ){
                $('.spinner').show();
                csrftoken = getCookie('csrftoken');
                if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader('X-CSRFToken', csrftoken);
                }
            },
            success: function( msg ) {
                $('.spinner').hide(); 
                if (msg.error == '1') {
                    $('.success_msg').hide();
                    $('.error_msg').show();
                    $('.error_msg').html(msg.text);
                    $('.users_result').html();
                }

                if (msg.error == '0') {
                    $('.spinner').hide();
                    $('.error_msg').hide();
                    $('.users_result').html(msg.text);
                }
            },
            error: function() {
                $('.spinner').hide(); 
                $('.success_msg').hide();
                $('.error_msg').show();
                $('.error_msg').html('Server error :(');
            },
        });   

    });

    $('.clear_session').click( function() {
        var cart_type = $(this).attr('data'); 
        $.ajax({
            method: 'POST',
            url: '/api/clear_session/',
            data:  {'cart_type': cart_type},
            beforeSend: function( xhr, settings ){
                $('.spinner_pdf').show();
                csrftoken = getCookie('csrftoken');
                if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader('X-CSRFToken', csrftoken);
                }
            },
            success: function( msg ) {
                $('.spinner_pdf').hide();
                $('.download_pdf').hide();
                $('.session_data').html('');
                $('.ajax_messages').show();
                $('.success_msg').html(msg.mes);
            },
            error: function() {
                $('.ajax_messages').show();
                $('.success_msg').html('Server error :(');
                $('.spinner_pdf').hide();
            },
        });
    });

    $('.generate_pdf').click( function() {
        var cart_type = $(this).attr('data'); 
        $.ajax({
            method: 'POST',
            url: '/docs/api/generate_pdf/',
            data:  {'cart_type': cart_type, 'cart_type': cart_type},
            beforeSend: function( xhr, settings ){
                $('.spinner_pdf').show();
                csrftoken = getCookie('csrftoken');
                if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader('X-CSRFToken', csrftoken);
                }
            },
            success: function( msg ) {
                $('.spinner_pdf').hide();
                if ( msg.url ) {
                    $('.download_pdf').show();
                    $('.download_pdf').attr('href', msg.url)
                }
            },
            error: function() {
                $('.ajax_messages').show();
                $('.success_msg').html('Server error :(');
                $('.spinner_pdf').hide();
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

    $('.edit_cart_name').click(function() {
        /* Редактируем человекочитаемое имя картриджа и его тип. 
        */
        var cbox = $('.checkboxes input:checked');
        var name_id = cbox.val();
        if (name_id) {
            var loc = $(this).attr('href');
            loc = loc + '?id=' + name_id + '&back=' + window.location.pathname; 
            window.location.href = loc;
        }
    });


    $('.tr_to_recycle_bin').click( function() {
        var selected = [];
        var atype    = $(this).attr('atype') 
        $('.checkboxes input:checked').each(function() {
            if ($(this).attr('value')) {
                selected.push( $(this).attr('value') );
            }
        });


        if ( selected.length !== 0 ) {
            var ansver = window.confirm('Вы точно хотите поместить выбранные объекты в корзину?');
            if ( ansver ) {
                $('.spinner').show();
                var tr = $('.checkboxes input:checked').parent().parent().not('.table_header');
                /* мигание красным цветом */
                var freezy_f = pretty_del_table_row(tr);

                $.ajax({
                    method: 'POST',
                    url: '/api/transfer_to_basket/',
                    data:  {'selected': selected, 'atype': atype},
                    beforeSend: function( xhr, settings ){
                        csrftoken = getCookie('csrftoken');
                        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                            xhr.setRequestHeader('X-CSRFToken', csrftoken);
                        }
                    },
                    success: function( msg ) {
                        
                        if (msg.error == '1') {
                            setTimeout(function() { $('.spinner').hide(); }, 2000);
                            $('.success_msg').hide();
                            $('.error_msg').show();
                            $('.error_msg').html(msg.text);
                        }

                        if (msg.error == '0') {
                            setTimeout(function() { $('.spinner').hide(); }, 2000);
                            $('.error_msg').hide();
                            $('.success_msg').hide();
                            freezy_f(function() {
                                $('.success_msg').show();
                                $('.success_msg').html(msg.text);
                            });
                        }

                    },
                    error: function() {
                        $('.spinner').hide();
                        $('.error_msg').show();
                        setTimeout(function() { $('.error_msg').html('<p>Server not available.</p>'); }, 12000);
                    },
                });                
            }

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
            var ansver = window.confirm('Вы точно хотите удалить расходник(и)?');
            var tr = $('.checkboxes input:checked').parent().parent().not('.table_header');
            var freezy_f = pretty_del_table_row(tr);
            if (ansver) {
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
                        $('.spinner').hide();
                        freezy_f(function() {  });
                        /* window.location.href = '/basket/'; */
                });
            }
        }
    });


    $('.tr_to_stock').click( function() {
        var selected = [];
        // выбираем все строки, за исключением заголовочной
        var tr = $('.checkboxes input:checked').parent().parent().not('.table_header');
        $('.checkboxes input:checked').each(function() {
            if ($(this).attr('value')) {
                selected.push( $(this).attr('value') );    
            }
        });

        if ( selected.length !== 0 ) {
            var ansver = window.confirm('Вы точно хотите вернуть выбранные объекты обратно на склад?');
            if ( ansver ) {
                // если пользователь ответил Да, то запускаем аякс запрос
                $.ajax({
                    method: 'POST',
                    url: '/api/transfer_to_stock/',
                    data:  {'selected': selected},
                    beforeSend: function( xhr, settings ){
                        $('.spinner').show();
                        csrftoken = getCookie('csrftoken');
                        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                            xhr.setRequestHeader('X-CSRFToken', csrftoken);
                        }
                    },
                    success: function( msg ) {
                        if (msg.error == '0') {
                            setTimeout(function() { 
                                $('.spinner').hide(); 
                                $('.error_msg').hide();
                                $('.success_msg').show();
                                $('.success_msg').html(msg.text);
                                tr.hide();
                            }, 4000);
                        }
                    },
                    error: function() {
                        $('.spinner').hide();
                        $('.error_msg').show();
                        setTimeout(function() { $('.error_msg').html('<p>Server not available.</p>'); }, 12000);
                    },
                });
            }
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
        var selected = $('.checkboxes input:checked').attr('value');
        if ( selected ) {
            var ansver = window.confirm('Вы точно хотите удалить контрагента?');
            var tr = $('.checkboxes input:checked').parent().parent();
            var freezy_f = pretty_del_table_row(tr);
            if ( ansver ) {
                $.ajax({
                    method: 'POST',
                    url: '/api/del_firm/',
                    data:  {'selected': selected},
                    beforeSend: function( xhr, settings ){
                        $('.spinner').css('display', 'inline');
                        csrftoken = getCookie('csrftoken');
                        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                            xhr.setRequestHeader('X-CSRFToken', csrftoken);
                        }
                    },
                    success: function( msg ) {
                        
                        if (msg.error == '1') {
                            setTimeout(function() { }, 4000);
                            $('.spinner').hide(); 
                            $('.success_msg').hide();
                            $('.error_msg').show();
                            $('.error_msg').html(msg.text);
                        }

                        if (msg.error == '0') {
                            $('.spinner').hide();
                            $('.error_msg').hide();
                            freezy_f(function() {
                                $('.success_msg').show();
                                $('.success_msg').html(msg.text);
                            });
                        }

                    },
                    error: function() {
                        $('.spinner').hide();
                        $('.error_msg').show();
                        setTimeout(function() { $('.error_msg').html('<p>Server not available.</p>'); }, 12000);
                    },
                });
            }
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
                data:  {'selected[]': selected},
                beforeSend: function( xhr, settings ){
                    $('.spinner').css('display', 'inline');
                    csrftoken = getCookie('csrftoken');
                    if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                        xhr.setRequestHeader('X-CSRFToken', csrftoken);
                    }
                }, 
                success: function( msg ) {
                    var tr = $('.checkboxes input:checked').parent().parent();
                    if (msg.error == '1') {
                        setTimeout(function() { }, 4000);
                        $('.spinner').hide(); 
                        $('.success_msg').hide();
                        $('.error_msg').show();
                        $('.error_msg').html(msg.text);
                    }

                    if (msg.error == '0') {
                        setTimeout(function() { tr.remove(); }, 4000);
                        $('.spinner').hide();
                        $('.error_msg').hide();
                        $('.success_msg').show();
                        $('.success_msg').html(msg.text);
                    }

                },
                error: function() {
                        $('.spinner').hide();
                        $('.error_msg').show();
                        $('.success_msg').hide();
                        $('.error_msg').html('<p>Server not available.</p>');
                        setTimeout(function() { $('.error_msg').hide(); }, 12000);
                },
            });
        }
    });


    $('.edit_user').click( function() {
        var uid = $('.checkboxes input:checked').attr('value');
        window.location.href = '/manage_users/edit_user/?id=' + uid;
        return false;
    });


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

    /* Действие над строкой в таблице с картриджами (редактирование, просмотр) */
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
                case 'view_delivery':
                    var doc_id =  mainSelect.find(":selected").attr('data');
                    window.location.href = '/docs/delivery/?show=' + doc_id;
                    break;
                default:

            }
        });
    });

    /*  Действия для генерации docx файлов актов  */
    $('.docx_action').each( function() {
        var mainSelect = $(this);
        mainSelect.bind('change', function() {
            var doc_id = mainSelect.attr('data');
            $('.download_doc').hide();
            var doc_action = mainSelect.children(':selected').attr('value');
            if (doc_action) {
                $.ajax({
                    method: 'POST',
                    url: '/docs/api/generate_act/',
                    data:  {'doc_id': doc_id, 'doc_action': doc_action },
                    beforeSend: function( xhr, settings ){
                        $('.spinner').show();
                        csrftoken = getCookie('csrftoken');
                        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                            xhr.setRequestHeader('X-CSRFToken', csrftoken);
                        }
                    },
                    success: function( msg ) {
                        if (msg.error == '0') {
                            $('.spinner').hide(); 
                            $('.error_msg').hide();
                            $('.success_msg').show();
                            $('.success_msg').html(msg.text);
                            $('.download_doc').attr('href', msg.url);
                            $('.download_doc').show();
                            setTimeout(function() { $('.success_msg').hide(); }, 12000);
                        } 

                    },
                    error: function() {
                        $('.spinner').hide();
                        $('.error_msg').show();
                        setTimeout(function() { $('.error_msg').html('<p>Server not available.</p>'); }, 12000);
                    },
                });
            }
        });
    });


    $('.events_see_more').click( function() {
        var button_next = $(this);
        var time_zone_offset = new Date();
        time_zone_offset = time_zone_offset.getTimezoneOffset() / 60
        time_zone_offset = -1 * time_zone_offset; // меняем знак
        $.ajax({
            method: 'POST',
            url: '/events/api/show_event_page/',
            data:  {'next_page': button_next.attr('next_page'), 'time_zone_offset': time_zone_offset},
            beforeSend: function( xhr, settings ){
                $('.spinner').show();
                csrftoken = getCookie('csrftoken');
                if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader('X-CSRFToken', csrftoken);
                }
            }  
        }).done(function( msg ) {
            $('.spinner').hide();
            if (msg.stop_pagination === '0') {
                $('.all_events_view tr:last').after(msg.html_content);
                var next_page = button_next.attr('next_page');
                next_page = parseInt(next_page,10);
                next_page += 1;
                button_next.attr({'next_page': next_page});
                console.log(next_page);
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

    $('.del_user').click( function() {
        var selected = $('.checkboxes input:checked').attr('value');
        if ( selected ) {
            var ansver = window.confirm('Вы точно хотите удалить пользователя?');
            if ( ansver ) {
                $.ajax({
                    method: 'POST',
                    url: '/api/del_users/',
                    data:  {'selected': selected},
                    beforeSend: function( xhr, settings ){
                        $('.spinner').css('display', 'inline');
                        csrftoken = getCookie('csrftoken');
                        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                            xhr.setRequestHeader('X-CSRFToken', csrftoken);
                        }
                    },
                    success: function( msg ) {
                        var tr = $('.checkboxes input:checked').parent().parent();
                        if (msg.error == '1') {
                            setTimeout(function() { }, 4000);
                            $('.spinner').hide(); 
                            $('.success_msg').hide();
                            $('.error_msg').show();
                            $('.error_msg').html(msg.text);
                        }

                        if (msg.error == '0') {
                            setTimeout(function() { tr.remove(); }, 4000);
                            $('.spinner').hide();
                            $('.error_msg').hide();
                            $('.success_msg').show();
                            $('.success_msg').html(msg.text);
                        }

                    },
                    error: function() {
                        $('.spinner').hide();
                        $('.error_msg').show();
                        $('.success_msg').hide();
                        $('.error_msg').html('<p>Server not available.</p>');
                        setTimeout(function() { $('.error_msg').hide(); }, 12000);
                    },
                });
            }
        }
    });

    $('.change_password').click( function() {
        var selected = $('.checkboxes input:checked').attr('value');
        if ( selected ) {
            var move_url = $(this).attr('href');
            var loc = move_url + '?id=' + selected;
            window.location.href = loc;
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
        // выбор колонки с магнитными барабанами
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

    $('.del_cart_name, .del_cart_type').click( function() {
        var selected = $('.checkboxes input:checked').attr('value');
        var css_class = $(this).attr('class');
        if ( selected ) {
            var ansver = window.confirm('Вы точно хотите удалить?');
            if ( ansver ) {
                if ( css_class.indexOf('del_cart_name') != -1 ) {
                    var atype = 'cart_name';
                }

                if ( css_class.indexOf('del_cart_type') != -1 ) {
                    var atype = 'cart_type';
                }
                // если пользователь ответил Да, то запускаем аякс запрос
                $.ajax({
                    method: 'POST',
                    url: '/docs/api/del_cart_name/',
                    data:  {'cart_name_id': selected , 'atype': atype },
                    beforeSend: function( xhr, settings ){
                        $('.spinner').css('display', 'inline');
                        csrftoken = getCookie('csrftoken');
                        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                            xhr.setRequestHeader('X-CSRFToken', csrftoken);
                        }
                    },
                    success: function( msg ) {
                        var tr = $('.checkboxes input:checked').parent().parent();
                        if (msg.error == '1') {
                            setTimeout(function() { }, 4000);
                            $('.spinner').hide(); 
                            $('.success_msg').hide();
                            $('.error_msg').show();
                            $('.error_msg').html(msg.text);
                        }

                        if (msg.error == '0') {
                            setTimeout(function() { tr.remove(); }, 4000);
                            $('.spinner').hide();
                            $('.error_msg').hide();
                            $('.success_msg').show();
                            $('.success_msg').html(msg.text);
                        }

                    },
                    error: function() {
                        $('.spinner').hide();
                        $('.error_msg').show();
                        setTimeout(function() { $('.error_msg').html('<p>Server not available.</p>'); }, 12000);
                    },
                });

            }
        }
    });


    $('.edit_cart_type').click( function() {
        var selected = $('.checkboxes input:checked').attr('value');
        if (!selected) { return; }
        var move_url = $(this).attr('href');
        var loc = move_url + '?id=' + selected + '&back=' + window.location.pathname;
        window.location.href = loc;
    });

    $('#id_filter_ca').keyup( function(e) {
        var code = (e.keyCode ? e.keyCode : e.which);
        // the tab key will force the focus to the next input
          // already on keydown, let's prevent that
          // unless the alt key is pressed for convenience
        if (code == 9 || code == 13 || code == 38 || code == 40 || code == 18 || code == 17 || code == 39 || code == 37) {
            e.preventDefault();
            return false;
          // let's prevent default enter behavior while a suggestion
          // is being accepted (e.g. while submitting a form)
        } else {
            var cart_name = $(this).val();
            cart_name = cart_name.trim();
            if (!cart_name) {
                // отсекаем часть ненужных-пустых запросов к серверу
                $('.dinamic_list').find('option').remove().end(); // очищаем весь  select 
                return false;
            }
            $('.filter_spinner').css('display', 'block');
            $.ajax({
                method: 'POST',
                url: '/api/names_suggests/',
                data: {'cart_name': cart_name},
                beforeSend: function( xhr, settings ){
                    csrftoken = getCookie('csrftoken');
                    if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                        xhr.setRequestHeader('X-CSRFToken', csrftoken);
                    }
                },
                success: function( msg ) {
                    $('.filter_spinner').hide();
                    $('.error_msg').hide();
                    $('.dinamic_list').find('option').remove().end(); // очищаем весь  select 
                    for (var i = 0; i < msg.res.length; i++) {
                        // добавляем в селект новые опции
                        $('.dinamic_list').append($('<option>', { value: msg.res[i][0], text : msg.res[i][1] }));;
                    }

                },
                error: function() {
                    $('.filter_spinner').hide();
                    $('.error_msg').show();
                    setTimeout(function() { $('.error_msg').html('<p>Server not available.</p>'); }, 12000);
                },
            });
        }
          
    });

    $('.search_query').focus( function () {
        /*  При установке курсора в поле ввода очищаем текст */
        $(this).attr('value', '');
    });

    $('.settings_email').click( function() {
        var smtp_server   = $('#id_smtp_server').val();
        var smtp_port     = $('#id_smtp_port').val();
        var email_sender  = $('#id_email_sender').val();
        var smtp_login    = $('#id_smtp_login').val();
        var smtp_password = $('#id_smtp_password').val();
        var use_ssl    = $('#id_use_ssl').is(':checked');
        var use_tls    = $('#id_use_tls').is(':checked');
        $.ajax({
            method: 'POST',
            url: '/service/api/settings_email/',
            data: {'smtp_server': smtp_server, 'smtp_port': smtp_port,
                   'email_sender': email_sender, 'smtp_login': smtp_login,
                   'smtp_password': smtp_password, 'use_ssl': use_ssl,
                   'use_tls': use_tls
            },
            beforeSend: function( xhr, settings ){
                csrftoken = getCookie('csrftoken');
                $('.spinner_sett').show();
                if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader('X-CSRFToken', csrftoken);
                }
            },
            success: function( msg ) {
                $('.settings_email_form').find('.form_error_text').remove();
                for (var key in msg.errors) {
                    // Check for proper key in dictionary
                    if (key in {'smtp_server': 1, 'smtp_port': 1, 'email_sender': 1, 
                                'smtp_login': 1, 'smtp_password': 1, 'use_ssl': 1}) {
                        // Читаем сообщение об ошибке
                        error = msg.errors[key][0];
                        field = $('.settings_email_form').find('#id_' + key);
                        // Прикрепляем сообщение с ошибкой после поля
                        field.after('<div class="form_error_text" style="display: block;">' + error + '</div>');
                    }
                }
                $('.spinner_sett').hide();
                if (!msg.errors) {
                    $('.success_msg_set').show();
                    $('.success_msg_set').text(msg.text);
                    setTimeout(function() { $('.success_msg_set').hide(); }, 12000);
                }
            },
            error: function( msg ) {
                console.log(msg);                
            },
        });

    });

    $('.send_repair_email').click( function() {
        var email   = $('#id_email').val();
        $.ajax({
            method: 'POST',
            url: '/manage_users/api/send_repair_email/',
            data: {'email': email},
            beforeSend: function( xhr, settings ){
                $('.spinner_send').show();
                csrftoken = getCookie('csrftoken');
                if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader('X-CSRFToken', csrftoken);
                }
            },
            success: function( msg ) {
                $('.spinner_send').hide();
                if (msg.errors) {
                    $('.error_msg_send_email').show();
                    $('.error_msg_send_email').text(msg.errors);
                    setTimeout(function() { $('.error_msg_send_email').hide(); }, 20000);
                } else {
                    $('.success_msg_send_email').show();
                    $('.error_msg_send_email').hide();
                    $('.success_msg_send_email').text(msg.text);
                    setTimeout(function() { $('.success_msg_send_email').hide(); }, 20000);
                }
            },
            error: function( msg ) {
                $('.spinner_send').hide();
                console.log(msg);
            },
        });
    });

    $('.send_email').click( function() {
        var text   = $('#id_text').val();
        var email   = $('#id_email').val();
        $.ajax({
            method: 'POST',
            url: '/service/api/send_test_email/',
            data: {'text': text, 'email': email},
            beforeSend: function( xhr, settings ){
                $('.spinner_send').show();
                csrftoken = getCookie('csrftoken');
                if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader('X-CSRFToken', csrftoken);
                }
            },
            success: function( msg ) {
                $('.spinner_send').hide();
                $('.send_email_form').find('.form_error_text').remove();
                for (var key in msg.errors) {
                    // Check for proper key in dictionary
                    if (key in {'text': 1, 'email': 1}) {
                        // Читаем сообщение об ошибке
                        error = msg.errors[key][0];
                        field = $('.send_email_form').find('#id_' + key);
                        // Прикрепляем сообщение с ошибкой после поля
                        field.after('<div class="form_error_text" style="display: block;">' + error + '</div>');
                    }
                }
                if (msg.errors)  {
                    $('.success_msg_send').hide();
                    $('.error_msg_send').show();
                    $('.error_msg_send').text(msg.errors);
                    setTimeout(function() { $('.error_msg_send').hide(); }, 20000);
                } else  {
                    $('.success_msg_send').show();
                    $('.success_msg_send').text(msg.text);
                    $('.error_msg_send').hide();
                    setTimeout(function() { $('.success_msg_send').hide(); }, 20000);
                }

            },
            error: function( msg ) {
                console.log(msg);                
            },
        });
    });

    $('.select_ou').each( function() {
        var select_ou = $(this);
        select_ou.bind('change', function() {
            var id_ou = select_ou.children(':selected').attr('value');
            $.ajax({
                method: 'POST',
                url: '/api/get_cart_ou/',
                data: {'id_ou': id_ou},
                beforeSend: function( xhr, settings ){
                    $('.spinner').show();
                    csrftoken = getCookie('csrftoken');
                    if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                        xhr.setRequestHeader('X-CSRFToken', csrftoken);
                    }
                },
                success: function( msg ) {
                    $('.spinner').hide();
                    $('.check_use_cartridge').show();
                    $('.check_use_cartridge').html(msg.html);
                    $('.move_to_use').removeClass('block');
                },
                error: function( msg ) {
                    console.log(msg);
                },
            });
        })
    });

    $('.move_to_use').click(function () {
        var moved = $('.moved_cart_numb').attr('data');
        moved = moved.split(',')
        var id_ou = $('.select_ou').children(':selected').attr('value'); 
        var installed = [];
        $('.check_use_cartridge input:checked').each(function() {
            installed.push( $(this).attr('value') );
        });
        if (!$('.move_to_use').hasClass('block')) {
            $.ajax({
                method: 'POST',
                url: '/api/move_to_use/',
                data: {'moved[]': moved, 'id_ou': id_ou, 'installed[]': installed},
                beforeSend: function( xhr, settings ){
                    $('.spinner').show();
                    csrftoken = getCookie('csrftoken');
                    if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                        xhr.setRequestHeader('X-CSRFToken', csrftoken);
                    }
                },
                success: function( msg ) {
                    $('.spinner').hide();
                    if (msg.error == '0') {
                        window.location.href = msg.url;
                    }
                    
                    

                },
                error: function( msg ) {
                    console.log(msg);
                },
            });
        }
    });

});
