from fastapi import APIRouter, Query
from fastapi.responses import HTMLResponse

http = APIRouter()


def render_html(hackathon_id: int, group_id: int, room_id: int, token: str) -> str:
    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Hackathon Group Chat</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        #chat-container {{
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
            overflow: hidden;
        }}
        #messages {{
            height: 400px;
            overflow-y: auto;
            padding: 20px;
            list-style-type: none;
            margin: 0;
        }}
        #messages li {{
            padding: 10px 15px;
            margin-bottom: 8px;
            border-radius: 18px;
            background-color: #e3f2fd;
            max-width: 70%;
            word-wrap: break-word;
        }}
        #messages li.my-message {{
            margin-left: auto;
            background-color: #bbdefb;
            text-align: right;
        }}
        #message-form {{
            display: flex;
            padding: 15px;
            background-color: #f0f0f0;
            border-top: 1px solid #ddd;
        }}
        #message-input {{
            flex-grow: 1;
            padding: 10px 15px;
            border: 1px solid #ddd;
            border-radius: 20px;
            outline: none;
            font-size: 16px;
        }}
        #message-form button {{
            margin-left: 10px;
            padding: 10px 20px;
            background-color: #2196f3;
            color: white;
            border: none;
            border-radius: 20px;
            cursor: pointer;
            font-size: 16px;
        }}
        #status {{
            padding: 10px 15px;
            background-color: #e8f5e9;
            color: #2e7d32;
            text-align: center;
            font-size: 14px;
        }}
        #status.error {{
            background-color: #ffebee;
            color: #c62828;
        }}
        .typing-indicator {{
            font-style: italic;
            color: #666;
            padding: 5px 15px;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <div id="chat-container">
        <h1>Hackathon Group Chat</h1>
        <div id="status">Connecting to chat...</div>
        <div id="typing-indicator" class="typing-indicator" style="display: none;"></div>
        <ul id="messages"></ul>
        <form id="message-form">
            <input type="text" id="message-input" placeholder="Type your message..." autocomplete="off" />
            <button type="submit">Send</button>
        </form>
    </div>

    <script>
        document.addEventListener('DOMContentLoaded', () => {{
            const hackathonId = {hackathon_id};
            const groupId = {group_id};
            const roomId = {room_id};
            const token = "{token}";

            const ws = new WebSocket(
                `ws://localhost:5000/ws/${{hackathonId}}/${{groupId}}/${{roomId}}?token=${{token}}`
            );

            const messagesList = document.getElementById('messages');
            const messageForm = document.getElementById('message-form');
            const messageInput = document.getElementById('message-input');
            const statusDiv = document.getElementById('status');
            const typingIndicator = document.getElementById('typing-indicator');

            let typingTimeout;
            const TYPING_TIMEOUT = 2000;

            ws.onopen = () => {{
                statusDiv.textContent = "Connected to chat room";
                statusDiv.style.backgroundColor = "#e8f5e9";
                statusDiv.style.color = "#2e7d32";
                addMessageToChat("System", "You have joined the chat", true);
            }};

            ws.onclose = (event) => {{
                if (event.wasClean) {{
                    statusDiv.textContent = `Connection closed: ${{event.reason || 'No reason provided'}}`;
                }} else {{
                    statusDiv.textContent = "Connection lost. Trying to reconnect...";
                    statusDiv.className = "error";
                    setTimeout(() => window.location.reload(), 5000);
                }}
            }};

            ws.onerror = (error) => {{
                console.error("WebSocket error:", error);
                statusDiv.textContent = "WebSocket error occurred";
                statusDiv.className = "error";
            }};

            ws.onmessage = (event) => {{
                const data = JSON.parse(event.data);

                if (data.type === 'message') {{
                    addMessageToChat(data.username, data.text, data.isMyMessage);
                }} else if (data.type === 'typing') {{
                    showTypingIndicator(data.username);
                }} else if (data.type === 'user_joined') {{
                    addSystemMessage(`${{data.username}} joined the chat`);
                }} else if (data.type === 'user_left') {{
                    addSystemMessage(`${{data.username}} left the chat`);
                }}
            }};

            messageForm.addEventListener('submit', (e) => {{
                e.preventDefault();

                const message = messageInput.value.trim();
                if (message && ws.readyState === WebSocket.OPEN) {{
                    ws.send(JSON.stringify({{ type: 'message', text: message }}));
                    messageInput.value = '';
                }}
            }});

            messageInput.addEventListener('input', () => {{
                if (ws.readyState === WebSocket.OPEN) {{
                    ws.send(JSON.stringify({{ type: 'typing' }}));

                    clearTimeout(typingTimeout);
                    typingTimeout = setTimeout(() => {{
                        ws.send(JSON.stringify({{ type: 'typing_end' }}));
                    }}, TYPING_TIMEOUT);
                }}
            }});

            function addMessageToChat(username, text, isMyMessage = false) {{
                const li = document.createElement('li');
                li.innerHTML = `<strong>${{username}}:</strong> ${{text}}`;
                if (isMyMessage) {{
                    li.classList.add('my-message');
                }}
                messagesList.appendChild(li);
                messagesList.scrollTop = messagesList.scrollHeight;
            }}

            function addSystemMessage(text) {{
                const li = document.createElement('li');
                li.textContent = text;
                li.style.textAlign = 'center';
                li.style.color = '#666';
                li.style.fontStyle = 'italic';
                li.style.backgroundColor = 'transparent';
                messagesList.appendChild(li);
                messagesList.scrollTop = messagesList.scrollHeight;
            }}

            function showTypingIndicator(username) {{
                typingIndicator.textContent = `${{username}} is typing...`;
                typingIndicator.style.display = 'block';

                clearTimeout(typingTimeout);
                typingTimeout = setTimeout(() => {{
                    typingIndicator.style.display = 'none';
                }}, TYPING_TIMEOUT);
            }}

            window.addEventListener('beforeunload', () => {{
                if (ws.readyState === WebSocket.OPEN) {{
                    ws.close(1000, "User left the chat");
                }}
            }});
        }});
    </script>
</body>
</html>
"""


@http.get("/{hackathon_id}/{group_id}/{room_id}")
async def get_chat_page(
    hackathon_id: int,
    group_id: int,
    room_id: int,
    token: str = Query(..., description="Authentication token"),
):
    html = render_html(hackathon_id, group_id, room_id, token)
    return HTMLResponse(html)
