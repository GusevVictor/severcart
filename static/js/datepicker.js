
$(function() {
	// настраиваем календарик
    $('.datepicker').datepicker({ 
        dateFormat: 'dd/mm/yy',
        showOn: "button",
        buttonImage: "/static/img/calendar.png",
        buttonImageOnly: true,
    });

    // инициализируем календарик
    $('.datepicker').datepicker();
});
