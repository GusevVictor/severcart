function validator_money(any_num){
    any_num = any_num.trim();
    if (!any_num) {
        return {'error': true, 'text': 'Обязательное поле'}
    }

    var regex = /^[0-9]\d*(((,\d{3}){1})?(\.\d{0,2})?)$/;
    var result = regex.test(any_num);
    if (result) {
        return {'error': false, 'text': ''};
    } else {
        return {'error': true, 'text': 'Не соответствует формату'};
    }

}

$(function () {
    $('input.money').each(function() {
        var money_input = $(this);
        money_input.bind('focusout', function() {
            var current = $(this).val();
            var res = validator_money(current);
            if (res['error']) {
                money_input.next().show();
                $(money_input.next().children()[1]).html(res['text']);
                money_input.addClass('error_border');
            } else {
                money_input.next().hide();
                money_input.removeClass('error_border');
            }
            
        });
    });
});
