$(window, document, undefined).ready(function() {
  $('form').on('submit', function(event) {
    $.ajax({
      email: $('#email').val(),
      password: $('#password').val()
    }),
    type : 'POST',
    url : '../python/loginProcess'

    .done(function(data) {
      if (data.error) {
        $('#errorAlert').text(data.error).show();
        $('#successAlert').hide();
      } else {
        $('#successAlert').text(data.name).show();
        $('#errorAlert').hide();
      }
    });
    event.preventDefault();
  });


  $('input').blur(function() {
    var $this = $(this);
    if ($this.val())
      $this.addClass('used');
    else
      $this.removeClass('used');
  });

  var $ripples = $('.ripples');

  $ripples.on('click.Ripples', function(e) {

    var $this = $(this);
    var $offset = $this.parent().offset();
    var $circle = $this.find('.ripplesCircle');

    var x = e.pageX - $offset.left;
    var y = e.pageY - $offset.top;

    $circle.css({
      top: y + 'px',
      left: x + 'px'
    });

    $this.addClass('is-active');

  });

  $ripples.on('animationend webkitAnimationEnd mozAnimationEnd oanimationend MSAnimationEnd', function(e) {
  	$(this).removeClass('is-active');
  });

});