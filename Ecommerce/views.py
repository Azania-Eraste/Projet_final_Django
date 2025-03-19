from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Create your views here.
@login_required(login_url='Authentification:login')
def darshbord(request):
    user = request.user

    datas = {
        'active_page': 'shop'
    }

    return render(request, 'shoping-cart.html', datas)

@login_required(login_url='Authentification:login')
def favorite(request):

    datas = {
        'active_page': 'shop'
    }

    return render(request, 'Favorite.html', datas)

def shop(request):

    datas = {
        'active_page': 'shop'
    }

    return render(request, 'shop-grid.html', datas)

def shop_detail(request):

    datas = {
        'active_page': 'shop'
    }

    return render(request, 'shop-details.html', datas)