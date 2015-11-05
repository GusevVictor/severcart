$(function() {
    $( ".dialog-confirm" ).dialog({
      resizable: false,
      height:240,
      modal: true,
      autoOpen: false,
      buttons: {
        "Удалить": function() {
          /* Выполняем ajax запрос на удаление */
          $.ajax({
                method: "POST",
                url: "/api/del_user/",
                data:  {len: selected.length , 'selected[]': $(".dialog-confirm").data()['selected']},
                beforeSend: function( xhr, settings ){
                    /*$('.spinner').css('display', 'inline');
                    csrftoken = getCookie('csrftoken');
                    if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                        xhr.setRequestHeader("X-CSRFToken", csrftoken);
                    } */
                }  
            }).done(function( msg ) {
               /* $('.spinner').css('display', 'none');
                */
                window.location.href = "/manage_users/";
          });
          
          console.log();
          $( this ).dialog( "close" );
        },
        "Отменить": function() {
          $( this ).dialog( "close" );
        }
      }
    });
});


$(function(){
  
    $('.del_user').click( function() {
      var selected = [];
      $('.checkboxes input:checked').each(function() {
      selected.push( $(this).attr('value') );
      });

      if ( selected.length !== 0 )  {
        $(".dialog-confirm").data( "selected", selected );
        var show = $( ".dialog-confirm" ).dialog( 'open' );
      }
  });    
  
});