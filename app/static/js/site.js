$(document).ready(function() {

  // Variables
  var $nav = $('.navbar'),
    $body = $('body'),
    $window = $(window),
    $popoverLink = $('[data-popover]'),
    navOffsetTop = $nav.offset().top,
    $document = $(document);

  function init() {
    $window.on('scroll', onScroll);
    $window.on('resize', resize);
    $popoverLink.on('click', openPopover);
    $document.on('click', closePopover);
    $('a[href^="#"]').on('click', smoothScroll);
    $('input[type=text]:first').focus();
    $('input[type=text]:first').on('keypress click', function() {
      $('.has-error').hide();
    });
  }

  function smoothScroll(e) {
    e.preventDefault();
    $(document).off("scroll");
    var target = this.hash,
      menu = target;
    $target = $(target);
    $('html, body').stop().animate({
      'scrollTop': $target.offset().top - 40
    }, 0, 'swing', function() {
      window.location.hash = target;
      $(document).on("scroll", onScroll);
    });
  }

  function openPopover(e) {
    e.preventDefault();
    closePopover();
    var popover = $($(this).data('popover'));
    popover.toggleClass('open');
    e.stopImmediatePropagation();
  }

  function closePopover(e) {
    if ($('.popover.open').length > 0) {
      $('.popover').removeClass('open');
    }
  }

  $('#button').click(function() {
    $('html, body').animate({
      scrollTop: $('#elementtoScrollToID').offset().top
    }, 2000);
  });

  function resize() {
    $body.removeClass('has-docked-nav');
    navOffsetTop = $nav.offset().top;
    onScroll();
  }

  function onScroll() {
    if (navOffsetTop < $window.scrollTop() && !$body.hasClass('has-docked-nav')) {
      $body.addClass('has-docked-nav')
    }
    if (navOffsetTop > $window.scrollTop() && $body.hasClass('has-docked-nav')) {
      $body.removeClass('has-docked-nav')
    }
  }

  init();

});
