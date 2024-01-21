$('.set-bg').each(function () {
    var bg = $(this).data('setbg');
    $(this).css('background-image', 'url(' + bg + ')');
});

var hero_s = $(".hero__slider");
hero_s.owlCarousel({
    loop: true,
    margin: 0,
    items: 1,
    dots: true,
    nav: true,
    navText: [
        "<span class='arrow_carrot-left'><img src='static/img/arrow_left_nav_icon.svg' /></span>",
        "<span class='arrow_carrot-right'><img src='static/img/arrow_right_nav_icon.svg' /></span>"
    ],
    animateOut: 'fadeOut',
    animateIn: 'fadeIn',
    smartSpeed: 1200,
    autoHeight: false,
    mouseDrag: false
});