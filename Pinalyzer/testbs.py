from map.models import PinModel

def vider():
    l=PinModel.objects.all()
    for x in l:
        x.score=0
        x.match=0
        x.save()
        
