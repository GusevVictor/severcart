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

});
