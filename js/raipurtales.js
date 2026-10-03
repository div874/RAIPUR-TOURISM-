jQuery(function($) {
  $(".animate").scrolla({ mobile: true, once: true });
  var tabLinks = $("#nav-tab .nav-link");
  var currentTab = 0;
  setInterval(function() { currentTab = (currentTab + 1) % tabLinks.length; tabLinks.eq(currentTab).trigger("click"); }, 8000);
  $(".events").owlCarousel({ items:1, loop:true, autoplay:true, autoplayTimeout:5000, nav:false, dots:false });
  $(".customPreviousBtn").click(function() { $(this).closest(".col-sm-6").find(".events").trigger("prev.owl.carousel"); });
  $(".customNextBtn").click(function() { $(this).closest(".col-sm-6").find(".events").trigger("next.owl.carousel"); });
  $(".related-slider").owlCarousel({ items:1, loop:true, autoplay:true, autoplayTimeout:6000, nav:false, dots:true });
  $(".story-carousel").owlCarousel({ loop:true, margin:20, autoplay:true, autoplayTimeout:4000, nav:false, dots:true, responsive:{0:{items:1},640:{items:2},1024:{items:3}} });
  $("#mainVideoContainer").on("click", function() {
    var vid = $(this).find(".main-video-thumb").data("video-id");
    $("#videoModal .youtube-modal-area").html("<iframe width=\"100%\" height=\"400\" style=\"border:none;\" src=\"https://www.youtube.com/embed/"+vid+"?autoplay=1\" allow=\"autoplay;encrypted-media\" allowfullscreen></iframe>");
    $("#videoModal").modal("show");
  });
  $("#videoModal").on("hidden.bs.modal", function() { $(this).find(".youtube-modal-area").html(""); });
  $(".playlist-item").on("click", function() {
    var vid = $(this).data("video-id"), title = $(this).data("video-title"), thumb = $(this).find(".playlist-thumb img").attr("src");
    $(".playlist-item").removeClass("active"); $(this).addClass("active");
    $("#mainVideoContainer .main-video-thumb").attr("src", thumb).data("video-id", vid);
    $(".main-video-title").text(title);
  });
  $("#search-trigger").on("click", function(e) { e.preventDefault(); $("#searchPop").addClass("open"); });
  $("#closeSearch").on("click", function() { $("#searchPop").removeClass("open"); });
  $(document).on("keydown", function(e) { if(e.key==="Escape") $("#searchPop").removeClass("open"); });
  $("#closeNotif").on("click", function() { $("#notificationBar").slideUp(300); });
  $(".menu-icon").on("click", function() { $(".collapse-menu").addClass("show-hide-menu"); });
  $(".close-rt-pnl").on("click", function() { $(".collapse-menu").removeClass("show-hide-menu"); });
  if($(window).width() <= 1023) {
    $(".navbar-menu .nav-link").on("click", function(e) {
      if($(this).siblings(".multi-drodown").length) { e.preventDefault(); $(this).closest(".nav-item").toggleClass("active-toggle"); }
    });
  }
});
