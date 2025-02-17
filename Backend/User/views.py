from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import Alumni, Post,Comment
from .serializer import AlumniSerializer, PostSerializer,CommentSerializer
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.utils.decorators import method_decorator
from django.db.models import Q
from rest_framework.generics import RetrieveAPIView
from django.contrib.auth.hashers import check_password
from django.shortcuts import get_object_or_404

@method_decorator(csrf_exempt, name='dispatch')
class LoginView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response(
                {'error': 'Please provide both email and password'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            alumni = Alumni.objects.get(email=email)
            print(f"Alumni found: {alumni.username}")

            if password != alumni.password:
                print(password)
                print("password is ", alumni.password)
                print("Password mismatch!")
                return Response(
                    {'error': 'Invalid credentials'},
                    status=status.HTTP_401_UNAUTHORIZED
                )

            refresh = RefreshToken.for_user(alumni)
            serializer = AlumniSerializer(alumni)

            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': serializer.data
            })

        except Alumni.DoesNotExist:
            print("Alumni not found!")
            return Response(
                {'error': 'Alumni not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        except Exception as e:
            print(f"Unexpected error: {str(e)}")  # Debugging line
            return Response(
                {'error': 'Something went wrong', 'details': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


            
@method_decorator(csrf_exempt, name='dispatch')
class PostListCreateView(generics.ListCreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def perform_create(self, serializer):
        try:
            alumni = Alumni.objects.get(email=self.request.user.email)
            serializer.save(alumni=alumni)
        except Alumni.DoesNotExist:
            raise ValidationError('User is not associated with an alumni profile')

@method_decorator(csrf_exempt, name='dispatch')
class PostRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get_queryset(self):
        return Post.objects.filter(alumni__user=self.request.user)


@method_decorator(csrf_exempt, name='dispatch')
class LikePostView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request, pk):
        try:
            post = Post.objects.get(pk=pk)
            alumni = Alumni.objects.get(email=self.request.user.email)

            if alumni in post.likes.all():
                post.likes.remove(alumni)
                action = 'unliked'
            else:
                post.likes.add(alumni)
                action = 'liked'

            return Response({'status': f'Post {action}', 'likes_count': post.likes.count()}, status=status.HTTP_200_OK)
        except Post.DoesNotExist:
            return Response(
                {'error': 'Post not found'},
                status=status.HTTP_404_NOT_FOUND
            )


@method_decorator(csrf_exempt, name='dispatch')
class LikeProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request, pk):
        try:
            target_alumni = Alumni.objects.get(pk=pk)
            liker_alumni = Alumni.objects.get(email=self.request.user.email)

            if liker_alumni in target_alumni.likes.all():
                target_alumni.likes.remove(liker_alumni)
                action = 'unliked'
            else:
                target_alumni.likes.add(liker_alumni)
                action = 'liked'

            return Response({'status': f'Profile {action}', 'likes_count': target_alumni.likes.count()}, status=status.HTTP_200_OK)
        except Alumni.DoesNotExist:
            return Response(
                {'error': 'Alumni not found'},
                status=status.HTTP_404_NOT_FOUND
            )


@method_decorator(csrf_exempt, name='dispatch')
class CommentCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request, post_id):
        try:
            post = Post.objects.get(pk=post_id)
        except Post.DoesNotExist:
            return Response({'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)

        alumni = Alumni.objects.get(email=self.request.user.email)
        serializer = CommentSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(post=post, alumni=alumni)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name='dispatch')
class CommentListView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request, post_id):
        try:
            post = Post.objects.get(pk=post_id)
        except Post.DoesNotExist:
            return Response({'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)

        comments = Comment.objects.filter(post=post)
        serializer = CommentSerializer(comments, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

class PostListOrSearchView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        search_query = request.GET.get('search', '').strip()
        
        if search_query is not None and search_query != '':
            users = Alumni.objects.filter(
                Q(username__icontains=search_query) |
                Q(email__icontains=search_query)
            )
            serializer = AlumniSerializer(users, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        else:  
            posts = Post.objects.all().order_by('-posted_date')
            serializer = PostSerializer(posts, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
class GetAlumniByUsernameView(RetrieveAPIView):
    serializer_class = AlumniSerializer

    def get(self, request, *args, **kwargs):
        try:
            username = request.query_params.get("username")
            if not username:
                return Response({"error": "Username parameter is required"}, status=status.HTTP_400_BAD_REQUEST)
            
            alumni = get_object_or_404(Alumni, username=username)
            
            # Serialize alumni details
            alumni_serializer = self.get_serializer(alumni)
            
            # Get posts by this alumni
            posts = Post.objects.filter(alumni=alumni).order_by('-posted_date')

            enriched_posts = []
            for post in posts:
                # Get post comments
                comments = Comment.objects.filter(post=post)
                comment_list = [
                    {
                        "id": comment.id,
                        "post": comment.post.id,
                        "alumni": comment.alumni.id,
                        "alumni_username": comment.alumni.username,
                        "comment_text": comment.comment_text,
                        "posted_date": comment.posted_date,
                    }
                    for comment in comments
                ]

                # Create post object with likes and comments
                enriched_posts.append({
                    "post": {
                        "id": post.id,
                        "alumni": {
                            "id": alumni.id,
                            "username": alumni.username,
                            "email": alumni.email,
                            "company": alumni.company,
                            "designation": alumni.designation,
                            "profile_picture_url": alumni.profile_picture_url
                        },
                        "posted_date": post.posted_date,
                        "description": post.description,
                        "image_link": post.image_link,
                        "video_link": post.video_link,
                        "likes": list(post.likes.values_list('id', flat=True)),  # List of user IDs who liked
                        "comments": comment_list  # Ensure comments are only added once
                    },
                    "likes_count": post.likes.count(),
                })

            return Response({
                "alumni": alumni_serializer.data,
                "posts": enriched_posts
            }, status=status.HTTP_200_OK)

        except Exception as e:
            import logging
            logging.error(f"Error in GetAlumniByUsernameView: {str(e)}")
            return Response({"error": "An internal error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
