from django.shortcuts import render

# using a simple function based view to render the login template
def login_view(request):
    return render(request, 'login.html')

def home_view(request):
    return render(request, 'home.html')