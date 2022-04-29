from django.shortcuts import render
from .models import Champion

def index(request):
    """Muestra la lista de campeones disponibles."""
    champions = Champion.objects.order_by('name')
    context = {
                'champions': champions,
            }
    return render(request, 'champions/index.html', context)

def detail(request, champion_identifier):
    """Muestra la pagina de detalles de un campeon."""
    champion = Champion.objects.get(identifier=champion_identifier)
    data = champion.get_data()
    context = {
                'champion': champion,
                'data': data,
            }
    return render(request, 'champions/detail.html', context)
