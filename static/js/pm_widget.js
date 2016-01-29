/* https://css-tricks.com/number-increment-buttons/ */ 

$(function() {
    $(".pm_counter").after('<a class="inc button">+</a>');
    $(".pm_counter").before('<a class="dec button">-</a>');


    $(".button").on("click", function() {
        var $button = $(this);
        var oldValue = $button.parent().find("input.pm_counter").val();
        if (!parseInt(oldValue)) {
            oldValue = "0";
        }
        if ($button.text() == "+") {
            var newVal = parseFloat(oldValue) + 1;
        } else {
       
            if (oldValue > 0) {
                var newVal = parseFloat(oldValue) - 1;
            } else {
                newVal = 0;
            }
        }
        $button.parent().find("input.pm_counter").val(newVal);
    });

});
