$( function() {
    $('.tooltips').powerTip({
        placement: 'ne', // north-east tooltip position
        smartPlacement: true
    });


    $('.info_ico').each(function() {
        $(this).powerTip({
            placement: 'ne', // north-east tooltip position
            smartPlacement: true
        });

        $(this).click( function(){
            $(this).powerTip('show');
        });
    });

    $('.cart_number_for_tip').each(function() {
        $(this).powerTip({
            placement: 'n',
            smartPlacement: true,
        });

        $(this).click( function(){
            $(this).powerTip('show');
        });
    });

});
