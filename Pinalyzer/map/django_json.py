from django.db.models.query import QuerySet
from django.utils.simplejson import  JSONEncoder
from django.db.models import Model
import datetime
from map.user import User
#from django.core.serializers import serialize

class MyEncoder(JSONEncoder):
    def default(self, obj):
        """
        Transform obj into a serializable object 
        """
        if isinstance(obj, QuerySet):
            return list(obj)
        elif isinstance(obj,User):
            return obj.__dict__
        elif isinstance(obj, datetime.datetime):
            return {'year':obj.year,'month':obj.month,'day': obj.day}
        elif isinstance(obj, Model):
            d=obj.__dict__
            del d['_state']
            return d
        return JSONEncoder.default(self,obj)
    



