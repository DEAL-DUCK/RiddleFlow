import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from api_v1.chat_groups.dependencies import can_access_chat, creating_chat, clear_room
from api_v1.dependencies.authentication.access_tokens import get_access_tokens_db
from api_v1.users.crud import get_user
from core.models import db_helper

ws = APIRouter()

# rooms:
# {
#   "hackathon_id": {
#       "group_id": {
#           "connections": set(),  # активные WebSocket-подключения
#       }
#   }
# }
rooms: dict[int, dict[int, dict[int, set[WebSocket]]]] = {}


@ws.websocket("/{hackathon_id}/{group_id}/{room_id}")
async def websocket_group_chat(
    websocket: WebSocket,
    hackathon_id: int,
    group_id: int,
    room_id: int,
    token: str = Query(...),
    access_token_db=Depends(get_access_tokens_db),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    access_token = await access_token_db.get_by_token(token)

    if not access_token:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    else:
        user = await get_user(session=session, user_id=access_token.user_id)

    if not can_access_chat(user, hackathon_id, group_id):
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await websocket.accept()

    active_connections = creating_chat(
        hackathon_id=hackathon_id,
        group_id=group_id,
        room_id=room_id,
        active_connections=rooms,
    )

    active_connections[hackathon_id][group_id][room_id].add(websocket)

    # Сообщаем всем остальным пользователям, что новый пользователь присоединился
    for connection in active_connections[hackathon_id][group_id][room_id]:
        if connection != websocket:
            await connection.send_json(
                {
                    "type": "user_joined",
                    "username": user.username,
                }
            )

    try:
        while True:
            data = await websocket.receive_json()

            if data.get("type") == "message":
                message = data.get("text")
                if message:
                    for connection in active_connections[hackathon_id][group_id][
                        room_id
                    ]:
                        await connection.send_json(
                            {
                                "type": "message",
                                "username": user.username,
                                "text": message,
                                "isMyMessage": connection == websocket,
                            }
                        )

            elif data.get("type") == "typing":
                for connection in active_connections[hackathon_id][group_id][room_id]:
                    if connection != websocket:
                        await connection.send_json(
                            {"type": "typing", "username": user.username}
                        )

            elif data.get("type") == "typing_end":
                for connection in active_connections[hackathon_id][group_id][room_id]:
                    if connection != websocket:
                        await connection.send_json(
                            {"type": "typing_end", "username": user.username}
                        )

    except WebSocketDisconnect:
        active_connections[hackathon_id][group_id][room_id].remove(websocket)

        # Когда пользователь отключается, сообщаем остальным
        for connection in active_connections[hackathon_id][group_id][room_id]:
            await connection.send_json({"type": "user_left", "username": user.username})

        # Очистка пустых комнат
        clear_room(
            hackathon_id=hackathon_id,
            group_id=group_id,
            room_id=room_id,
            active_connections=rooms,
        )
