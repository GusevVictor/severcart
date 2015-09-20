$( function(){
    $(".add_items").click( function() {
        ;
    });

    $(".tr_for_use").click( function() {
        var selected = [];
        $('.checkboxes input:checked').each(function() {
            selected.push( $(this).attr('value') );
        });
        //console.log(selected);
        var get_path = selected.join('s')
        var loc = "/transfe_for_use/?select=" + get_path;
        window.location.href = loc;
        //console.log(JSON.stringify(selected));

    });

    $(".tr_to_recycle_bin").click( function() {
        console.log('Утилизируем');
    });

});