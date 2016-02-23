var drawerClickEvent = 'touchend';

if(!((window.DocumentTouch && document instanceof DocumentTouch) || 'ontouchstart' in window)){
    drawerClickEvent = 'click';
}

$('[data-toggle=offcanvas]').on(drawerClickEvent, function(){
    var drawerClass = ( $(this).data('target') === 'left' ? 'active-left' : 'active-right');
    $('html').toggleClass('drawer-open '+ drawerClass);
});

$('.offcanvas-close-btn').on(drawerClickEvent, function(){
    $('html').removeClass('drawer-open active-left active-right');
});
