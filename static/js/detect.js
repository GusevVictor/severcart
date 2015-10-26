var agt = navigator.userAgent.toLowerCase(),
	IE8 = (agt.indexOf('msie 8.0') != -1) //&& document.all && !OP,
	IE7 = (agt.indexOf('msie 7.0') != -1) //&& document.all && !OP,
	IE6 = (agt.indexOf('msie 6.0') != -1) //&& document.all && !OP,

	if (IE8) {
        //return 1;
        ;
    } else {
    
    if (IE6 || IE7) {
        window.location.replace('/bad_browser/');
	}
   }
   