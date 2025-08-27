from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Log
from .serializers import LogSerializer

class LogViewSet(viewsets.ModelViewSet):
    queryset = Log.objects.all().order_by("-timestamp")
    serializer_class = LogSerializer

@api_view(["GET"])
def stats(request):
    return Response({
        "login_fail": Log.objects.filter(event_type="LOGIN_FAIL").count(),
        "brute_force": Log.objects.filter(event_type="BRUTE_FORCE").count(),
        "port_scan": Log.objects.filter(event_type="PORT_SCAN").count(),
        "malware": Log.objects.filter(event_type="MALWARE").count(),
    })
