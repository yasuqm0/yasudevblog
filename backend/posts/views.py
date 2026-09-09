from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Post, Comment, PostReaction, CommentReaction
from .serializers import PostListSerializer, PostDetailSerializer, CommentSerializer


class PostListView(generics.ListAPIView):
    queryset = Post.objects.all().order_by('-fecha_publicacion')
    serializer_class = PostListSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['tags__slug']


class PostDetailView(generics.RetrieveAPIView):
    queryset = Post.objects.all()
    serializer_class = PostDetailSerializer
    lookup_field = 'slug'

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.vistas += 1
        instance.save(update_fields=['vistas'])
        return super().retrieve(request, *args, **kwargs)


class CommentCreateView(generics.CreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(autor=self.request.user, post_id=self.kwargs['post_id'])

class PostReactionView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, post_id):
        tipo = request.data.get('tipo')
        if tipo not in ('like', 'dislike'):
            return Response({'error': 'tipo debe ser like o dislike'}, status=400)

        reaction, created = PostReaction.objects.update_or_create(
            post_id=post_id, usuario=request.user,
            defaults={'tipo': tipo},
        )
        return Response({'tipo': reaction.tipo, 'created': created})

    def delete(self, request, post_id):
        PostReaction.objects.filter(post_id=post_id, usuario=request.user).delete()
        return Response(status=204)


class CommentReactionView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, comment_id):
        tipo = request.data.get('tipo')
        if tipo not in ('like', 'dislike'):
            return Response({'error': 'tipo debe ser like o dislike'}, status=400)

        reaction, created = CommentReaction.objects.update_or_create(
            comment_id=comment_id, usuario=request.user,
            defaults={'tipo': tipo},
        )
        return Response({'tipo': reaction.tipo, 'created': created})

    def delete(self, request, comment_id):
        CommentReaction.objects.filter(comment_id=comment_id, usuario=request.user).delete()
        return Response(status=204)