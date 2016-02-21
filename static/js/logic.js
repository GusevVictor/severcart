
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


    $('.export_to_csv').click( function() {
        var win = function() {
            return window.open('', '_blank');
        };
        var view = $(this).attr('view');
        $.ajax({
            method: 'POST',
            url: '/docs/api/generate_csv/',
            data:  {'view': view },
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
                var w = win();
                w.location.href = msg.url;
                w.focus();
            },
            error: function() {
                $('.export_spinner').hide();
                $('.error_msg').show();
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
            var loc = '/transfe_for_use/?select=' + get_path + '&back=' + window.location.pathname;
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


  /*  var getUrlParameter = function getUrlParameter(sParam) {
        
        //http://stackoverflow.com/questions/19491336/get-url-parameter-jquery
        
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
    }; */

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
            var doc_action = mainSelect.children(':selected').attr('value');
            if (doc_action) {
                var win = window.open('', '_blank');
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
                            setTimeout(function() { }, 4000);
                            $('.spinner').hide(); 
                            $('.error_msg').hide();
                            $('.success_msg').show();
                            $('.success_msg').html(msg.text);
                            win.location.href = msg.url;
                            win.focus();
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
        var move_url = $(this).attr('href');        
        var loc = move_url + '?id=' + selected;
        window.location.href = loc;        
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

});