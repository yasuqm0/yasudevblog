from django.shortcuts import render, get_object_or_404
from django.http import Http404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime
from .models import Entry
from .serializers import EntrySerializer, EntryDetailSerializer


def entry_list(request):
    entries = Entry.objects.filter(active=True)
    return render(request, 'entries/entry_list.html', {'entries': entries})


def entry_detail(request, slug):
    entry = get_object_or_404(Entry, slug=slug, active=True)
    if not entry.is_accessible():
        raise Http404
    templates = {
        'full': 'entries/full.html',
        'minimal': 'entries/minimal.html',
        'blank': 'entries/blank.html',
        'custom': f'entries/{entry.custom_template}',
    }
    template = templates.get(entry.template_type, 'entries/full.html')
    return render(request, template, {'entry': entry})

@api_view(['GET'])
def api_entry_list(request):
    entries = Entry.objects.filter(active=True)
    serializer = EntrySerializer(entries, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def api_entry_detail(request, slug):
    entry = get_object_or_404(Entry, slug=slug, active=True)
    if not entry.is_accessible():
        return Response(
            {'detail': 'No encontrado.'},
            status=status.HTTP_404_NOT_FOUND
        )
    serializer = EntryDetailSerializer(entry)
    return Response(serializer.data)