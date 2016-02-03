/* https://css-tricks.com/number-increment-buttons/ */ 

$(function() {
    $(".pm_counter").after('<a class="inc button">+</a>');
    $(".pm_counter").before('<a class="dec button">-</a>');

    

    $(".button").on("click", function() {
        var $button = $(this);
        var oldValue = $button.parent().find("input.pm_counter").val();
        // в атрибуте data спрятано минимальное допустимое значение счётчика
        // если атрибут не определен, то предполагается 0
        var minValue = $button.parent().find("input.pm_counter").attr("data");
        if (minValue) {
            minValue = parseInt(minValue);
        } else {
            minValue = 0;
        }
        
        if (!parseInt(oldValue)) {
            oldValue = minValue;
        }
        if ($button.text() == "+") {
            var newVal = parseFloat(oldValue) + 1;
        } else {
            // если пользователь нажал на минус
            if (oldValue > minValue) {
                var newVal = parseFloat(oldValue) - 1;
            } else {
                newVal = minValue;
            }
        }
        $button.parent().find("input.pm_counter").val(newVal);
    });

});
