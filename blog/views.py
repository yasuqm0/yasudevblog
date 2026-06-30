from django.shortcuts import render, get_object_or_404, redirect
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Post, Comment, CommentVote, EmojiPack
from django.contrib.auth.decorators import login_required
from .serializers import PostListSerializer, PostDetailSerializer
from django.http import JsonResponse

def post_list(request):
    posts = Post.objects.filter(published=True).order_by('-created_at')
    return render(request, 'blog/post_list.html', {'posts': posts})


def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug, published=True)
    comments = post.comments.all().order_by('-votes__vote', 'created_at')

    if request.method == 'POST' and request.user.is_authenticated:
        content = request.POST.get('content', '').strip()
        if content:
            Comment.objects.create(
                post=post,
                author=request.user,
                content=content
            )
        return redirect('post_detail', slug=slug)

    comments_data = []
    for comment in comments.distinct():
        likes = comment.votes.filter(vote=1).count()
        dislikes = comment.votes.filter(vote=-1).count()
        user_vote = None
        if request.user.is_authenticated:
            vote = comment.votes.filter(user=request.user).first()
            user_vote = vote.vote if vote else None
        comment.likes = likes
        comment.dislikes = dislikes
        comment.user_vote = user_vote
        comments_data.append(comment)

    emoji_packs = EmojiPack.objects.prefetch_related('emojis').all()

    return render(request, 'blog/post_detail.html', {
        'post': post,
        'comments': comments_data,
        'emoji_packs': emoji_packs,
    })

from django.http import JsonResponse

@login_required
def vote_comment(request, slug, comment_id, vote_type):
    comment = get_object_or_404(Comment, id=comment_id)
    vote_value = 1 if vote_type == 'like' else -1

    existing = CommentVote.objects.filter(comment=comment, user=request.user).first()

    if existing:
        if existing.vote == vote_value:
            existing.delete()
        else:
            existing.vote = vote_value
            existing.save()
    else:
        CommentVote.objects.create(comment=comment, user=request.user, vote=vote_value)

    likes = comment.votes.filter(vote=1).count()
    dislikes = comment.votes.filter(vote=-1).count()
    user_vote = None
    vote_obj = comment.votes.filter(user=request.user).first()
    if vote_obj:
        user_vote = vote_obj.vote

    return JsonResponse({'likes': likes, 'dislikes': dislikes, 'user_vote': user_vote})

@login_required
def delete_comment(request, slug, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, author=request.user)
    comment.delete()
    return redirect('post_detail', slug=slug)

@api_view(['GET'])
def api_post_list(request):
    posts = Post.objects.filter(published=True).order_by('-created_at')
    serializer = PostListSerializer(posts, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def api_post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug, published=True)
    serializer = PostDetailSerializer(post)
    return Response(serializer.data)