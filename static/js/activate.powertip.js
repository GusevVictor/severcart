$( function() {
    $('.tooltips').powerTip({
        placement: 'ne', // north-east tooltip position
        smartPlacement: true
    });

    $('.info_ico').powerTip({
        placement: 'ne', // north-east tooltip position
        smartPlacement: true
    });

    $('.info_ico').click( function(){
        $('.info_ico').powerTip('show');
    } );
});
