from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Create your views here.
@login_required(login_url='Authentification:login')
def darshbord(request):
    user = request.user

    datas = {
        'active_page': 'accueil'
    }

    return render(request, 'shoping-cart.html', datas)