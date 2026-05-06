from django.http import HttpRequest, HttpResponse


def hello(request: HttpRequest, name: str) -> HttpResponse:
    return HttpResponse(f"<h1>Hello, {name}!</h1>")
