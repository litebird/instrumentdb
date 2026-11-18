from django.shortcuts import get_object_or_404, render
from .models import Post
from django.contrib.auth.decorators import login_required


@login_required
def post_list(request):
    posts = Post.objects.filter(is_published=True)
    return render(request, "blog/post_list.html", {"posts": posts})


@login_required
def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug, is_published=True)
    return render(request, "blog/post_detail.html", {"post": post})
