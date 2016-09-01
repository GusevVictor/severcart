/* привязываем искусственное генерацию события нажатия клавиши  "Добавить"
при нажатии на клавишу Enter
*/

$(document).ready(function() {
    $(document).bind('keydown', 'return', function() {
        $('.add_items').click();
        $('.add_items_from_barcode').click();
    });
});
