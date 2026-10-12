from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Profile(models.Model):
    """Extended user profile with bio, avatar, and follower relationships."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(max_length=500, blank=True)
    avatar = models.ImageField(upload_to='avatars/', default='avatars/default.png', blank=True)
    website = models.URLField(blank=True)
    location = models.CharField(max_length=100, blank=True)
    followers = models.ManyToManyField(
        User, related_name='following', blank=True
    )
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'{self.user.username} Profile'

    def get_followers_count(self):
        return self.followers.count()

    def get_following_count(self):
        return Profile.objects.filter(followers=self.user).count()

    def is_followed_by(self, user):
        return self.followers.filter(pk=user.pk).exists()


class Post(models.Model):
    """User post with optional image, content, likes, and timestamps."""
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    content = models.TextField(max_length=2000)
    image = models.ImageField(upload_to='posts/', blank=True, null=True)
    likes = models.ManyToManyField(User, related_name='liked_posts', blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.author.username}: {self.content[:50]}'

    def get_likes_count(self):
        return self.likes.count()

    def is_liked_by(self, user):
        return self.likes.filter(pk=user.pk).exists()

    def get_comments_count(self):
        return self.comments.count()


class Comment(models.Model):
    """Comment on a post, supports nested replies via parent field."""
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField(max_length=500)
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies'
    )
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'{self.author.username} on {self.post}: {self.content[:30]}'
