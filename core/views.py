from django.http import HttpResponse

def test_view(request):
    return HttpResponse("Hello, media should be served now!")
