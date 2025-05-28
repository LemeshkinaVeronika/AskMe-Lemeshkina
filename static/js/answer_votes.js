$(document).ready(function() {
    const pendingRequests = {};
    
    function getCSRFToken() {
        const metaTag = document.querySelector('meta[name="csrf-token"]');
        if (metaTag && metaTag.content) {
            return metaTag.content;
        }
        
        const csrfInput = document.querySelector('input[name="csrfmiddlewaretoken"]');
        if (csrfInput && csrfInput.value) {
            return csrfInput.value;
        }
        
        const cookie = document.cookie.split(';').find(c => c.trim().startsWith('csrftoken='));
        if (cookie) {
            return cookie.split('=')[1];
        }
        
        console.error('CSRF token not found!');
        return null;
    }

    const csrftoken = getCSRFToken();
    if (!csrftoken) {
        console.error('CSRF token is missing! Voting will not work.');
        return;
    }

    function handleAnswerVote(type, $button) {
        const answerId = $button.data('answer-id');
        const buttonId = $button.attr('id');
        
        console.log(`Processing ${type} vote for answer ${answerId} (button: ${buttonId})`);
        
        if (pendingRequests[answerId]) {
            console.log(`Request for answer ${answerId} already in progress`);
            return;
        }
        const $voteBlock = $button.closest('.d-flex.gap-2.ps-4');
        $button.prop('disabled', true).addClass('loading');
        pendingRequests[answerId] = true;
        
        $.ajax({
            url: `/answer/${answerId}/vote/`,
            type: 'POST',
            data: { type: type },
            headers: {
                "X-CSRFToken": csrftoken
            },
            success: function(data) {
                console.log('Vote successful:', {
                    url: this.url,
                    response: data,
                    button: buttonId
                });
                
                if (data.error) {
                    console.error('Server error:', data.error);
                    return;
                }
                
                $voteBlock.find('.answer-like-count').text(data.total_likes || 0);
                $voteBlock.find('.answer-dislike-count').text(data.total_dislikes || 0);
                $voteBlock.find('.answer-like-btn, .answer-dislike-btn').removeClass('active');
                if (data.user_vote === true) {
                    $voteBlock.find('.answer-like-btn').addClass('active');
                } else if (data.user_vote === false) {
                    $voteBlock.find('.answer-dislike-btn').addClass('active');
                }
            },
            error: function(xhr, status, error) {
                console.error('Vote failed:', {
                    status: xhr.status,
                    error: error,
                    response: xhr.responseText,
                    button: buttonId
                });
                alert('Ошибка при голосовании. Пожалуйста, попробуйте позже.');
            },
            complete: function() {
                pendingRequests[answerId] = false;
                $button.prop('disabled', false).removeClass('loading');
            }
        });
    }

    function initVoteHandlers() {
        $(document)
            .off('click', '.answer-like-btn')
            .off('click', '.answer-dislike-btn');
        
        $(document)
            .on('click', '.answer-like-btn', function(e) {
                e.preventDefault();
                e.stopPropagation();
                e.stopImmediatePropagation();
                console.log('Like button clicked:', this.id);
                handleAnswerVote('like', $(this));
            })
            .on('click', '.answer-dislike-btn', function(e) {
                e.preventDefault();
                e.stopPropagation();
                e.stopImmediatePropagation();
                console.log('Dislike button clicked:', this.id);
                handleAnswerVote('dislike', $(this));
            });
        
        console.log('Vote handlers initialized');
    }

    initVoteHandlers();
    $(document).ajaxComplete(function() {
        console.log('AJAX request completed, reinitializing vote handlers');
        initVoteHandlers();
    });
});