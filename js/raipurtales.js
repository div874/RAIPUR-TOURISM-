jQuery(function($) {
  // Init Lucide icons
  if (typeof lucide !== 'undefined') {
    lucide.createIcons();
  }

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

  // Live AI Search Assistant powered by Qwen3.8 Max (xkiro API)
  (function initAiSearchAssistant() {
    var apiKey = "sk-xt-76c57fd259af55d2fc746eb295cff2f8d2a84be40e6216c7";
    var modelName = "qwen/qwen3.8-max:free";
    var apiUrl = "https://api.xkiro.com/v1/chat/completions";

    function getSmartFallbackResponse(query) {
      var q = query.toLowerCase();
      if (q.includes("turf") || q.includes("sport") || q.includes("cricket") || q.includes("football") || q.includes("play")) {
        return "For sports turfs and grounds in Raipur, check out <strong>Swami Vivekananda Turf</strong>, <strong>VIP Road Sports Arenas</strong>, or <strong>Netaji Subhash Stadium</strong> for cricket, football, and night matches!";
      } else if (q.includes("food") || q.includes("eat") || q.includes("farra") || q.includes("chila") || q.includes("sweet") || q.includes("restaurant") || q.includes("cafe")) {
        return "Raipur is renowned for authentic Chhattisgarhi delicacies like <strong>Farra</strong>, <strong>Chila</strong> with spicy garlic chutney, <strong>Bara</strong>, and <strong>Muthia</strong>. Visit <strong>Gole Bazaar</strong> and <strong>Telibandha Marine Drive</strong> for street food treats!";
      } else if (q.includes("sunset") || q.includes("lake") || q.includes("park") || q.includes("view") || q.includes("evening")) {
        return "Top sunset and lake spots in Raipur include <strong>Vivekananda Sarovar (Budha Talab)</strong> with its 37-ft statue, <strong>Telibandha Lake (Marine Drive)</strong>, and <strong>Urja Park</strong>.";
      } else if (q.includes("temple") || q.includes("history") || q.includes("heritage") || q.includes("museum") || q.includes("culture")) {
        return "Experience Raipur's rich heritage at the 17th-century <strong>Dudhadhari Math</strong>, <strong>Hatkeshwar Mahadev Temple</strong> (1402 AD), and the <strong>Mahant Ghasidas Memorial Museum</strong>.";
      } else if (q.includes("wildlife") || q.includes("safari") || q.includes("nature") || q.includes("zoo")) {
        return "Explore <strong>Nandan Van Jungle Safari</strong> in Naya Raipur (over 800 acres featuring Tiger, Lion, Bear & Herbivore safaris) or stroll through <strong>Purkhauti Muktangan</strong> open-air museum.";
      } else if (q.includes("stay") || q.includes("hotel") || q.includes("flight") || q.includes("airport") || q.includes("train") || q.includes("station")) {
        return "Raipur is easily accessible via <strong>Swami Vivekananda Airport (Mana)</strong> and <strong>Raipur Junction Railway Station</strong>. Premier stays and business hotels are clustered around VIP Road and GE Road.";
      } else {
        return "Hamara Raipur offers a wonderful blend of heritage and modern charm! You can explore <strong>Purkhauti Muktangan</strong> for open-air tribal culture, enjoy sunset views at <strong>Telibandha Lake</strong>, or try traditional <strong>Farra & Chila</strong> in Old Raipur.";
      }
    }

    function askAi(query, $textEl, $cardEl) {
      if (!query || !query.trim()) return;
      var cleanQuery = query.trim();

      $cardEl.slideDown(250);
      $textEl.html('<div class="rt-ai-loading"><span class="rt-ai-pulse"></span> Asking Hamara Raipur AI...</div>');

      var systemPrompt = "You are Hamara Raipur AI, a highly knowledgeable, precise local guide for Raipur, Chhattisgarh. Answer the user prompt with exact, highly specific details about Raipur (such as real sports turfs, food spots, places, events, or local advice). Provide a clear, detailed, and accurate response (2 to 4 sentences).";

      var controller = typeof AbortController !== 'undefined' ? new AbortController() : null;
      var timeoutId = controller ? setTimeout(function() { controller.abort(); }, 4000) : null;

      fetch(apiUrl, {
        method: "POST",
        headers: {
          "Authorization": "Bearer " + apiKey,
          "Content-Type": "application/json"
        },
        signal: controller ? controller.signal : undefined,
        body: JSON.stringify({
          model: modelName,
          messages: [
            { role: "system", content: systemPrompt },
            { role: "user", content: cleanQuery }
          ],
          max_tokens: 350
        })
      })
      .then(function(res) {
        if (timeoutId) clearTimeout(timeoutId);
        if (!res.ok) throw new Error("API request error " + res.status);
        return res.json();
      })
      .then(function(data) {
        if (data && data.choices && data.choices[0] && data.choices[0].message) {
          var rawAnswer = data.choices[0].message.content.trim();
          var formattedAnswer = rawAnswer.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
          $textEl.html(formattedAnswer);
        } else {
          $textEl.html(getSmartFallbackResponse(cleanQuery));
        }
      })
      .catch(function(err) {
        if (timeoutId) clearTimeout(timeoutId);
        console.warn("AI API unavailable, using smart local fallback:", err);
        $textEl.html(getSmartFallbackResponse(cleanQuery));
      });
    }

    // Hero Search Button & Enter Key
    $(".rt-ai-search-btn").on("click", function(e) {
      var query = $("#heroSearchInput").val();
      if (query && query.trim()) {
        e.preventDefault();
        askAi(query, $("#heroAiResponseText"), $("#heroAiResponse"));
      }
    });

    $("#heroSearchInput").on("keydown", function(e) {
      if (e.key === "Enter") {
        e.preventDefault();
        var query = $(this).val();
        askAi(query, $("#heroAiResponseText"), $("#heroAiResponse"));
      }
    });

    // Suggestion Chips
    $(".btn-suggest-chip").on("click", function(e) {
      e.preventDefault();
      var query = $(this).data("query") || $(this).text();
      $("#heroSearchInput").val(query);
      askAi(query, $("#heroAiResponseText"), $("#heroAiResponse"));
    });

    // Hero Close AI Answer Card
    $("#closeHeroAiResponse").on("click", function() {
      $("#heroAiResponse").slideUp(200);
    });

    // Modal Search Bar
    $("#searchPop form").on("submit", function(e) {
      var query = $("#keyword").val();
      if (query && query.trim()) {
        e.preventDefault();
        askAi(query, $("#modalAiResponseText"), $("#modalAiResponse"));
      }
    });
  })();

  // Dynamic Events Loader from events.json with Live Search & Tabs
  (function loadDynamicEvents() {
    var $grid = $("#eventsContainer");
    if (!$grid.length) return;

    var allEventsData = [];

    function createCardHtml(ev) {
      var cat = (ev.category || "").toLowerCase();
      var dataTab = cat.includes("garba") || cat.includes("activity") ? "garba" : "comedy";
      var linkUrl = ev.link || "https://in.bookmyshow.com/explore/events-raipur";
      var posterImg = ev.image || "images/tribal_dance.jpg";
      var dateText = ev.date && ev.date !== "Upcoming · Check BookMyShow" ? ev.date : "Upcoming Event";
      var venueText = ev.venue || "Raipur Venue / Cultural Center";

      var cardHtml = '<div class="col-lg-4 col-md-6 mb-4">';
      cardHtml += '  <div class="rt-modern-card" data-tab="' + dataTab + '">';
      cardHtml += '    <div class="rt-modern-poster-wrap">';
      cardHtml += '      <span class="rt-modern-badge"><i class="fa-regular fa-calendar-check"></i> UPCOMING</span>';
      cardHtml += '      <img src="' + posterImg + '" alt="' + ev.title + '" onerror="this.src=\'images/tribal_dance.jpg\'">';
      cardHtml += '    </div>';
      cardHtml += '    <div class="rt-modern-body">';
      cardHtml += '      <h3 class="rt-modern-title">' + ev.title + '</h3>';
      
      // Date Row
      cardHtml += '      <div class="rt-modern-info-row">';
      cardHtml += '        <div class="rt-modern-icon-box"><i class="fa-regular fa-calendar-days"></i></div>';
      cardHtml += '        <div class="rt-modern-info-text">';
      cardHtml += '          <strong>' + dateText + '</strong>';
      cardHtml += '          <span>Evening onwards</span>';
      cardHtml += '        </div>';
      cardHtml += '      </div>';

      // Location Row
      cardHtml += '      <div class="rt-modern-info-row">';
      cardHtml += '        <div class="rt-modern-icon-box location-icon"><i class="fa-solid fa-location-dot"></i></div>';
      cardHtml += '        <div class="rt-modern-info-text">';
      cardHtml += '          <strong>' + venueText + '</strong>';
      cardHtml += '          <span>Raipur, Chhattisgarh</span>';
      cardHtml += '        </div>';
      cardHtml += '      </div>';

      // Description Paragraph
      cardHtml += '      <p class="rt-modern-desc">' + (ev.description || "Live event in Raipur. Get tickets directly on BookMyShow.") + '</p>';

      // Platform Specific Booking Button
      var sourceName = ev.source || "BookMyShow";
      var buttonText = sourceName.indexOf("Google") !== -1 ? "View details on Google Search" : "Book tickets on " + sourceName;

      cardHtml += '      <a href="' + linkUrl + '" target="_blank" rel="noopener" class="btn-book-bms">';
      cardHtml += '        <span><i class="fa-solid fa-ticket me-2"></i> ' + buttonText + '</span>';
      cardHtml += '        <i class="fa-solid fa-arrow-right"></i>';
      cardHtml += '      </a>';

      // Find a Group / Join Community Button
      cardHtml += '      <button type="button" class="btn-find-group btn-open-group-modal" data-event-title="' + ev.title.replace(/"/g, '&quot;') + '">';
      cardHtml += '        <i class="fa-solid fa-users text-success me-1"></i> Find a Group / Join Community';
      cardHtml += '      </button>';

      cardHtml += '    </div>';
      cardHtml += '  </div>';
      cardHtml += '</div>';

      return cardHtml;
    }

    function renderEvents(list) {
      if (!list || !list.length) {
        $grid.html('<div class="col-12 text-center py-5"><p class="text-muted fs-5">No events found matching your search query.</p></div>');
        $("#eventsCountBadge").html('<i class="fa-solid fa-ticket me-1"></i> 0 Events Found');
        return;
      }

      $("#eventsCountBadge").html('<i class="fa-solid fa-ticket me-1"></i> ' + list.length + ' Live Events (BMS, District & Google)');

      var cardsHtml = "";
      list.forEach(function(ev) {
        cardsHtml += createCardHtml(ev);
      });

      $grid.html('<div class="row g-4">' + cardsHtml + '</div>');
    }

    fetch("events.json")
      .then(function(res) {
        if (!res.ok) throw new Error("Could not load events.json");
        return res.json();
      })
      .then(function(eventsList) {
        allEventsData = eventsList || [];
        renderEvents(allEventsData);
      })
      .catch(function(err) {
        console.log("Using default events grid:", err);
      });

    // Search filter input listener
    $("#eventSearchInput").on("input", function() {
      var query = $(this).val().toLowerCase().trim();
      var activeTab = $(".rt-event-tab-btn.active").data("tab") || "all";
      var filtered = allEventsData.filter(function(ev) {
        var matchesSearch = (ev.title || "").toLowerCase().includes(query) ||
                            (ev.venue || "").toLowerCase().includes(query) ||
                            (ev.category || "").toLowerCase().includes(query);

        var cat = (ev.category || "").toLowerCase();
        var matchesTab = true;
        if (activeTab === "garba") matchesTab = cat.includes("garba") || cat.includes("activity");
        if (activeTab === "comedy") matchesTab = !cat.includes("garba") && !cat.includes("activity");

        return matchesSearch && matchesTab;
      });
      renderEvents(filtered);
    });

    // Tab filter listener
    $(".rt-event-tab-btn").on("click", function() {
      $(".rt-event-tab-btn").removeClass("active");
      $(this).addClass("active");
      var tab = $(this).data("tab");
      var query = $("#eventSearchInput").val().toLowerCase().trim();

      var filtered = allEventsData.filter(function(ev) {
        var matchesSearch = !query || (ev.title || "").toLowerCase().includes(query) ||
                            (ev.venue || "").toLowerCase().includes(query) ||
                            (ev.category || "").toLowerCase().includes(query);

        var cat = (ev.category || "").toLowerCase();
        var matchesTab = true;
        if (tab === "garba") matchesTab = cat.includes("garba") || cat.includes("activity");
        if (tab === "comedy") matchesTab = !cat.includes("garba") && !cat.includes("activity");

        return matchesSearch && matchesTab;
      });

      renderEvents(filtered);
    });
  })();

  // Community Event Groups & Live Chat Manager
  (function initCommunityEventGroups() {
    var activeEventTitle = "";
    var activeGroupId = null;

    function getStorageKey(title) {
      return "rt_groups_" + encodeURIComponent(title.toLowerCase().trim());
    }

    function getDefaultGroups(title) {
      return [
        {
          id: "g1_" + Date.now(),
          name: title + " — Squad Raipur",
          leader: "Rahul Sharma",
          membersCount: 6,
          description: "Heading together around 7:30 PM! Anyone from Civil Lines / Shankar Nagar welcome.",
          messages: [
            { sender: "Rahul Sharma", text: "Hey everyone! We are meeting near the main gate at 7:30 PM.", time: "18:30", isMe: false },
            { sender: "Priya S.", text: "Awesome! I am coming with 2 friends.", time: "18:45", isMe: false }
          ]
        },
        {
          id: "g2_" + Date.now(),
          name: "Carpool & Ride Sharing (Marine Drive)",
          leader: "Amit Verma",
          membersCount: 4,
          description: "Pooling cabs from Telibandha Marine Drive at 6:45 PM. 2 spots open!",
          messages: [
            { sender: "Amit Verma", text: "Starting from Marine Drive at 6:45 PM. Message if you want to share a cab!", time: "17:15", isMe: false }
          ]
        }
      ];
    }

    function loadGroups(title) {
      try {
        var raw = localStorage.getItem(getStorageKey(title));
        if (raw) return JSON.parse(raw);
      } catch (e) {}
      var defaults = getDefaultGroups(title);
      saveGroups(title, defaults);
      return defaults;
    }

    function saveGroups(title, groups) {
      try {
        localStorage.setItem(getStorageKey(title), JSON.stringify(groups));
      } catch (e) {}
    }

    function renderGroupsList(title) {
      var groups = loadGroups(title);
      var $container = $("#activeGroupsContainer");

      if (!groups.length) {
        $container.html('<div class="text-center py-4"><p class="text-muted">No groups created yet. Be the first to start a group for this event!</p></div>');
        return;
      }

      var html = "";
      groups.forEach(function(g) {
        html += '<div class="rt-group-card d-flex justify-content-between align-items-center flex-wrap gap-2">';
        html += '  <div>';
        html += '    <h6 class="fw-bold text-dark mb-1"><i class="fa-solid fa-users-line text-success me-2"></i>' + g.name + '</h6>';
        html += '    <p class="small text-muted mb-2">' + g.description + '</p>';
        html += '    <small class="badge bg-light text-dark border"><i class="fa-solid fa-user-group text-primary me-1"></i> ' + g.membersCount + ' Members · Leader: ' + g.leader + '</small>';
        html += '  </div>';
        html += '  <button class="btn btn-sm btn-success rounded-pill px-4 fw-bold btn-join-group" data-group-id="' + g.id + '">';
        html += '    Join & Chat <i class="fa-solid fa-comments ms-1"></i>';
        html += '  </button>';
        html += '</div>';
      });

      $container.html(html);
    }

    function renderChatView(group) {
      $("#chatGroupName").text(group.name);
      $("#chatGroupMembersCount").html('<i class="fa-solid fa-circle text-success me-1" style="font-size: 8px;"></i> ' + group.membersCount + ' Members Online · Leader: ' + group.leader);

      var msgsHtml = "";
      if (group.messages && group.messages.length) {
        group.messages.forEach(function(m) {
          var meClass = m.isMe ? " my-msg ms-auto" : "";
          msgsHtml += '<div class="rt-chat-bubble' + meClass + '" style="max-width: 80%;">';
          msgsHtml += '  <div class="d-flex justify-content-between align-items-center mb-1">';
          msgsHtml += '    <small class="fw-bold text-success">' + m.sender + '</small>';
          msgsHtml += '    <small class="text-muted" style="font-size: 10px;">' + (m.time || "Just now") + '</small>';
          msgsHtml += '  </div>';
          msgsHtml += '  <p class="m-0 text-dark small">' + m.text + '</p>';
          msgsHtml += '</div>';
        });
      } else {
        msgsHtml = '<div class="text-center py-4 text-muted small">No messages in group chat yet. Say hi to start the conversation!</div>';
      }

      $("#chatMessagesContainer").html(msgsHtml);

      // Scroll to bottom
      var box = document.getElementById("chatMessagesContainer");
      if (box) box.scrollTop = box.scrollHeight;
    }

    // Open Modal Listener
    $(document).on("click", ".btn-open-group-modal", function(e) {
      e.preventDefault();
      activeEventTitle = $(this).data("event-title") || "Raipur Event";
      $("#eventGroupModalTitle").text(activeEventTitle);
      
      // Reset view to Group List
      $("#createGroupFormCard").hide();
      $("#groupChatView").hide();
      $("#groupListView").show();

      renderGroupsList(activeEventTitle);

      var modal = new bootstrap.Modal(document.getElementById("eventGroupModal"));
      modal.show();
    });

    // Toggle Create Group Form
    $("#btnToggleCreateGroup").on("click", function() {
      $("#createGroupFormCard").slideToggle(200);
    });

    $("#btnCancelCreateGroup").on("click", function() {
      $("#createGroupFormCard").slideUp(200);
    });

    // Create Group Form Submit
    $("#formCreateGroup").on("submit", function(e) {
      e.preventDefault();
      var gName = $("#inputGroupName").val().trim();
      var leader = $("#inputLeaderName").val().trim();
      var msg = $("#inputGroupMsg").val().trim();

      if (!gName || !leader) return;

      var groups = loadGroups(activeEventTitle);
      var nowStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

      var newGroup = {
        id: "g_" + Date.now(),
        name: gName,
        leader: leader,
        membersCount: 1,
        description: msg,
        messages: [
          { sender: leader, text: msg, time: nowStr, isMe: true }
        ]
      };

      groups.unshift(newGroup);
      saveGroups(activeEventTitle, groups);

      $("#formCreateGroup")[0].reset();
      $("#createGroupFormCard").slideUp(200);

      renderGroupsList(activeEventTitle);
    });

    // Join & Chat Button Listener
    $(document).on("click", ".btn-join-group", function() {
      activeGroupId = $(this).data("group-id");
      var groups = loadGroups(activeEventTitle);
      var group = groups.find(function(g) { return g.id === activeGroupId; });

      if (group) {
        $("#groupListView").hide();
        $("#groupChatView").fadeIn(200);
        renderChatView(group);
      }
    });

    // Back to Groups List
    $("#btnBackToGroups").on("click", function() {
      $("#groupChatView").hide();
      $("#groupListView").fadeIn(200);
      renderGroupsList(activeEventTitle);
    });

    // Send Chat Message Form Submit
    $("#formSendChatMessage").on("submit", function(e) {
      e.preventDefault();
      var text = $("#inputChatMessage").val().trim();
      if (!text || !activeGroupId) return;

      var groups = loadGroups(activeEventTitle);
      var group = groups.find(function(g) { return g.id === activeGroupId; });

      if (group) {
        var nowStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        group.messages = group.messages || [];
        group.messages.push({
          sender: "You (Member)",
          text: text,
          time: nowStr,
          isMe: true
        });

        saveGroups(activeEventTitle, groups);
        $("#inputChatMessage").val("");
        renderChatView(group);
      }
    });
  })();

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

  // ScrollExpand Hero Component (React Bits Port to Vanilla JS)
  (function initScrollExpand() {
    var root = document.getElementById("heroScrollExpand");
    var track = document.getElementById("scrollExpandTrack");
    var stage = document.getElementById("scrollExpandStage");
    var frame = document.getElementById("scrollExpandFrame");
    var media = frame ? frame.querySelector(".rt-scroll-expand-media") : null;
    var title = document.getElementById("scrollExpandTitle");
    var hint = document.getElementById("scrollExpandHint");
    var overlay = document.getElementById("scrollExpandOverlay");
    var scrim = document.getElementById("scrollExpandScrim");
    var searchOverlay = document.getElementById("heroSearchOverlay");
    var leftScrim = document.getElementById("heroLeftScrim");
    var editorial = document.getElementById("heroEditorial");
    var eyebrowEl = editorial ? editorial.querySelector(".rt-hero-eyebrow") : null;
    var headlineEl = editorial ? editorial.querySelector(".rt-hero-headline") : null;
    var taglineEl = editorial ? editorial.querySelector(".rt-hero-tagline") : null;
    var heroSubEl = editorial ? editorial.querySelector(".rt-hero-sub") : null;
    var weatherWidget = document.getElementById("heroWeatherWidget");

    if (!root || !track || !stage || !frame || !media) return;

    var startWidth = 40; // %
    var startHeight = 40; // %
    var startRadius = 24; // px
    var endRadius = 0; // px
    var mediaZoom = 1.08;
    var scrollDistance = 0.55;
    var holdDistance = 0.0;
    var overlayScrim = 0.45;

    var current = 0;
    var target = 0;
    var running = false;

    function clamp(v, min, max) {
      return v < min ? min : v > max ? max : v;
    }

    function smoothstep(edge0, edge1, x) {
      var t = clamp((x - edge0) / (edge1 - edge0 || 1e-6), 0, 1);
      return t * t * (3 - 2 * t);
    }

    function measure() {
      var stageH = window.innerHeight;
      stage.style.height = stageH + "px";
      track.style.height = (stageH * (1 + scrollDistance + holdDistance)) + "px";
    }

    function applyProgress(p) {
      var e = smoothstep(0, 1, p);
      var w = startWidth + (100 - startWidth) * e;
      var h = startHeight + (100 - startHeight) * e;
      var ix = Math.max(0, (100 - w) / 2);
      var iy = Math.max(0, (100 - h) / 2);
      var r = startRadius + (endRadius - startRadius) * e;

      frame.style.clipPath = "inset(" + iy.toFixed(3) + "% " + ix.toFixed(3) + "% " + iy.toFixed(3) + "% " + ix.toFixed(3) + "% round " + r.toFixed(1) + "px)";
      media.style.transform = "scale(" + (mediaZoom + (1 - mediaZoom) * e).toFixed(4) + ")";

      if (scrim) {
        scrim.style.opacity = (overlayScrim * e).toFixed(3);
      }

      if (title) {
        var out = smoothstep(0.3, 0.85, p);
        title.style.opacity = (1 - out).toFixed(3);
        title.style.transform = "translate3d(0, " + (-36 * out).toFixed(1) + "px, 0) scale(" + (1 + 0.06 * out).toFixed(3) + ")";
      }

      if (hint) {
        var gone = smoothstep(0, 0.15, p);
        hint.style.opacity = (1 - gone).toFixed(3);
        hint.style.transform = "translate3d(0, " + (12 * gone).toFixed(1) + "px, 0)";
      }

      if (overlay) {
        var inn = smoothstep(0.72, 1, p);
        overlay.style.opacity = inn.toFixed(3);
        overlay.style.transform = "translate3d(0, " + (20 * (1 - inn)).toFixed(1) + "px, 0)";
      }

      if (searchOverlay) {
        var srch = smoothstep(0.80, 1, p);
        searchOverlay.style.opacity = srch.toFixed(3);
        searchOverlay.style.transform = "translateY(" + (24 * (1 - srch)).toFixed(1) + "px)";
        searchOverlay.style.pointerEvents = srch > 0.5 ? "auto" : "none";
      }

      if (leftScrim) {
        leftScrim.style.opacity = smoothstep(0.65, 0.95, p).toFixed(3);
      }

      if (editorial) {
        var editFade = smoothstep(0.72, 0.96, p);
        editorial.style.opacity = editFade.toFixed(3);
        editorial.style.pointerEvents = editFade > 0.5 ? "auto" : "none";
        editorial.style.transform = "translateY(" + (20 * (1 - editFade)).toFixed(1) + "px)";
      }

      if (eyebrowEl) {
        var ewFade = smoothstep(0.72, 0.88, p);
        eyebrowEl.style.opacity = ewFade.toFixed(3);
        eyebrowEl.style.transform = "translateY(" + (10 * (1 - ewFade)).toFixed(1) + "px)";
      }

      if (headlineEl) {
        var hlFade = smoothstep(0.76, 0.93, p);
        headlineEl.style.opacity = hlFade.toFixed(3);
        headlineEl.style.transform = "translateY(" + (16 * (1 - hlFade)).toFixed(1) + "px)";
      }

      if (taglineEl) {
        var tgFade = smoothstep(0.80, 0.96, p);
        taglineEl.style.opacity = tgFade.toFixed(3);
        taglineEl.style.transform = "translateY(" + (12 * (1 - tgFade)).toFixed(1) + "px)";
      }

      if (heroSubEl) {
        var hsFade = smoothstep(0.84, 1.0, p);
        heroSubEl.style.opacity = hsFade.toFixed(3);
        heroSubEl.style.transform = "translateY(" + (12 * (1 - hsFade)).toFixed(1) + "px)";
      }

      if (weatherWidget) {
        var wFade = smoothstep(0.72, 0.96, p);
        weatherWidget.style.opacity = wFade.toFixed(3);
        weatherWidget.style.pointerEvents = wFade > 0.5 ? "auto" : "none";
        weatherWidget.style.transform = "translateY(" + (20 * (1 - wFade)).toFixed(1) + "px)";
      }
    }

    var hasExpanded = false;
    var lastScrollY = window.pageYOffset || document.documentElement.scrollTop;
    var snapTimer = null;
    var isSnapping = false;

    function readProgress() {
      if (hasExpanded) return 1.0;
      var stageH = window.innerHeight;
      var span = stageH * Math.max(0.01, scrollDistance);
      var top = track.getBoundingClientRect().top;
      var p = clamp(-top / span, 0, 1);
      if (p >= 0.95) {
        hasExpanded = true;
        return 1.0;
      }
      return p;
    }

    function customSmoothScrollTo(targetY, duration, callback) {
      isSnapping = true;
      var startY = window.pageYOffset || document.documentElement.scrollTop;
      var distance = targetY - startY;
      var startTime = null;

      function cubicEaseInOut(t) {
        return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
      }

      function step(currentTime) {
        if (!startTime) startTime = currentTime;
        var elapsed = currentTime - startTime;
        var progress = Math.min(elapsed / duration, 1);
        var ease = cubicEaseInOut(progress);

        window.scrollTo(0, startY + distance * ease);

        if (elapsed < duration) {
          requestAnimationFrame(step);
        } else {
          isSnapping = false;
          if (callback) callback();
        }
      }

      requestAnimationFrame(step);
    }

    function triggerExpand() {
      if (hasExpanded || isSnapping) return;
      var stageH = window.innerHeight;
      var span = stageH * Math.max(0.01, scrollDistance);
      var trackTop = track.offsetTop;
      
      customSmoothScrollTo(trackTop + span, 850, function() {
        hasExpanded = true;
      });
    }

    function tick() {
      var k = 0.16; // Fluid responsive lerp speed
      current += (target - current) * k;
      if (Math.abs(target - current) < 0.0004) {
        current = target;
        running = false;
      }
      applyProgress(current);
      if (running) {
        requestAnimationFrame(tick);
      }
    }

    function onScroll() {
      if (hasExpanded) {
        applyProgress(1.0);
        return;
      }
      var currentY = window.pageYOffset || document.documentElement.scrollTop;
      target = readProgress();

      if (!running) {
        running = true;
        requestAnimationFrame(tick);
      }

      // Auto-trigger smooth expansion if user scrolls down slightly
      if (!isSnapping && currentY > lastScrollY && target > 0.02 && target < 0.95) {
        clearTimeout(snapTimer);
        snapTimer = setTimeout(triggerExpand, 40);
      }

      lastScrollY = currentY;
    }

    function onResize() {
      measure();
      target = readProgress();
      if (hasExpanded) target = 1.0;
      current = target;
      applyProgress(current);
    }

    measure();
    onResize();

    window.addEventListener("scroll", onScroll, { passive: true });
    window.addEventListener("resize", onResize);

    // Instant wheel gesture trigger for smooth 1.4s expansion
    window.addEventListener("wheel", function(e) {
      if (hasExpanded || isSnapping) return;
      var currentP = readProgress();

      if (e.deltaY > 5 && currentP < 0.92) {
        triggerExpand();
      }
    }, { passive: true });
  })();

  // Live Weather Integration for Raipur, Chhattisgarh
  (function initRaipurWeather() {
    var lat = 21.2514;
    var lon = 81.6296;
    var cacheKey = "rt_raipur_weather_v1";
    var cacheTTL = 15 * 60 * 1000; // 15 mins cache

    var tempEl = document.getElementById("weatherTemp");
    var condEl = document.getElementById("weatherCond");
    var feelsEl = document.getElementById("weatherFeels");
    var hlEl = document.getElementById("weatherHL");
    var contextEl = document.getElementById("weatherContext");
    var iconWrapEl = document.getElementById("weatherIconWrap");
    var widgetEl = document.getElementById("heroWeatherWidget");

    if (!tempEl || !condEl) return;

    function getWeatherInfo(code, temp) {
      // WMO Weather interpretation codes
      if (code === 0) {
        return { icon: "sun", text: "Clear", context: temp > 32 ? "Warm afternoon ahead." : "Clear skies over Raipur." };
      } else if (code === 1 || code === 2) {
        return { icon: "cloud-sun", text: "Partly Cloudy", context: "Good day to explore." };
      } else if (code === 3) {
        return { icon: "cloud", text: "Overcast", context: "Pleasant breeze over Raipur." };
      } else if (code >= 45 && code <= 48) {
        return { icon: "cloud-fog", text: "Foggy", context: "Hazy morning in Raipur." };
      } else if ((code >= 51 && code <= 67) || (code >= 80 && code <= 82)) {
        return { icon: "cloud-rain", text: "Rain Showers", context: "Carry an umbrella today." };
      } else if (code >= 95 && code <= 99) {
        return { icon: "cloud-lightning", text: "Thunderstorm", context: "Stay indoors & stay safe." };
      } else {
        return { icon: "cloud-sun", text: "Passing Clouds", context: "Good day to explore." };
      }
    }

    function renderWeatherData(data) {
      try {
        var current = data.current;
        var daily = data.daily;
        var temp = Math.round(current.temperature_2m);
        var feels = Math.round(current.apparent_temperature);
        var code = current.weather_code;
        var maxTemp = Math.round(daily.temperature_2m_max[0]);
        var minTemp = Math.round(daily.temperature_2m_min[0]);
        var info = getWeatherInfo(code, temp);

        tempEl.textContent = temp + "°C";
        condEl.textContent = info.text;
        feelsEl.textContent = "Feels like " + feels + "°C";
        hlEl.textContent = "H: " + maxTemp + "°   L: " + minTemp + "°";
        contextEl.innerHTML = "<span>" + info.context + "</span>";

        if (iconWrapEl) {
          iconWrapEl.innerHTML = '<i data-lucide="' + info.icon + '" class="rt-weather-icon"></i>';
          if (typeof lucide !== 'undefined') {
            lucide.createIcons();
          }
        }

        // Accessibility label
        if (widgetEl) {
          widgetEl.setAttribute("aria-label", "Current weather in Raipur: " + temp + " degrees Celsius, " + info.text.toLowerCase() + ".");
        }
      } catch (err) {
        showErrorState();
      }
    }

    function showErrorState() {
      if (tempEl) tempEl.textContent = "--°C";
      if (condEl) condEl.textContent = "Weather unavailable";
      if (feelsEl) feelsEl.textContent = "Unable to fetch live data";
      if (hlEl) hlEl.textContent = "";
      if (contextEl) contextEl.innerHTML = "<span>Check back shortly</span>";
    }

    // Try cache first
    try {
      var cached = localStorage.getItem(cacheKey);
      if (cached) {
        var parsed = JSON.parse(cached);
        if (parsed.timestamp && (Date.now() - parsed.timestamp < cacheTTL) && parsed.data) {
          renderWeatherData(parsed.data);
          return;
        }
      }
    } catch (e) {
      // Ignore storage errors
    }

    // Fetch live weather data asynchronously from Open-Meteo for Raipur (21.2514, 81.6296)
    var apiUrl = "https://api.open-meteo.com/v1/forecast?latitude=" + lat + "&longitude=" + lon + "&current=temperature_2m,apparent_temperature,weather_code&daily=temperature_2m_max,temperature_2m_min&timezone=Asia%2FKolkata";

    fetch(apiUrl)
      .then(function(response) {
        if (!response.ok) throw new Error("Network response was not ok");
        return response.json();
      })
      .then(function(data) {
        if (data && data.current && data.daily) {
          renderWeatherData(data);
          try {
            localStorage.setItem(cacheKey, JSON.stringify({
              timestamp: Date.now(),
              data: data
            }));
          } catch (e) {}
        } else {
          showErrorState();
        }
      })
      .catch(function() {
        showErrorState();
      });
  })();
});
