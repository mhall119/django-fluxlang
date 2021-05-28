from django.shortcuts import render

from django_fluxlang import Flux

from .models import HostInfo

# Create your views here.
def host_stats(request):
    cpu = Flux.bucket('website').range(start='-5m', stop='-0s')
    cpu = cpu.filter(_measurement='cpu', _field='usage_user')

    if 'host' in request.GET:
        cpu = cpu.filter(host=request.GET.get('host'))

    hosts = HostInfo.objects.all()
    joined = Flux.join([hosts, cpu], on=['host'])
    context = {
        'query': cpu.fieldsAsCols(),
    }
    return render(request, 'flux_rawdata.html', context)

def monitoring(request):
    mon = Flux.bucket('_monitoring').range(start='-5m', stop='-0s')

    context = {
        'query': mon.fieldsAsCols(),
    }
    return render(request, 'flux_rawdata.html', context)

def host_lookup(request):
    cpu = Flux.bucket('website').range(start='-5m', stop='-0s')
    cpu = cpu.filter(_measurement='cpu', _field='usage_user')

    if 'host' in request.GET:
        cpu = cpu.filter(host=request.GET.get('host'))

    hosts = HostInfo.objects.all()
    joined = Flux.join([hosts, cpu], on=['host'])
    context = {
        'query': joined.fieldsAsCols(),
    }
    return render(request, 'flux_queryinfo.html', context)

    