$( function(){
    $(".add_items").click( function() {
        ;
    });

    $(".tr_for_use").click( function() {
        var selected = [];
        $('.checkboxes input:checked').each(function() {
            selected.push( $(this).attr('value') );
        });

        if ( selected.length !== 0 ) {
            var get_path = selected.join('s')
            var loc = "/transfe_for_use/?select=" + get_path;
            window.location.href = loc;
        }
        //console.log(JSON.stringify(selected));

    });

    $(".tr_to_recycle_bin").click( function() {
        console.log('Утилизируем');
    });

    $(".tr_to_stock").click( function() {
        var selected = [];
        $('.checkboxes input:checked').each(function() {
            selected.push( $(this).attr('value') );
        });

        if ( selected.length !== 0 ) {
            var get_path = selected.join('s')
            var loc = "/transfer_to_stock/?select=" + get_path;
            window.location.href = loc;
        }
        //console.log(JSON.stringify(selected));

    });

    $(".edit_firm").click( function() {
        var selected = [];
        $('.checkboxes input:checked').each(function() {
            selected.push( $(this).attr('value') );
        });


        if ( selected.length !== 0 ) {
            var get_path = selected.join('s')
            var loc = "/edit_firm/?select=" + get_path;
            window.location.href = loc;
        }

    });

    $(".del_firm").click( function() {
        var selected = [];
        $('.checkboxes input:checked').each(function() {
            selected.push( $(this).attr('value') );
        });

        if ( selected.length !== 0 ) {
            var get_path = selected.join('s')
            var loc = "/del_firm/?select=" + get_path;
            window.location.href = loc;
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
        var loc = "";
        var page = ""
        var page_num = getUrlParameter('page');

        if (page_num) {
            page = "&page=" + page_num;
        };

        if ($(this).val()) {
            loc = "/toner_refill/?city=" + $(this).val() + page;
        } else {
            loc = "/toner_refill/";
        }
        window.location.href = loc;

    });

});