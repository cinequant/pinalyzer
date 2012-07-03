from map.models import UserStatModel
from simplejson import  dumps
from django_json import MyEncoder

dumps(UserStatModel.objects.all(), cls=MyEncoder)
