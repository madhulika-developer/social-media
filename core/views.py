from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from django.views.decorators.http import require_POST
from .models import Post, Comment, Profile
from .forms import (
    RegisterForm, LoginForm, ProfileUpdateForm,
    UserUpdateForm, PostForm, CommentForm
)


# ─── Auth Views ────────────────────────────────────────────────────────────────

def register_view(request):
    """Register a new user account."""
    if request.user.is_authenticated:
        return redirect('feed')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome to SocialApp, {user.username}! 🎉')
            return redirect('feed')
    else:
        form = RegisterForm()
    return render(request, 'auth/register.html', {'form': form})


def login_view(request):
    """Log in an existing user."""
    if request.user.is_authenticated:
        return redirect('feed')
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}! 👋')
            return redirect(request.GET.get('next', 'feed'))
    else:
        form = LoginForm()
    return render(request, 'auth/login.html', {'form': form})


def logout_view(request):
    """Log out the current user."""
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('login')


# ─── Feed ───────────────────────────────────────────────────────────────────────

@login_required
def feed_view(request):
    """Show posts from users the current user follows + own posts."""
    user = request.user
    # Get IDs of users the current user follows
    following_ids = Profile.objects.filter(
        followers=user
    ).values_list('user_id', flat=True)

    posts = Post.objects.filter(
        Q(author__in=following_ids) | Q(author=user)
    ).select_related('author', 'author__profile').prefetch_related('likes', 'comments')

    post_form = PostForm()

    if request.method == 'POST':
        post_form = PostForm(request.POST, request.FILES)
        if post_form.is_valid():
            post = post_form.save(commit=False)
            post.author = user
            post.save()
            messages.success(request, 'Post created!')
            return redirect('feed')

    # Attach comment forms and like status to each post
    posts_data = []
    for post in posts:
        posts_data.append({
            'post': post,
            'comment_form': CommentForm(),
            'is_liked': post.is_liked_by(user),
            'top_comments': post.comments.filter(parent=None)[:3],
        })

    # Suggest users to follow (not already following, not self)
    suggestions = User.objects.exclude(
        pk__in=list(following_ids) + [user.pk]
    ).select_related('profile').order_by('?')[:5]

    return render(request, 'feed.html', {
        'posts_data': posts_data,
        'post_form': post_form,
        'suggestions': suggestions,
    })


# ─── Post Views ─────────────────────────────────────────────────────────────────

@login_required
def post_detail_view(request, pk):
    """Show a single post with all comments."""
    post = get_object_or_404(Post, pk=pk)
    comments = post.comments.filter(parent=None).select_related('author', 'author__profile')
    comment_form = CommentForm()

    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.post = post
            comment.author = request.user
            parent_id = request.POST.get('parent_id')
            if parent_id:
                comment.parent = get_object_or_404(Comment, pk=parent_id)
            comment.save()
            messages.success(request, 'Comment added!')
            return redirect('post_detail', pk=pk)

    return render(request, 'post_detail.html', {
        'post': post,
        'comments': comments,
        'comment_form': comment_form,
        'is_liked': post.is_liked_by(request.user),
    })


@login_required
@require_POST
def post_delete_view(request, pk):
    """Delete a post (only by its author)."""
    post = get_object_or_404(Post, pk=pk, author=request.user)
    post.delete()
    messages.success(request, 'Post deleted.')
    return redirect('feed')


@login_required
@require_POST
def like_post_view(request, pk):
    """Toggle like on a post; returns JSON for AJAX calls."""
    post = get_object_or_404(Post, pk=pk)
    user = request.user
    if post.is_liked_by(user):
        post.likes.remove(user)
        liked = False
    else:
        post.likes.add(user)
        liked = True
    return JsonResponse({'liked': liked, 'count': post.get_likes_count()})


# ─── Comment Views ──────────────────────────────────────────────────────────────

@login_required
@require_POST
def add_comment_view(request, post_pk):
    """Add a comment (or reply) to a post via AJAX or form submit."""
    post = get_object_or_404(Post, pk=post_pk)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.author = request.user
        parent_id = request.POST.get('parent_id')
        if parent_id:
            comment.parent = get_object_or_404(Comment, pk=parent_id)
        comment.save()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'comment_id': comment.pk,
                'author': comment.author.username,
                'avatar': comment.author.profile.avatar.url if comment.author.profile.avatar else '',
                'content': comment.content,
                'created_at': comment.created_at.strftime('%b %d, %Y'),
                'count': post.get_comments_count(),
            })
    return redirect('post_detail', pk=post_pk)


@login_required
@require_POST
def delete_comment_view(request, pk):
    """Delete a comment (only by its author)."""
    comment = get_object_or_404(Comment, pk=pk, author=request.user)
    post_pk = comment.post.pk
    comment.delete()
    messages.success(request, 'Comment deleted.')
    return redirect('post_detail', pk=post_pk)


# ─── Profile Views ──────────────────────────────────────────────────────────────

@login_required
def profile_view(request, username):
    """Display a user's public profile with their posts."""
    profile_user = get_object_or_404(User, username=username)
    profile = profile_user.profile
    posts = profile_user.posts.all().prefetch_related('likes', 'comments')
    is_following = profile.is_followed_by(request.user)

    return render(request, 'profile.html', {
        'profile_user': profile_user,
        'profile': profile,
        'posts': posts,
        'is_following': is_following,
        'is_own_profile': request.user == profile_user,
        'followers_count': profile.get_followers_count(),
        'following_count': profile.get_following_count(),
    })


@login_required
def edit_profile_view(request):
    """Edit the current user's profile."""
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile', username=request.user.username)
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)

    return render(request, 'edit_profile.html', {
        'user_form': user_form,
        'profile_form': profile_form,
    })


# ─── Follow System ──────────────────────────────────────────────────────────────

@login_required
@require_POST
def follow_toggle_view(request, username):
    """Follow or unfollow a user; returns JSON for AJAX calls."""
    target_user = get_object_or_404(User, username=username)
    if target_user == request.user:
        return JsonResponse({'error': 'Cannot follow yourself'}, status=400)

    profile = target_user.profile
    if profile.is_followed_by(request.user):
        profile.followers.remove(request.user)
        following = False
    else:
        profile.followers.add(request.user)
        following = True

    return JsonResponse({
        'following': following,
        'followers_count': profile.get_followers_count(),
    })


# ─── Search ─────────────────────────────────────────────────────────────────────

@login_required
def search_view(request):
    """Search users and posts by keyword."""
    query = request.GET.get('q', '').strip()
    users = []
    posts = []
    if query:
        users = list(User.objects.filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query)
        ).select_related('profile').exclude(pk=request.user.pk)[:10])

        following_ids = set(
            Profile.objects.filter(followers=request.user).values_list('user_id', flat=True)
        )
        for u in users:
            u.is_followed = u.id in following_ids

        posts = Post.objects.filter(
            content__icontains=query
        ).select_related('author', 'author__profile')[:20]

    return render(request, 'search.html', {
        'query': query,
        'users': users,
        'posts': posts,
    })


# ─── Followers / Following Lists ────────────────────────────────────────────────

@login_required
def followers_view(request, username):
    """List all followers of a user."""
    profile_user = get_object_or_404(User, username=username)
    followers = list(profile_user.profile.followers.all().select_related('profile'))
    following_ids = set(
        Profile.objects.filter(followers=request.user).values_list('user_id', flat=True)
    )
    for u in followers:
        u.is_followed = u.id in following_ids
    return render(request, 'followers.html', {
        'profile_user': profile_user,
        'users': followers,
        'list_type': 'Followers',
    })


@login_required
def following_view(request, username):
    """List all users that a user is following."""
    profile_user = get_object_or_404(User, username=username)
    following_profiles = Profile.objects.filter(followers=profile_user).select_related('user')
    following_users = [p.user for p in following_profiles]
    following_ids = set(
        Profile.objects.filter(followers=request.user).values_list('user_id', flat=True)
    )
    for u in following_users:
        u.is_followed = u.id in following_ids
    return render(request, 'followers.html', {
        'profile_user': profile_user,
        'users': following_users,
        'list_type': 'Following',
    })
