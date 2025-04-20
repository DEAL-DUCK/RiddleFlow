import datetime
from core.models import Hackathon

now = datetime.datetime.now()
start_time = datetime.datetime.fromisoformat("2025-04-20T14:55:50.785000")
end_time = datetime.datetime.fromisoformat("2025-04-20T14:59:50.785000")
print(
    start_time + datetime.timedelta(hours=3)
    <= now
    <= end_time + datetime.timedelta(hours=3)
)
print(
    now.isoformat(),
    "\n",
    start_time + datetime.timedelta(hours=3),
    "\n",
    end_time + datetime.timedelta(hours=3),
)
