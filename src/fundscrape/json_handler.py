import os
import json
from datetime import date,datetime


# why doesn't python have a json dunder method? wtf
class JsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, "__json__"):
            return obj.__json__()
        
        # dates aren't serialisable by default
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()

        return super().default(obj)