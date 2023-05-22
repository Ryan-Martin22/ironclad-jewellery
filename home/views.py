from django.shortcuts import render


def index(request):
    """ A view to return the index page """

    return render(request, 'home/index.html')


def aboutus(request):
    """
    A view to return about us page
    """
    return render(request, 'about/aboutus.html')