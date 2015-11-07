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


$(function() {
    $(".dialog-confirm").dialog({
        resizable: false,
        height: 240,
        width: 400,
        modal: true,
        autoOpen: false,
        buttons: [
            {
                text: 'Удалить',
                //'class': 'button alert',
                click: function() {
                    /* Выполняем ajax запрос на удаление */
                    $('.spinner').css('display', 'inline');
                    $.ajax({
                        method: "POST",
                        url: "/api/del_users/",
                        data: {
                            len: $(".dialog-confirm").data()['selected'].length,
                            'selected[]': $(".dialog-confirm").data()['selected']
                        },
                        beforeSend: function(xhr, settings) {
                            $('img.spinner').css('display', 'inline');
                            csrftoken = getCookie('csrftoken');
                            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                                xhr.setRequestHeader("X-CSRFToken", csrftoken);
                            } 
                        },
                        success: function (data, text) {
                            $('.spinner').css('display', 'none');
                            $('.errorlog').addClass('success').addClass('marginBot');
                            $('.errorlog').text(data.msg);
                            // удаляем ноды tr
                            var tmp_arr = $(".dialog-confirm").data()['selected'];
                            for (var inx=0; inx < tmp_arr.length; inx++) {
                                var class_inx = tmp_arr[inx];
                                var class_name = ".userid-" + class_inx;
                                $(class_name).hide(1000);
                                $(class_name).remove();
                            }

                        },
                        error : function(request, status, error) {
                            $('.errorlog').addClass('error').addClass('marginBot');
                            $('.errorlog').text('Пользователь не может быть удалён. ' +
                                                request.responseText + ' Код ошибки: ' + request.status);
                        }
                    });
                    $(this).dialog("close");
                },

            }, {
                text: 'Отменить',
                //'class': 'button',
                click: function() {
                    $(this).dialog("close");
                }
            }

        ],
        close: function() {

        }
    });
});


$(function() {

    $('.del_user').click(function() {
        var selected = [];
        var logins = [];
        $('.checkboxes input:checked').each(function() {
            selected.push($(this).attr('value'));
            var sibl = $(this).parent().siblings()[1].outerText;
            logins.push(sibl);

        });

        
        if (selected.length == 1) {
            $('.dialog-confirm .chislo').text('я');
        } else {
            $('.dialog-confirm .chislo').text('ей');
        }

        $('.dialog-confirm p b').text(logins.join(', '))
        if (selected.length !== 0) {

            $(".dialog-confirm").data("selected", selected);
            var show = $(".dialog-confirm").dialog('open');
        }
    });

});