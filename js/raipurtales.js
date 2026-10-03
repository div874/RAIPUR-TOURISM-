jQuery(function($) {
  // Init scroll animations
  if ($.fn.scrolla) {
    $(".animate").scrolla({ mobile: true, once: true });
  }

  // Historical Timeline Interactive Switching
  var timelineData = {
    "kosala": {
      year: "ANCIENT KOSALA",
      title: "Vedic & Epic Era Roots",
      desc: "The region of Raipur was part of South Kosala (Dakshina Kosala), mentioned in ancient epics like the Ramayana and Mahabharata. Lush forests and river valleys shaped early indigenous human settlements along the Mahanadi river basin.",
      img: "images/heritage.jpg"
    },
    "somavanshi": {
      year: "9TH - 11TH CENTURY",
      title: "Somavanshi Dynasty & Temple Marvels",
      desc: "Under the Somavanshi rulers, classical brick and stone temple architecture reached its peak in nearby Sirpur and Rajim. Master stone carvers crafted spiritual monuments that stood the test of time.",
      img: "images/museum.jpg"
    },
    "kalchuri": {
      year: "14TH CENTURY",
      title: "Kalchuri Dynasty & Fortification",
      desc: "King Ramachandra of the Kalchuri dynasty established Raipur in the late 14th century, naming it after his son Brahmadeo Rai. The city became the administrative capital of the Ratanpur kingdom branch.",
      img: "images/hero_banner.jpg"
    },
    "1402": {
      year: "1402 AD",
      title: "Hatkeshwar Mahadev Temple Established",
      desc: "In 1402 AD, King Brahmadeo built the revered Hatkeshwar Mahadev Temple on the banks of the Kharun River, creating one of Raipur's oldest and most sacred pilgrimage landmarks.",
      img: "images/heritage.jpg"
    },
    "maratha": {
      year: "18TH CENTURY",
      title: "Maratha Administration & Old Bazaars",
      desc: "The Marathas took control of Raipur in 1750, developing old city markets (Gole Bazaar), trade routes, and administrative posts that connected Central India to the eastern coast.",
      img: "images/purkhauti.jpg"
    },
    "1854": {
      year: "1854 AD",
      title: "Headquarters of Chhattisgarh Commissionery",
      desc: "Under British governance in 1854, Raipur was declared the official headquarters of the Chhattisgarh Commissionery, establishing the Mahant Ghasidas Museum in 1875.",
      img: "images/museum.jpg"
    },
    "2000": {
      year: "2000 AD",
      title: "Chhattisgarh Statehood & Raipur Capital",
      desc: "On November 1, 2000, Chhattisgarh was formed as the 26th state of India, with Raipur designated as its vibrant capital, triggering rapid cultural and economic growth.",
      img: "images/tribal_dance.jpg"
    },
    "today": {
      year: "TODAY",
      title: "A Modern Capital with an Old Soul",
      desc: "Today, Raipur seamlessly bridges ancient tribal traditions and modern urban infrastructure, boasting Naya Raipur's planned smart corridors alongside centuries-old living heritage.",
      img: "images/wildlife.jpg"
    }
  };

  $(".rt-timeline-step").on("click", function() {
    $(".rt-timeline-step").removeClass("active");
    $(this).addClass("active");
    var key = $(this).data("timeline");
    var data = timelineData[key];
    if (data) {
      $("#timeline-img").attr("src", data.img);
      $("#timeline-year").text(data.year);
      $("#timeline-title").text(data.title);
      $("#timeline-desc").text(data.desc);
    }
  });

  // Discovery Filter Tabs
  $(".rt-filter-btn").on("click", function() {
    $(".rt-filter-btn").removeClass("active");
    $(this).addClass("active");
    var filter = $(this).data("filter");

    if (filter === "all") {
      $(".rt-disc-item").fadeIn(300);
    } else {
      $(".rt-disc-item").hide();
      $(".rt-disc-item[data-category='" + filter + "']").fadeIn(300);
    }
  });

  // AI Guide Interactive Assistant
  var aiKnowledgeBase = {
    "1day": {
      title: "1-Day Classic Raipur Itinerary",
      body: "<strong>Morning (8:00 AM):</strong> Start with warm Chila & Farra at Gole Bazaar. Visit the 17th-century Dudhadhari Math.<br><strong>Afternoon (12:30 PM):</strong> Explore Mahant Ghasidas Memorial Museum & have authentic lunch.<br><strong>Evening (5:00 PM):</strong> Sunset stroll at Vivekananda Sarovar (Budha Talab) followed by evening musical fountain show."
    },
    "food": {
      title: "Chhattisgarhi Culinary Discovery",
      body: "Head to Old Raipur street markets for freshly prepared <strong>Farra</strong> (steamed seasoned rice dough) and crispy <strong>Chila</strong> served with spicy tomato-garlic chutney. For sweets, don't miss traditional <strong>Khurmi</strong> and <strong>Bara</strong>!"
    },
    "sunset": {
      title: "Best Sunset Locations in Raipur",
      body: "1. <strong>Vivekananda Sarovar (Budha Talab):</strong> The 37-ft Swami Vivekananda statue glowing against sunset waters.<br>2. <strong>Marine Drive (Telibandha Lake):</strong> Vibrant promenade popular for evening walks and street food.<br>3. <strong>Gangrel Dam Reservoir:</strong> Pristine water vistas just outside the city."
    },
    "temple": {
      title: "Story of Dudhadhari Math",
      body: "Built in the 17th century by Mahant Balbhadra Das, this temple is dedicated to Lord Rama. Legend says the saint lived solely on milk ('Dudh-Ahari'), giving the Math its iconic name. Beautiful ancient wall paintings adorn the interior."
    },
    "wildlife": {
      title: "Nandan Van Jungle Safari Guide",
      body: "Spanning over 800 acres in Naya Raipur, Nandan Van features 4 distinct safaris: Tiger, Lion, Bear, and Herbivore. Visit early morning (9:00 AM) for maximum animal activity!"
    }
  };

  $(".rt-ai-chip, .btn-ask-prompt").on("click", function() {
    var promptKey = $(this).data("prompt");
    var userQuery = $(this).text().trim();
    if(userQuery) $("#aiQueryInput").val(userQuery);

    var res = aiKnowledgeBase[promptKey] || {
      title: "Hamara Raipur AI Recommendation",
      body: "Raipur offers incredible living traditions! For a tailored experience, we recommend exploring <strong>Purkhauti Muktangan</strong> for open-air tribal heritage or enjoying authentic Chhattisgarhi flavours in Old Raipur."
    };

    $("#aiResponseTitle").html(res.title);
    $("#aiResponseBody").html(res.body);
    $("#aiResponseArea").addClass("active").hide().fadeIn(300);
  });

  $("#aiQueryForm").on("submit", function(e) {
    e.preventDefault();
    var query = $("#aiQueryInput").val().toLowerCase();
    var matchedKey = "1day";
    if (query.includes("food") || query.includes("eat") || query.includes("farra")) matchedKey = "food";
    else if (query.includes("sunset") || query.includes("lake")) matchedKey = "sunset";
    else if (query.includes("temple") || query.includes("math") || query.includes("history")) matchedKey = "temple";
    else if (query.includes("wildlife") || query.includes("safari") || query.includes("zoo")) matchedKey = "wildlife";

    var res = aiKnowledgeBase[matchedKey];
    $("#aiResponseTitle").html(res.title);
    $("#aiResponseBody").html(res.body);
    $("#aiResponseArea").addClass("active").hide().fadeIn(300);
  });

  // Events Tabs
  $(".rt-event-tab-btn").on("click", function() {
    $(".rt-event-tab-btn").removeClass("active");
    $(this).addClass("active");
    var tab = $(this).data("tab");
    if(tab === "all") {
      $(".rt-event-card-item").fadeIn(250);
    } else {
      $(".rt-event-card-item").hide();
      $(".rt-event-card-item[data-tab='" + tab + "']").fadeIn(250);
    }
  });

  // Video Playlist Switcher & Modal
  $("#mainVideoContainer, #btnWatchRaipur").on("click", function(e) {
    e.preventDefault();
    var vid = $("#mainVideoContainer").find(".main-video-thumb").data("video-id") || "dQw4w9WgXcQ";
    $("#videoModal .youtube-modal-area").html('<iframe width="100%" height="480" style="border:none;" src="https://www.youtube.com/embed/' + vid + '?autoplay=1" allow="autoplay;encrypted-media" allowfullscreen></iframe>');
    $("#videoModal").modal("show");
  });

  $("#videoModal").on("hidden.bs.modal", function() {
    $(this).find(".youtube-modal-area").html("");
  });

  $(".playlist-item").on("click", function() {
    var vid = $(this).data("video-id"), title = $(this).data("video-title"), thumb = $(this).find(".playlist-thumb img").attr("src");
    $(".playlist-item").removeClass("active");
    $(this).addClass("active");
    $("#mainVideoContainer .main-video-thumb").attr("src", thumb).data("video-id", vid);
    $(".main-video-title").text(title);
  });

  // Search & Navigation
  $("#search-trigger").on("click", function(e) { e.preventDefault(); $("#searchPop").addClass("open"); });
  $("#closeSearch").on("click", function() { $("#searchPop").removeClass("open"); });
  $(document).on("keydown", function(e) { if(e.key === "Escape") $("#searchPop").removeClass("open"); });
  $("#closeNotif").on("click", function() { $("#notificationBar").slideUp(300); });
  $(".menu-icon").on("click", function() { $(".collapse-menu").addClass("show-hide-menu"); });
  $(".close-rt-pnl").on("click", function() { $(".collapse-menu").removeClass("show-hide-menu"); });

  // Mobile menu dropdown
  if ($(window).width() <= 1023) {
    $(".navbar-menu .nav-link").on("click", function(e) {
      if ($(this).siblings(".multi-drodown").length) {
        e.preventDefault();
        $(this).closest(".nav-item").toggleClass("active-toggle");
      }
    });
  }

  // Sticky Header & Logo Tab Auto-Hide on Scroll
  $(window).on("scroll", function() {
    if ($(this).scrollTop() > 40) {
      $(".header").addClass("scrolled");
    } else {
      $(".header").removeClass("scrolled");
    }
  }).trigger("scroll");
});
