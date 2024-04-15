import json
from bson import ObjectId
from datetime import datetime

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        elif isinstance(obj, datetime):
            return obj.isoformat()  # Serialize datetime objects to ISO format
        else:
            return super().default(obj)