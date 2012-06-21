from django.db.models.query import QuerySet
from django.core.serializers import serialize
from django.utils.simplejson import loads, JSONEncoder
from django.db.models import Model
from map.views import PinModel

from user import User


class DjangoJSONEncoder(JSONEncoder):
   
    def default(self, obj):
        """
        Transform obj into a serializable object ( for exemple, a dict)
        """
        if isinstance(obj, QuerySet):
            return list(obj)
        elif isinstance(obj,User):
            return obj.__dict__
        elif isinstance(obj, Model):
            d=obj.__dict__
            del d['_state']
            return d
        return JSONEncoder.default(self,obj)
    



