/*
 1. opens in TOC view.  - toc class
    transitions immediately fire to spin out the thumbnails
 2. on selection they collapse into controlbar - tos class is removed. show class is added.
    transition position into stacked in bar
 3. on last box's transitionEnd hit, position scheme is changed to relative to the box and they float
    a. need a fallback for no transitionEnd event support.
    b. need a fallback for no transition support
*/

$(window).load(function () {
  setTimeout(function () {
    $(document.body).addClass('go');
  }, 500);
})


// load iframe
$('.show.open div.box').live('click', function () {
  tip.out();
  
  lastDemo = this;
   
  $(this).addClass('selected').siblings().removeClass('selected');
  var link = $(this).find('a:first');
  $('#stage iframe').attr('src', link.attr('href')).show();
  
  // don't show the tooltip twice
  if (Modernizr.sessionstorage){
    var key = link.text().replace(/\s+/g,'').toLowerCase();
    if (sessionStorage[key]) return;
    sessionStorage[key] = true;
  }
  tip.over();
});


// return to grid
$('#return').click(function (e) {
  $('#stage iframe').hide().attr('src', 'about:blank');
  $(document.body).addClass('go');
  $('#body').addClass('toc open').removeClass('show open');

});

var lastDemo;

// when we click from TOC view, kick off the transition to showcase view
$('#boxes').delegate('.toc .box', 'click', function (e) {

  lastDemo = this;

  $(document).bind('webkitTransitionEnd transitionend oTransitionEnd', transitionEnd);

  $(document.body).removeClass('go');
  $('#body').removeClass('toc');

}).delegate('.box a', 'click', function (e) {
  e.preventDefault();
});

// transition queue action...
var boxes = $('.box');
var fnQueue = [
  function () {
    $('#body').addClass('show')
  }, function () {
    $('#body').addClass('open');
    //log(lastDemo)
    $(lastDemo).click()
  }
];

var transitionEnd = function (e) {

  if ($('#body').hasClass('toc') || $('#body').hasClass('open')) {
    return;
  }

  var f = transitionEnd;
  f.boxes = f.boxes || boxes.length;
  // use the in progress one or make a shallow copy
  f.fns = (f.fns && f.fns.length) ? f.fns : $.extend([], fnQueue);

  f.boxes--;
  if (f.boxes === 0) {
    f.boxes = boxes.length;
    var fn = f.fns.shift();
    fn && setTimeout(fn, 500);
  }
};


$('#view_source').click(function () {
  window.open('view-source:' + $('iframe')[0].contentDocument.location.href);
});


// download.. 
$('#download').click(function () {
  var path = $('iframe')[0].contentDocument.location.href.split('/');
  window.open( path.slice(0,-1).join('/') + '/' + path.slice(-2,-1)[0] + '.zip' );
});


// tooltip 
var tip = {
  over: function (e) {
    
    // hover over the invisible tooltip?
    if (e && e.srcElement && $(e.srcElement).closest('.tooltip').length){
      return;
    }
    
    var h3 = $('<h3>').text($(lastDemo).find('a:first span').text());
    var info = $(lastDemo).find('p,ul').clone();

    $('.tooltip').find('h3,p,ul').remove().end()
     .append(h3).append(info)
     .appendTo("#info").addClass('popped');
   },
   out: function (e) {
     $('.tooltip').removeClass('popped');
   }
}

$("#info").hoverIntent({
  over: tip.over,
  out: tip.out,
  timeout: 500
});







var tops = {
  '#stage iframe': 'height',
  '#container': 'height',
  '.controlbar': 'top',
  'footer': 'top'
}

var initialOffset;

function setShowCaseSize() {
  if (!setShowCaseSize.run) {
    storeInitialTops(tops);
    setShowCaseSize.run = true;
  }

  var offset = getOffset();

  $.each(tops, function (sel, prop) {
    var elem = $(sel);
    var value = $.data(elem[0], 'initial');
    //log(elem[0],prop,   value, offset)
    elem.css(prop, parseFloat(value) + offset + 'px')
  });

}

function storeInitialTops(tops) {
  $.each(tops, function (sel, prop) {
    var elem = $(sel); //log( elem.css(prop))
    var value = elem.css(prop);
    value = (value === 'auto' || !value) ? 471 : value; // fix for controlbar position
    $.data(elem[0], 'initial', value);
  });

  var footer = $('footer');
  initialOffset = footer.offset().top + footer.height();
}

function getOffset() {
  // magic number 33 is a good looking amount of padding before bottom of window
  var offset = $(window).height() - 33 - initialOffset;
  // allow between 0 and 160 px of offset
  return Math.min(160, Math.max(0, offset));
}

$(document).ready(setShowCaseSize);
$(window).resize(setShowCaseSize);

