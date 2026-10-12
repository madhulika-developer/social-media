from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Feed
    path('', views.feed_view, name='feed'),

    # Posts
    path('post/<int:pk>/', views.post_detail_view, name='post_detail'),
    path('post/<int:pk>/delete/', views.post_delete_view, name='post_delete'),
    path('post/<int:pk>/like/', views.like_post_view, name='like_post'),

    # Comments
    path('post/<int:post_pk>/comment/', views.add_comment_view, name='add_comment'),
    path('comment/<int:pk>/delete/', views.delete_comment_view, name='delete_comment'),

    # Profiles
    path('profile/<str:username>/', views.profile_view, name='profile'),
    path('profile/<str:username>/follow/', views.follow_toggle_view, name='follow_toggle'),
    path('profile/<str:username>/followers/', views.followers_view, name='followers'),
    path('profile/<str:username>/following/', views.following_view, name='following'),
    path('edit-profile/', views.edit_profile_view, name='edit_profile'),

    # Search
    path('search/', views.search_view, name='search'),
]
