const djangoVars = document.getElementById('django-variables').dataset;

const loadOldMessagesUrl = djangoVars.loadOldMessagesUrl;
const sendMessageUrl = djangoVars.sendMessageUrl;
const checkNewMessagesUrl = djangoVars.checkNewMessagesUrl;
const getNewMessagesUrl = djangoVars.getNewMessagesUrl;
const updateContactsUrl = djangoVars.updateContactsUrl;
const homeUrl = djangoVars.homeUrl;
const username = djangoVars.userUsername;
const chatUser = djangoVars.chatUser;
const groupId = djangoVars.groupId;
const loadOldPostsUrl = djangoVars.loadOldPostsUrl;
const publishPostUrl = djangoVars.publishPostUrl;
const checkNewPostsUrl = djangoVars.checkNewPostsUrl;
const getNewPostsUrl = djangoVars.getNewPostsUrl;
const updateGroupsUrl = djangoVars.updateGroupsUrl;

$(function() {
    const messageTextarea = document.getElementById('message-input');
    if (messageTextarea) {
        messageTextarea.addEventListener('input', () => {
            messageTextarea.style.height = 'auto';
            const newHeight = Math.min(messageTextarea.scrollHeight, 120);
            messageTextarea.style.height = `${newHeight}px`;
        });
    }

    const postTextarea = document.getElementById('post-input');
    if (postTextarea) {
        postTextarea.addEventListener('input', () => {
            postTextarea.style.height = 'auto';
            const newHeight = Math.min(postTextarea.scrollHeight, 120);
            postTextarea.style.height = `${newHeight}px`;
        });
    }

    let offset = $('#chat-messages .message').length;
    const limit = 20;
    let lastMessageTime = 0;
    let lastPostTime = 0;

    function isUserAtBottom() {
        const chatMessages = $('#chat-messages')[0];
        return chatMessages.scrollHeight - chatMessages.scrollTop <= chatMessages.clientHeight + 250;
    }

    function loadOldMessages() {
        let $oldestMessage = $('#chat-messages .message').first();
        let oldestMessageTimestamp = $oldestMessage.attr('data-timestamp');
        let oldestMessageId = parseInt($oldestMessage.attr('data-id'), 10);

        if (!oldestMessageTimestamp) {
            return;
        }

        $.ajax({
            url: loadOldMessagesUrl,
            type: 'GET',
            data: {
                'before_timestamp': oldestMessageTimestamp,
                'before_id': oldestMessageId,
                'limit': limit
            },
            success: function(response) {
                const messages = response.messages;
                if (messages.length > 0) {
                    let scrollHeightBefore = $('#chat-messages')[0].scrollHeight;
                    let scrollTopBefore = $('#chat-messages').scrollTop();

                    messages.forEach(function(message) {
                        if ($('#chat-messages .message[data-id="' + message.id + '"]').length === 0) {
                            let senderClass = message.sender === username ? 'from-user' : 'from-contact';
                            let messageHtml = `<div class="message ${senderClass}" data-timestamp="${message.timestamp}" data-id="${message.id}">`;
                            if (message.image_url) {
                                messageHtml += `<img src="${message.image_url}" width="200">`;
                            }
                            if (message.content) {
                                messageHtml += `<p>${message.content}</p>`;
                            }
                            messageHtml += `</div>`;

                            if (message.sender === username){
                                $('#chat-messages').prepend(`<a class="pop_message_link" href="/home/pop_message/${message.id}/?chat_with=${message.chat_user}">Delete message</a>`);
                            }
                            $('#chat-messages').prepend(messageHtml);


                        }
                    });

                    let scrollHeightAfter = $('#chat-messages')[0].scrollHeight;
                    $('#chat-messages').scrollTop(scrollTopBefore + (scrollHeightAfter - scrollHeightBefore));
                } else {
                    $('#chat-messages').off('scroll');
                }
            },
            error: function(xhr, status, error) {
                console.log("Error loading old messages: ", error);
            }
        });
    }

    $('#chat-messages').on('scroll', function() {
        if ($(this).scrollTop() === 0) {
            loadOldMessages();
        }
    });

    $('#message-input').on('keydown', function(event) {
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault();
            $('#send-message-form').submit();
            $('#message-input').css('height', 'auto');
        }
    });

    $('#post-input').on('keydown', function(event) {
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault();
            $('#publish-post-form').submit();
            $('#post-input').css('height', 'auto');
        }
    });

    function scrollToBottom() {
        $('#chat-messages').animate({ scrollTop: $('#chat-messages')[0].scrollHeight }, 300);
    }

    scrollToBottom();

    $('#send-message-form').on('submit', function(event) {
        event.preventDefault();

        const messageContent = $('#message-input').val().trim();
        const imageInput = $('#image-input')[0].files[0];

        if (!messageContent && !imageInput) {
            alert("You cannot send an empty message.");
            return;
        }

        if (messageContent.length > 5000) {
            alert("The message is too long. The maximum length is 5000 characters.");
            return;
        }

        const now = Date.now();
        if (now - lastMessageTime < 1000) {
            alert("You are sending messages too frequently. Please wait a bit.");
            return;
        }

        lastMessageTime = now;

        const formData = new FormData(this);

        $.ajax({
            url: sendMessageUrl,
            type: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            success: function(response) {
                if (response.status === 'success') {
                    const messageContent = $('#message-input').val();
                    const imageInput = $('#image-input')[0].files[0];

                    let messageHtml = `<div class="message from-user" data-timestamp="${response.timestamp}" data-id="${response.id}">`;
                    if (imageInput) {
                        messageHtml += `<img src="${URL.createObjectURL(imageInput)}" width="200">`;
                    }
                    if (messageContent  && messageContent.replace(/<\/?(b|i|u)>/g, '').length) {
                        messageHtml += `<p>${messageContent}</p>`;
                    }
                    messageHtml += `</div>`;


                    $('#chat-messages').append(messageHtml);
                    $('#chat-messages').append(`<a class="pop_message_link" href="/home/pop_message/${response.id}/?chat_with=${response.chat_user}">Delete message</a>`);

                    $('#message-input').val('');
                    $('#message-input').css('height', 'auto');
                    $('#image-input').val('');

                    scrollToBottom();
                } else {
                    alert(response.message || "Error sending message.");
                }
            },
            error: function(xhr, status, error) {
                console.log("Error sending message: ", error);
            }
        });
    });

    function checkNewMessages() {
        $.ajax({
            url: checkNewMessagesUrl,
            type: 'GET',
            success: function(response) {
                $('.notification-dot').hide();
                response.contacts_with_unread.forEach(function(contact) {
                    if (contact !== chatUser) {
                        $(`#contact-${contact} .notification-dot`).show();
                    }
                });
                setTimeout(checkNewMessages, 1000);
            },
            error: function() {
                setTimeout(checkNewMessages, 2000);
            }
        });
    }

    function loadNewMessages() {
        let $latestMessage = $('#chat-messages .message').last();
        let latestMessageTimestamp = $latestMessage.attr('data-timestamp');
        let latestMessageId = parseInt($latestMessage.attr('data-id'), 10);

        if (!latestMessageTimestamp) {
            latestMessageTimestamp = new Date().toISOString();
            latestMessageId = 0;
        }

        $.ajax({
            url: getNewMessagesUrl,
            type: 'GET',
            data: {
                'after_timestamp': latestMessageTimestamp,
                'after_id': latestMessageId
            },
            success: function(response) {
                if (response.new_messages) {
                    const wasAtBottom = isUserAtBottom();

                    response.new_messages.forEach(function(message) {
                        if ($('#chat-messages .message[data-id="' + message.id + '"]').length === 0) {
                            let senderClass = message.sender === username ? 'from-user' : 'from-contact';
                            let messageHtml = `<div class="message ${senderClass}" data-timestamp="${message.timestamp}" data-id="${message.id}">`;
                            if (message.image_url) {
                                messageHtml += `<img src="${message.image_url}" width="200">`;
                            }
                            if (message.content) {
                                messageHtml += `<p>${message.content}</p>`;
                            }
                            messageHtml += `</div>`;


                            $('#chat-messages').append(messageHtml);
                        }
                    });

                    if (response.new_messages.length > 0 && wasAtBottom) {
                        scrollToBottom();
                    }
                }
                setTimeout(loadNewMessages, 500);
            },
            error: function(xhr, status, error) {
                setTimeout(loadNewMessages, 1000);
            }
        });
    }

    function updateContacts() {
        $.ajax({
            url: updateContactsUrl,
            type: 'GET',
            success: function(response) {
                const contacts = response.contacts;
                const $contactsList = $('.contacts-list .contacts');
                $contactsList.empty();

                if (contacts.length === 0) {
                    $contactsList.append('<li>No contacts</li>');
                } else {
                    contacts.forEach(function(contact) {
                        let contactHtml = `
                            <li id="contact-${contact.username}">
                                <div class="info-contact">
                                    <img src="${contact.profile_image_url}" alt="Profile image">
                                    <a href="${homeUrl}?chat_with=${contact.username}">${contact.username}</a>
                                </div>
                                <span class="notification-dot" style="display: ${contact.is_read ? 'inline': 'none'};">●</span>
                            </li>
                        `;
                        $contactsList.append(contactHtml);
                    });
                }
            },
            error: function(xhr, status, error) {
                console.log("Error reloading contacts: ", error);
            }
        });
    }

    function loadOldPosts() {
        let $oldestPost = $('#chat-messages .post_group').first();
        let oldestPostTimestamp = $oldestPost.attr('data-timestamp');
        let oldestPostId = parseInt($oldestPost.attr('data-id'), 10);

        if (!oldestPostTimestamp) {
            return;
        }

        $.ajax({
            url: loadOldPostsUrl,
            type: 'GET',
            data: {
                'before_timestamp': oldestPostTimestamp,
                'before_id': oldestPostId,
                'limit': limit
            },
            success: function(response) {
                const posts = response.posts;
                if (posts.length > 0) {
                    let scrollHeightBefore = $('#chat-messages')[0].scrollHeight;
                    let scrollTopBefore = $('#chat-messages').scrollTop();

                    posts.forEach(function(post) {
                        if ($('#chat-messages .post_group[data-id="' + post.id + '"]').length === 0) {
                            let postHtml = `<div class="post_group" data-timestamp="${post.timestamp}" data-id="${post.id}">`;
                            if (post.image_url) {
                                postHtml += `<img src="${post.image_url}" width="200">`;
                            }
                            if (post.content) {
                                postHtml += `<p>${post.content}</p>`;
                            }
                            postHtml += `</div>`;


                            if (post.group_sender === username){
                                $('#chat-messages').prepend(`<a class="pop_post_link" href="/home/pop_message/${post.id}/?group_with=${post.sender}">Delete message</a>`);
                            }
                            $('#chat-messages').prepend(postHtml);
                        }
                    });

                    let scrollHeightAfter = $('#chat-messages')[0].scrollHeight;
                    $('#chat-messages').scrollTop(scrollTopBefore + (scrollHeightAfter - scrollHeightBefore));
                } else {
                    $('#chat-messages').off('scroll');
                }
            },
            error: function(xhr, status, error) {
                console.log("Error loading old posts: ", error);
            }
        });
    }

    function loadNewPosts() {
        let $latestPost = $('#chat-messages .post_group').last();
        let latestPostTimestamp = $latestPost.attr('data-timestamp');
        let latestPostId = parseInt($latestPost.attr('data-id'), 10);

        if (!latestPostTimestamp) {
            latestPostTimestamp = new Date().toISOString();
            latestPostId = 0;
        }

        $.ajax({
            url: getNewPostsUrl,
            type: 'GET',
            data: {
                'after_timestamp': latestPostTimestamp,
                'after_id': latestPostId
            },
            success: function(response) {
                if (response.new_posts) {
                    const wasAtBottom = isUserAtBottom();

                    response.new_posts.forEach(function(post) {
                        if ($('#chat-messages .post_group[data-id="' + post.id + '"]').length === 0) {
                            let postHtml = `<div class="post_group" data-timestamp="${post.timestamp}" data-id="${post.id}">`;
                            if (post.image_url) {
                                postHtml += `<img src="${post.image_url}" width="200">`;
                            }
                            if (post.content) {
                                postHtml += `<p>${post.content}</p>`;
                            }
                            postHtml += `</div>`;
                            $('#chat-messages').append(postHtml);
                        }
                    });

                    if (response.new_posts.length > 0 && wasAtBottom) {
                        scrollToBottom();
                    }
                }
                setTimeout(loadNewPosts, 500);
            },
            error: function(xhr, status, error) {
                setTimeout(loadNewPosts, 1000);
            }
        });
    }

    function checkNewPosts() {
        $.ajax({
            url: checkNewPostsUrl,
            type: 'GET',
            success: function(response) {
                $('.notification-dot-group').hide();
                response.groups_with_unread.forEach(function(group) {
                    if (group !== groupId) {
                        $(`#group-${group} .notification-dot-group`).show();
                    }
                });
                setTimeout(checkNewPosts, 1000);
            },
            error: function() {
                setTimeout(checkNewPosts, 2000);
            }
        });
    }

    function updateGroups() {
        $.ajax({
            url: updateGroupsUrl,
            type: 'GET',
            success: function(response) {
                const groups = response.groups;
                const $groupsList = $('.contacts-list .groups');
                $groupsList.empty();

                if (groups.length === 0) {
                    $groupsList.append('<li>No groups</li>');
                } else {
                    groups.forEach(function(group) {
                        let groupHtml = `
                            <li id="group-${group.name}">
                                <div class="info-group">
                                    <img src="${group.image_url}" alt="Profile image">
                                    <a href="${homeUrl}?group_with=${group.name}">${group.name}</a>
                                </div>
                                <span class="notification-dot-group" style="display: ${group.is_read ? 'inline' : 'none'};">●</span>
                            </li>
                        `;
                        $groupsList.append(groupHtml);
                    });
                }
            },
            error: function(xhr, status, error) {
                console.log("Error reloading groups: ", error);
            }
        });
    }

    $('#chat-messages').on('scroll', function() {
        if ($(this).scrollTop() === 0) {
            if (chatUser) {
                loadOldMessages();
            } else if (groupId) {
                loadOldPosts();
            }
        }
    });

    $('#publish-post-form').on('submit', function(event) {
        event.preventDefault();

        const postContent = $('#post-input').val().trim();
        const imageInput = $('#post-image-input')[0].files[0];

        if (!postContent && !imageInput) {
            alert("The post cannot be empty.");
            return;
        }

        if (postContent.length > 8000) {
            alert("The post is too long. Maximum length is 8000 characters.");
            return;
        }

        const now = Date.now();
        if (now - lastPostTime < 1000) {
            alert("You are sending messages too frequently. Please wait a bit.");
            return;
        }

        lastPostTime = now;

        const formData = new FormData(this);

        $.ajax({
            url: publishPostUrl,
            type: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            success: function(response) {
                if (response.status === 'success') {
                    const postContent = $('#post-input').val();
                    const imageInput = $('#post-image-input')[0].files[0];

                    let postHtml = `<div class="post_group" data-timestamp="${response.timestamp}" data-id="${response.id}">`;
                    if (imageInput) {
                        postHtml += `<img src="${URL.createObjectURL(imageInput)}" width="200">`;
                    }
                    if (postContent && postContent.replace(/<\/?(b|i|u)>/g, '').length) {
                        postHtml += `<p>${postContent}</p>`;
                    }
                    postHtml += `</div>`;

                    $('#chat-messages').append(postHtml);
                    $('#chat-messages').append(`<a class="pop_post_link" href="/home/pop_message/${response.id}/?group_with=${response.group_id}">Delete message</a>`);

                    $('#post-input').val('');
                    $('#post-input').css('height', 'auto');
                    $('#post-image-input').val('');

                    scrollToBottom();
                } else {
                    alert(response.post || "Error sending message.");
                }
            },
            error: function(xhr, status, error) {
                console.log("Error sending message: ", error);
            }
        });
    });

    if (chatUser) {
        checkNewMessages();
        loadNewMessages();
    }

    if (groupId) {
        checkNewPosts();
        loadNewPosts();
    }

    setInterval(updateContacts, 5000);
    setInterval(updateGroups, 5000);
});


document.addEventListener('DOMContentLoaded', function() {
    const emojiButton = document.getElementById('emoji-button');
    const emojiPicker = document.getElementById('emoji-picker');
    const messageInput = document.getElementById('message-input');

    const emojiButtonPost = document.getElementById('emoji-button-post');
    const emojiPickerPost = document.getElementById('emoji-picker-post');
    const postInput = document.getElementById('post-input');

    const styleButton = document.getElementById('style-button');
    const styleMenu = document.getElementById('style-menu');
    const textarea = document.getElementById('message-input');

    const styleButtonPost = document.getElementById('style-button-post');
    const styleMenuPost = document.getElementById('style-menu-post');
    const textareaPost = document.getElementById('post-input');


    if (emojiButton){
        emojiButton.addEventListener('click', function(event) {
            if (emojiPicker.style.display === 'none' || emojiPicker.style.display === '') {
                emojiPicker.style.display = 'table';

                const start = messageInput.selectionStart;
                const end = messageInput.selectionEnd;
                messageInput.setSelectionRange(start , end);
                messageInput.focus();

                updateEmojiPickerPosition()
            } else {
                emojiPicker.style.display = 'none';
            }
        });


        emojiPicker.addEventListener('click', function(event) {
            if (event.target.classList.contains('emoji')) {
                const start = messageInput.selectionStart;
                const end = messageInput.selectionEnd;


                messageInput.value = messageInput.value.substring(0, start) + event.target.textContent+ messageInput.value.substring(end);

                messageInput.setSelectionRange(start + event.target.textContent.length, start + event.target.textContent.length);
                messageInput.focus();

            }
        });

        document.addEventListener('click', function(event) {
            if (!emojiPicker.contains(event.target) && event.target !== emojiButton) {
                emojiPicker.style.display = 'none';
            }
        });


        window.addEventListener('resize', updateEmojiPickerPosition);

        function updateEmojiPickerPosition() {
            const rect = emojiButton.getBoundingClientRect();
            const pickerHeight = emojiPicker.offsetHeight;


            emojiPicker.style.top = `${rect.top + window.scrollY - pickerHeight}px`;
            emojiPicker.style.left = `${Math.max(rect.left + window.scrollX, 10)}px`;
            emojiPicker.style.right = `${Math.max(window.innerWidth - rect.right, 10)}px`;
        }
    }
    else if (emojiButtonPost){
        emojiButtonPost.addEventListener('click', function(event) {
            if (emojiPickerPost.style.display === 'none' || emojiPickerPost.style.display === '') {
                emojiPickerPost.style.display = 'table';

                const start = postInput.selectionStart;
                const end = postInput.selectionEnd;
                postInput.setSelectionRange(start, end);
                postInput.focus();

                updateEmojiPickerPostPosition()
            } else {
                emojiPickerPost.style.display = 'none';
            }
        });


        emojiPickerPost.addEventListener('click', function(event) {
            if (event.target.classList.contains('emoji')) {
                const start = postInput.selectionStart;
                const end = postInput.selectionEnd;


                postInput.value = postInput.value.substring(0, start) + event.target.textContent+ postInput.value.substring(end);

                postInput.setSelectionRange(start + event.target.textContent.length, start + event.target.textContent.length);
                postInput.focus();
            }
        });

        document.addEventListener('click', function(event) {
            if (!emojiPickerPost.contains(event.target) && event.target !== emojiButtonPost) {
                emojiPickerPost.style.display = 'none';
            }
        });


        window.addEventListener('resize', updateEmojiPickerPostPosition);

        function updateEmojiPickerPostPosition() {
            const rect = emojiButtonPost.getBoundingClientRect();
            const pickerHeight = emojiPickerPost.offsetHeight;


            emojiPickerPost.style.top = `${rect.top + window.scrollY - pickerHeight}px`;
            emojiPickerPost.style.left = `${Math.max(rect.left + window.scrollX, 10)}px`;
            emojiPickerPost.style.right = `${Math.max(window.innerWidth - rect.right, 10)}px`;
        }
    }


    if (styleButton){

        styleButton.addEventListener('click', function (e) {
            const start = textarea.selectionStart;
            const end = textarea.selectionEnd;
            textarea.setSelectionRange(start, end);
            textarea.focus();

            if (styleMenu.style.display === 'none') {

                const rect = styleButton.getBoundingClientRect();
                styleMenu.style.display = 'block';
                styleMenu.style.top = `${rect.top + window.scrollY - styleMenu.offsetHeight}px`;
                styleMenu.style.left = `${rect.left + window.scrollX}px`;
            } else {
                styleMenu.style.display = 'none';
            }
        });

        styleMenu.addEventListener('click', function (e) {
            if (!e.target.classList.contains('style-option')) return;

            const start = textarea.selectionStart;
            const end = textarea.selectionEnd;
            const style = e.target.getAttribute('data-style');
            const text = textarea.value;
            const selectedText = text.substring(start, end);

            let styledText;
            switch (style) {
                case 'bold':
                    styledText = `<b>${selectedText}</b>`;
                    break;
                case 'italic':
                    styledText = `<i>${selectedText}</i>`;
                    break;
                case 'underline':
                    styledText = `<u>${selectedText}</u>`;
                    break;
                case 'normal':
                    styledText = selectedText.replace(/<\/?(b|i|u)>/g, '');
                    break;
                default:
                    return;
            }

            textarea.value = text.substring(0, start) + styledText + text.substring(end);

            textarea.setSelectionRange(start, start + styledText.length);
            textarea.focus();

            styleMenu.style.display = 'none';
        });

        document.addEventListener('click', function (e) {
            if (!styleMenu.contains(e.target) && e.target !== styleButton) {
                styleMenu.style.display = 'none';
            }
        });

        window.addEventListener('resize', function () {
            if (styleMenu.style.display === 'block') {
                const rect = styleButton.getBoundingClientRect();
                styleMenu.style.top = `${rect.top + window.scrollY - styleMenu.offsetHeight}px`;
                styleMenu.style.left = `${rect.left + window.scrollX}px`;
            }
        });
    }

    else  if (styleButtonPost){
        styleButtonPost.addEventListener('click', function (e) {
            const start = textareaPost.selectionStart;
            const end = textareaPost.selectionEnd;
            textareaPost.setSelectionRange(start, end);
            textareaPost.focus();

            if (styleMenuPost.style.display === 'none') {

                const rect = styleButtonPost.getBoundingClientRect();
                styleMenuPost.style.display = 'block';
                styleMenuPost.style.top = `${rect.top + window.scrollY - styleMenuPost.offsetHeight}px`;
                styleMenuPost.style.left = `${rect.left + window.scrollX}px`;
            } else {
                styleMenuPost.style.display = 'none';
            }
        });

        styleMenuPost.addEventListener('click', function (e) {
            if (!e.target.classList.contains('style-option')) return;

            const start = textareaPost.selectionStart;
            const end = textareaPost.selectionEnd;
            const style = e.target.getAttribute('data-style');
            const text = textareaPost.value;
            const selectedText = text.substring(start, end);

            let styledText;
            switch (style) {
                case 'bold':
                    styledText = `<b>${selectedText}</b>`;
                    break;
                case 'italic':
                    styledText = `<i>${selectedText}</i>`;
                    break;
                case 'underline':
                    styledText = `<u>${selectedText}</u>`;
                    break;
                case 'normal':
                    styledText = selectedText.replace(/<\/?(b|i|u)>/g, '');
                    break;
                default:
                    return;
            }

            textareaPost.value = text.substring(0, start) + styledText + text.substring(end);

            textareaPost.setSelectionRange(start, start + styledText.length);
            textareaPost.focus();

            styleMenuPost.style.display = 'none';
        });

        document.addEventListener('click', function (e) {
            if (!styleMenuPost.contains(e.target) && e.target !== styleButtonPost) {
                styleMenuPost.style.display = 'none';
            }
        });

        window.addEventListener('resize', function () {
            if (styleMenuPost.style.display === 'block') {
                const rect = styleButtonPost.getBoundingClientRect();
                styleMenuPost.style.top = `${rect.top + window.scrollY - styleMenuPost.offsetHeight}px`;
                styleMenuPost.style.left = `${rect.left + window.scrollX}px`;
            }
        });
    }
});