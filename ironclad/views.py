from django.shortcuts import render


def handler404(request, exception):
    """ Error Handler 404 - Page Not Found """
    return render(request, "errors/404.html", status=404)


def handler503(request, exception):
    """ Error Handler 404 - Page Not Found """
    return render(request, "errors/404.html", status=503)


def handler500(request):
    """ 500 Internal Server Error """
    return render(request, "errors/500.html", status=500)