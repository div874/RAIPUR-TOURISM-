/**
 * Site-wide text zoom (A− / A / A+). CSS: css/menu.css (--site-text-scale, html zoom).
 * Runs when this file loads (footer) to apply stored scale ASAP; binds toolbar on DOM ready.
 */
(function () {
  var STORAGE_KEY = 'mpt_site_text_scale';
  var LEGACY_KEY = 'mpt_site_text_size';
  var MIN = 0.75;
  var MAX = 1.55;
  var STEP = 0.1;

  function clampScale(n) {
    if (isNaN(n)) return 1;
    var r = Math.round(n * 100) / 100;
    return Math.min(MAX, Math.max(MIN, r));
  }

  function readStoredScale() {
    try {
      var raw = localStorage.getItem(STORAGE_KEY);
      if (raw !== null && raw !== '') {
        var s = parseFloat(raw);
        if (!isNaN(s)) return clampScale(s);
      }
      var t = localStorage.getItem(LEGACY_KEY);
      if (t === 'small') return 0.9;
      if (t === 'large') return 1.2;
    } catch (e) {}
    return 1;
  }

  function applyScale(scale) {
    scale = clampScale(scale);
    document.documentElement.style.setProperty('--site-text-scale', String(scale));
    try {
      localStorage.setItem(STORAGE_KEY, String(scale));
    } catch (e) {}

    var buttons = document.querySelectorAll('.header .font-size-btn');
    for (var i = 0; i < buttons.length; i++) {
      var b = buttons[i];
      var tier = b.getAttribute('data-tier');
      var pressed = 'false';
      if (tier === 'normal' && scale === 1) pressed = 'true';
      else if (tier === 'small' && scale < 1) pressed = 'true';
      else if (tier === 'large' && scale > 1) pressed = 'true';
      b.setAttribute('aria-pressed', pressed);
    }
    try {
      window.setTimeout(function () {
        window.dispatchEvent(new Event('resize'));
      }, 0);
    } catch (e) {}
  }

  function bootstrapScaleFromStorage() {
    try {
      document.documentElement.style.setProperty('--site-text-scale', String(readStoredScale()));
    } catch (e) {}
  }

  function initFontSizeToolbar() {
    applyScale(readStoredScale());

    var btns = document.querySelectorAll('.header .font-size-btn');
    for (var j = 0; j < btns.length; j++) {
      btns[j].addEventListener('click', function () {
        var tier = this.getAttribute('data-tier');
        var current = parseFloat(
          getComputedStyle(document.documentElement).getPropertyValue('--site-text-scale').trim()
        );
        if (isNaN(current)) current = readStoredScale();

        if (tier === 'small') {
          applyScale(current - STEP);
        } else if (tier === 'large') {
          applyScale(current + STEP);
        } else {
          applyScale(1);
        }
      });
    }
  }

  bootstrapScaleFromStorage();

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initFontSizeToolbar);
  } else {
    initFontSizeToolbar();
  }
})();


	

// Navbar hover animatio
$(function(){

    setTimeout(function() {
        $('.tab-pane.active .initial_content').fadeOut('fast');
    }, 2000);




     

    var lastScrollTop = 0;
    $(window).on('scroll', function() {
        ss = $(this).scrollTop();
        if(ss < lastScrollTop) {
             $(".header").removeClass("not-visible");
        }
        else {
             $(".header").addClass("not-visible");
        }
        lastScrollTop = ss;
    });

});



$(document).ready(function () {
  function mptSyncHeaderHeightVar() {
    var el = document.querySelector(".header");
    if (!el) return;
    var h = Math.round(el.getBoundingClientRect().height || el.offsetHeight);
    if (h < 72) h = 150;
    document.documentElement.style.setProperty("--mpt-header-height", h + "px");
  }

  mptSyncHeaderHeightVar();
  requestAnimationFrame(function () {
    mptSyncHeaderHeightVar();
  });
  $(window).on("load resize", mptSyncHeaderHeightVar);

  function mptHeaderStickThreshold() {
    var raw = getComputedStyle(document.documentElement)
      .getPropertyValue("--mpt-header-height")
      .trim();
    var px = parseInt(raw, 10);
    return !isNaN(px) && px > 0 ? px : 150;
  }

  $(window).on("scroll", function () {
    var sc = $(window).scrollTop();
    if (sc > mptHeaderStickThreshold()) {
      $(".header").addClass("fixed-header");
      $(".planitinerary-cnt").addClass("show-form");
    } else {
      $(".header").removeClass("fixed-header not-visible");
      $(".planitinerary-cnt").removeClass("show-form");
    }
  });
});
// range slider

$(document).ready(function() {
  var rangeInput = $("#cowbell");
  var rangeValue = $(".rangevalu span");
  
  // Set initial value
  rangeValue.text(rangeInput.val());
  
  // Update value on all types of input
  rangeInput.on('input change touchstart touchmove touchend', function() {
    var value = $(this).val();
    rangeValue.text(value);
  });
});

// close Notification

$(document).ready(function() {
 
  $(".close-notification").click(function(){
    $(".notification").hide("slide", { direction: "right" }, 1000);
    $(".noti-icon").addClass("active-icon");
  });
  $(".noti-icon").click(function(){
    $(".notification").show("slide", { direction: "right" }, 1000);
    $(".noti-icon").removeClass("active-icon");
  });
   
});


// Search popup
$(document).ready(function() {

  $(".search-item").click(function(){
    $(".serch-pop").addClass("active-ser-pop");
  });

  $(".close-pop").click(function(){
    $(".serch-pop").removeClass("active-ser-pop");
  });

});
// select box

$(document).ready(function() {
$('select').niceSelect();
});

// Scrolling animation
$('.animate').scrolla({
  mobile: true,
  once: true
});

// owl carousel
var owl = $('.event-slider');
owl.owlCarousel({
  stagePadding: 160,
  loop:true,
  margin:20,
  nav:false,
  items:1,
  smartSpeed : 800, 
  touchDrag: false,
  mouseDrag: false,
  responsiveClass: true,
  responsive:{
      0:{
          items:1,
          stagePadding: 0,
      },
      400:{
          items:1,
          stagePadding: 0,
          margin:0
      },
      1000:{
          items:1,
      }
  }
});
$('.customNextBtn').click(function() {
  owl.trigger('next.owl.carousel');
});
$('.customPreviousBtn').click(function() {
  owl.trigger('prev.owl.carousel');
});



$(document).ready(function() {
  var $events_txt = $('.owl-item.active .eventsslide-item .overly-txt').clone();
  $('.events-slide-txt').html($events_txt);
  $('.customNextBtn, .customPreviousBtn').click(function() {
    var $events_txt = $('.owl-item.active .eventsslide-item .overly-txt').clone();
    $('.events-slide-txt').html($events_txt);
  });
 
});



// Related owl carousel
var related_owl = $('.related-slider');
related_owl.owlCarousel({
  loop:true,
  margin:0,
  items:1,
  autoplay: true,
  nav:true,
  navText:['<i class="fa fa-angle-left"></i>','<i class="fa fa-angle-right"></i>'],
  smartSpeed : 800,
  responsive:{
      0:{
          items:1
      },
      600:{
          items:1
      },
      1000:{
          items:1,
      }
  }
});
$('.relatedNextBtn').click(function() {
  related_owl.trigger('next.owl.carousel');
});
$('.relatedPreviousBtn').click(function() {
  related_owl.trigger('prev.owl.carousel');
});





// Notification Scrolltop
$(document).ready(function() {
  $( ".notification-click" ).click(function( event ) {
    event.preventDefault();
    $("html, body").animate({ 
      scrollTop: $($(this).attr("href")).offset().top - 110
    }, 800);
  });
});





$.simpleTicker($("#ticker-fade"),{
  speed : 1000,
  delay : 5000,
  easing : 'swing',
  effectType : 'slide'
});



// $(function() {
//   $("#video-tabs").tabs({
//     hide:{effect:"slide", direction:"left"},
//     show:{effect:"slide", direction:"right"}
//   });
// });

$(function() {
  // $("#heritage-tabs").tabs({
  //   hide:{effect:"slide", direction:"left"},
  //   show:{effect:"slide", direction:"right"}
  // });

  $("#heritage-tabs .js-tabs-nav .nav-tabs-link").aniTabs({animation:"slide", animationSpeed:800, slideDirection:"left", drag:false,autoHeight:false});
});

// Custom video button

/*$('.video').parent().click(function () {
  if($(this).children(".video").get(0).paused){$(this).children(".video").get(0).play();   $(this).children(".playpause").fadeOut();
    }else{       $(this).children(".video").get(0).pause();
  $(this).children(".playpause").fadeIn();
    }
});*/



  jQuery(function($){
    $(".rvs-container").rvslider();
    
    $(".story-carousel").owlCarousel({
                  loop:false,
                  margin:10,
                  items:1,
                  dots:false,
                  nav:true,
                  navText:['<i class="fa fa-angle-left"></i>','<i class="fa fa-angle-right"></i>'],
                  smartSpeed : 800,
                  responsive:{
                      0:{
                          items:1
                      },
                      401:{
                          items:1
                      },
                      600:{
                          items:2
                      },
                      1000:{
                          items:3,
                      }
                  }
                });
    

  });

$(window).on('load', function() {
	// Animate loader off screen
	jQuery(".se-pre-con").fadeOut("slow");
});

$(document).ready(function(){
  $(".header .menu-icon").click(function(){
    $(".collapse-menu").addClass("show-hide-menu");
  });

  $(".close-rt-pnl").click(function(){
    $(".collapse-menu").removeClass("show-hide-menu");
  });
  
  $('.header .nav-item').click(function(){
      
      if($(window).width() < 768){
        $(this).toggleClass("active-toggle");
      }
  });

  $('.header .nav-link').click(function(){
    if($(window).width() < 768){
    $(this).toggleClass("active");
    }
  });

});







$(document).ready(function() {

  var sync1 = $("#sync1");
  var sync2 = $("#sync2");
  var slidesPerPage = 12; //globaly define number of elements per page
  var syncedSecondary = true;

  sync1.owlCarousel({
    items : 1,
    slideSpeed : 2000,
    nav: true,
    navText: ['<div class="owl-arrows"><i class="fa fa-angle-left" aria-hidden="true"></i></div>','<div class="owl-arrows"><i class="fa fa-angle-right" aria-hidden="true"></i></div>'],
    autoplay: false,
    dots: false,
    loop: true,
    responsiveRefreshRate : 200,
   
  }).on('changed.owl.carousel', syncPosition);

  sync2
    .on('initialized.owl.carousel', function () {
      sync2.find(".owl-item").eq(0).addClass("current");
    })
    .owlCarousel({
    items : slidesPerPage,
    dots: false,
    margin: 10,
    nav: true,
    navText: ['<div class="owl-arrows"><i class="fa fa-arrow-left" aria-hidden="true"></i></div>','<div class="owl-arrows"><i class="fa fa-arrow-right" aria-hidden="true"></i></div>'],
    smartSpeed: 200,
    slideSpeed : 500,
    slideBy: slidesPerPage, //alternatively you can slide by 1, this way the active slide will stick to the first item in the second carousel
    responsiveRefreshRate : 100,
    responsiveClass: true,
    responsive: {
        0:{
          items: 3
        },
        480:{
          items: 3
        },
        769:{
          items: slidesPerPage,
        }
    }
  }).on('changed.owl.carousel', syncPosition2);

  function syncPosition(el) {
    //if you set loop to false, you have to restore this next line
    //var current = el.item.index;
    
    //if you disable loop you have to comment this block
    var count = el.item.count-1;
    var current = Math.round(el.item.index - (el.item.count/2) - .5);
    
    if(current < 0) {
      current = count;
    }
    if(current > count) {
      current = 0;
    }
    
    //end block

    sync2
      .find(".owl-item")
      .removeClass("current")
      .eq(current)
      .addClass("current");
    var onscreen = sync2.find('.owl-item.active').length - 1;
    var start = sync2.find('.owl-item.active').first().index();
    var end = sync2.find('.owl-item.active').last().index();
    
    if (current > end) {
      sync2.data('owl.carousel').to(current, 100, true);
    }
    if (current < start) {
      sync2.data('owl.carousel').to(current - onscreen, 100, true);
    }
  }
  
  function syncPosition2(el) {
    if(syncedSecondary) {
      var number = el.item.index;
      sync1.data('owl.carousel').to(number, 100, true);
    }
  }
  
  sync2.on("click", ".owl-item", function(e){
    e.preventDefault();
    var number = $(this).index();
    sync1.data('owl.carousel').to(number, 300, true);
  });







$(".open-lightbox").click(function(){
  $(".custom-lightbox").addClass("lightbox-opend");
});
$(".lightbox-close").click(function(){
  $(".custom-lightbox").removeClass("lightbox-opend");
});

});