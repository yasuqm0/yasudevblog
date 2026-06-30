from django.shortcuts import render, get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Page
from .serializers import PageSerializer
from blog.models import Post
from blog.serializers import PostListSerializer
from games.models import Game
from games.serializers import GameSerializer

# Create your views here.
def index(request):
    recent_posts = Post.objects.filter(published=True).order_by('-created_at')[:3]
    featured_games = Game.objects.filter(active=True)[:4]
    return render(request, 'pages/index.html', {
        'recent_posts': recent_posts,
        'featured_games': featured_games,
    })

def about(request):
    page = Page.objects.filter(slug='sobre-mi').first()
    return render(request, 'pages/about.html', {'page': page})

@api_view(['GET'])
def api_index(request):
    recent_posts = Post.objects.filter(published=True).order_by('-created_at')[:3]
    featured_games = Game.objects.filter(active=True)[:4]
    return Response({
        'recent_posts': PostListSerializer(recent_posts, many=True).data,
        'featured_games': GameSerializer(featured_games, many=True).data,
    })


@api_view(['GET'])
def api_page_detail(request, slug):
    page = get_object_or_404(Page, slug=slug)
    serializer = PageSerializer(page)
    return Response(serializer.data)