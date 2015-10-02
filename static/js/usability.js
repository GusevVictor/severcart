$( function() {
    var parent_item;
    var child_item;
    $('#menu li a').hover(
        function() {
            parent_item = $(this);
            $(this).parent().children('ul').addClass('hovered');
        }, 
        function() {
            //
        }
    );
    
    $('#menu li ul').hover(
        function() {
            //
        },
        function() {
            var self = $(this);
            child_item = $(this);
            setTimeout(function() {
                if (self.parent().children('a').is(parent_item)) {
                    //console.log('True');
                } else {
                    self.removeClass('hovered'); 
                }
            }, 500)
        }
    )
    
});
