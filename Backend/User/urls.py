from django.urls import path
from .views import LoginView,  PostListCreateView, PostRetrieveUpdateDestroyView, LikePostView,CommentListView,CommentCreateView,PostListOrSearchView,GetAlumniByUsernameView

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('posts/', PostListCreateView.as_view(), name='post-list-create'),
    path('posts/<int:pk>/', PostRetrieveUpdateDestroyView.as_view(), name='post-detail'),
    path('posts/<int:pk>/like/', LikePostView.as_view(), name='post-like'),
    path('posts/<int:post_id>/comments/', CommentListView.as_view(), name='comment-list'),
    path('posts/<int:post_id>/comments/create/', CommentCreateView.as_view(), name='comment-create'),
    path('allposts/', PostListOrSearchView.as_view(), name='view-all-posts'),
    path('alumni/', GetAlumniByUsernameView.as_view(), name='get-alumni-by-username'),

]