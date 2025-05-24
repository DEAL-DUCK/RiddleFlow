from core.models import User


def can_access_chat(user: User, hackathon_id: int, group_id: int) -> bool:
    if not any(assoc.hackathon_id == hackathon_id for assoc in user.hackathons_details):
        return False
    return any(assoc.group_id == group_id for assoc in user.groups_details)


def creating_chat(
    hackathon_id: int, group_id: int, room_id: int, active_connections: dict
):
    if hackathon_id not in active_connections:
        active_connections[hackathon_id] = {}
    if group_id not in active_connections[hackathon_id]:
        active_connections[hackathon_id][group_id] = {}
    if room_id not in active_connections[hackathon_id][group_id]:
        active_connections[hackathon_id][group_id][room_id] = set()
    return active_connections


def clear_room(
    hackathon_id: int, group_id: int, room_id: int, active_connections: dict
):
    if not active_connections[hackathon_id][group_id][room_id]:
        del active_connections[hackathon_id][group_id][room_id]
        if not active_connections[hackathon_id][group_id]:
            del active_connections[hackathon_id][group_id]
        if not active_connections[hackathon_id]:
            del active_connections[hackathon_id]
