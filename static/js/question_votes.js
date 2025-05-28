$(document).ready(function() {
    let isRequestPending = false;
    
    function getCSRFToken() {
    let csrfToken = null;
    const metaTag = document.querySelector('meta[name="csrf-token"]');
    if (metaTag) {
        csrfToken = metaTag.content;
    }
    if (!csrfToken) {
        const csrfInput = document.querySelector('input[name="csrfmiddlewaretoken"]');
        if (csrfInput) {
            csrfToken = csrfInput.value;
        }
    }
    if (!csrfToken) {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const [name, value] = cookie.trim().split('=');
            if (name === 'csrftoken') {
                csrfToken = value;
                break;
            }
        }
    } 
    return csrfToken;
}

const csrftoken = getCSRFToken();
if (!csrftoken) {
    console.error('CSRF token not found!');
}
    function handleVote(type, $button) {
        if (isRequestPending) return;
        const questionId = $button.data('question-id');
        const $questionBlock = $button.closest('.card');
        $button.prop('disabled', true).addClass('loading');
        isRequestPending = true;
        
        $.ajax({
            url: `/question/${questionId}/vote/`,
            type: 'POST',
            data: { type: type },
            headers: {
                "X-CSRFToken": csrftoken
            },
            success: function(data) {
                if (data.error) {
                    console.error('Error:', data.error);
                    return;
                }
                
                $questionBlock.find('.like-count').text(data.total_likes || 0);
                $questionBlock.find('.dislike-count').text(data.total_dislikes || 0);
                $questionBlock.find('.like-btn, .dislike-btn').removeClass('active');
                if (data.user_vote === true) {
                    $questionBlock.find('.like-btn').addClass('active');
                } else if (data.user_vote === false) {
                    $questionBlock.find('.dislike-btn').addClass('active');
                }
            },
            error: function(xhr) {
                console.error('Vote error:', xhr.responseText);
                if (xhr.status !== 500) {
                    alert('Произошла ошибка при обработке вашего голоса.');
                }
            },
            complete: function() {
                isRequestPending = false;
                $questionBlock.find('.like-btn, .dislike-btn').prop('disabled', false).removeClass('loading');
            }
        });
    }
    $(document).on('click', '.like-btn', function() {
        handleVote('like', $(this));
    });
    $(document).on('click', '.dislike-btn', function() {
        handleVote('dislike', $(this));
    });
});


