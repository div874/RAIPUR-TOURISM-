/**
 * Video Section JavaScript
 * Handles video playlist, modal, and YouTube video playback
 */

jQuery(function ($) {

    // -------------------------------------------------------
    // Init: Set data-video-id on container from the img tag
    // (Fix Bug 1 & 2: main thumb video id not on container)
    // -------------------------------------------------------
    var initialVideoId = $('#mainVideoContainer').find('.main-video-thumb').data('video-id');
    if (initialVideoId) {
        $('#mainVideoContainer').attr('data-video-id', initialVideoId);
    }

    // -------------------------------------------------------
    // Playlist Item Click Handler
    // -------------------------------------------------------
    $('.playlist-item').on('click', function() {
        // Remove active class from all items
        $('.playlist-item').removeClass('active');
        // Add active class to clicked item
        $(this).addClass('active');

        // Get video data
        var videoId    = $(this).data('video-id');
        var videoTitle = $(this).data('video-title');
        var videoThumb = $(this).find('.playlist-thumb img').attr('src');

        // Update main video player
        $('#mainVideoContainer').find('.main-video-thumb').attr('src', videoThumb);
        $('#mainVideoContainer').attr('data-video-id', videoId);
        $('.main-video-title').text(videoTitle);
    });

    // -------------------------------------------------------
    // Function to stop video and clear modal
    // -------------------------------------------------------
    function stopVideoAndCloseModal() {
        var iframe = $('.youtube-modal-area iframe');
        if (iframe.length > 0) {
            iframe.attr('src', '');
        }
        $('.youtube-modal-area').html('');
    }

    // -------------------------------------------------------
    // Open Modal on Main Video Container Click
    // (Fix Bug 3: use pointer-events & touch on whole container)
    // -------------------------------------------------------
    $('#mainVideoContainer').on('click touchend', function(e) {
        e.preventDefault();
        e.stopPropagation();

        var videoId = $(this).attr('data-video-id');
        if (!videoId) return;

        var embeded_code = '<iframe width="100%" height="100%" ' +
            'src="https://www.youtube.com/embed/' + videoId +
            '?autoplay=1&rel=0" frameborder="0" ' +
            'allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" ' +
            'allowfullscreen></iframe>';

        $('.youtube-modal-area').html(embeded_code);
        $('#videoModal').modal('show');
    });

    // -------------------------------------------------------
    // Stop video when modal closes
    // -------------------------------------------------------
    $('#videoModal').on('hidden.bs.modal', function () {
        stopVideoAndCloseModal();
    });

    $('#videoModal').on('hide.bs.modal', function () {
        stopVideoAndCloseModal();
    });

    $('.close-youtube').on('click', function() {
        stopVideoAndCloseModal();
    });

    // Stop video when clicking on backdrop
    $(document).on('click touchend', '#videoModal', function(e) {
        if (e.target === this) {
            stopVideoAndCloseModal();
        }
    });
});
