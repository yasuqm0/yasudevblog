from django.urls import path
from .views import PostListView, PostDetailView, CommentCreateView, PostReactionView, CommentReactionView

urlpatterns = [
    path('', PostListView.as_view(), name='post-list'),
    path('<slug:slug>/', PostDetailView.as_view(), name='post-detail'),
    path('<int:post_id>/comentarios/', CommentCreateView.as_view(), name='comment-create'),
    path('<int:post_id>/reaccion/', PostReactionView.as_view(), name='post-reaction'),
    path('comentarios/<int:comment_id>/reaccion/', CommentReactionView.as_view(), name='comment-reaction'),
]