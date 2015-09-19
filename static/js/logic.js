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
        console.log(JSON.stringify(selected));
    });

    $(".tr_to_recycle_bin").click( function() {
        console.log('Утилизируем');
    });

});