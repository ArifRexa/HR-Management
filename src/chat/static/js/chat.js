window.addEventListener('DOMContentLoaded', () => {
    // Check if the browser supports notifications
    if ("Notification" in window && Notification.permission !== "granted") {
        Notification.requestPermission().then(permission => {
            if (permission === "granted") {
                console.log("Notification permission granted.");
            }
        });
    }

    const WebSocketProtocal = window.location.protocol === 'https:' ? 'wss://' : 'ws://';
    const WebSocketBaseUrl = WebSocketProtocal + window.location.host;

    function showNotification(title, message, chatUrl) {
        if (Notification.permission === "granted") {
            const options = {
                body: message,
                // icon: "/path/to/icon.png",  // Optionally add an icon
                // badge: "/path/to/badge.png", // Optionally add a badge icon
                tag: chatUrl,  // A tag allows you to group notifications
            };

            const notification = new Notification(title, options);

            // Handle notification click
            notification.onclick = function() {
                window.focus();
                window.open(chatUrl);
            };
        }
    }

    const getNewChatSocket = new WebSocket(`${WebSocketBaseUrl}/ws/new-chat/`);

    getNewChatSocket.onopen = function(e) {
        console.log("new connected....", e)
    }

    getNewChatSocket.onmessage = function(e) {
        console.log("on message")
        const data = JSON.parse(e.data);
        const chatListTable = document.getElementById("result_list");
        const chatList = chatListTable.getElementsByTagName("tbody")[0];
        const chatId = data.chat_id
        const new_message_count = document.getElementById("new-message-count");
        
        
        
        const action = data.type
        if(action == "new_chat"){
            const newChatElement = `<tr>
                                <td class="action-checkbox">
                                    <input type="checkbox" name="_selected_action" value="${chatId}" class="action-select">
                                </td>
                                <td class="field-get_client">
                                    <a href="/admin/chat/chat/${chatId}/change/">
                                    ${data.client}
                                    <br>
                                    ${data.message}
                                    <br>
                                    ${timeSince(data.timestamp)}
                                    </a>
                                </td>
                                <td class="field-status">${data.status}</td>
                            </tr>
                            `
            
            chatList.insertAdjacentHTML('afterbegin', newChatElement);
            new_message_count.textContent = parseInt(new_message_count.textContent) + 1
            showNotification(`New Chat Started From ${data.client}`, data.message, `/admin/chat/chat/${chatId}/change`);
        }else if(action == "new_message"){
            const chatId = data.chat_id;
            const chatElement = chatList.querySelector(`a[href="/admin/chat/chat/${chatId}/change/"]`).parentElement.parentElement;
            console.log(chatElement, chatList)
            chatElement.querySelector("p:nth-of-type(1)").textContent = data.message;
            chatElement.querySelector("p:nth-of-type(2)").textContent = timeSince(data.timestamp);

            // Move the chat to the top of the list
            // document.querySelector(`a[href="/chat/${chatId}/"]`).classList.add("unread");
            chatElement.classList.add("unread");
            chatList.prepend(chatElement);
            new_message_count.textContent = parseInt(new_message_count.textContent) + 1
            showNotification("New Message", data.message, `/admin/chat/chat/${chatId}/change`);
        }
    }

    getNewChatSocket.onclose = function(e) {
        console.log('Chat socket closed unexpectedly', e);
    }

    getNewChatSocket.onerror = function(e) {
        console.error('WebSocket error:', e);
    }
    // convert date to human readable
    function timeSince(dateString) {
        const date = new Date(dateString);
        const now = new Date();
        const seconds = Math.floor((now - date) / 1000);

        let interval = Math.floor(seconds / 31536000); // 1 year
        if (interval >= 1) return interval === 1 ? "1 year" : `${interval} years`;

        interval = Math.floor(seconds / 2592000); // 1 month
        if (interval >= 1) return interval === 1 ? "1 month" : `${interval} months`;

        interval = Math.floor(seconds / 86400); // 1 day
        if (interval >= 1) return interval === 1 ? "1 day" : `${interval} days`;

        interval = Math.floor(seconds / 3600); // 1 hour
        if (interval >= 1) return interval === 1 ? "1 hour" : `${interval} hours`;

        interval = Math.floor(seconds / 60); // 1 minute
        if (interval >= 1) return interval === 1 ? "1 minute" : `${interval} minutes`;

        return 'Now';
    }



})