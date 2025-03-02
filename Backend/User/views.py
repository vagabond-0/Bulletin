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
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from django.utils.decorators import method_decorator
from django.db.models import Q
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth.models import AnonymousUser
from rest_framework.generics import RetrieveAPIView
from django.contrib.auth.hashers import check_password
from django.shortcuts import get_object_or_404
import traceback
import logging
from django.apps import apps
from django.contrib.auth.hashers import check_password
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework import status, permissions, generics
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView
from .authentication import AlumniJWTAuthentication
from django.core.mail import send_mail
from django.conf import settings

logger = logging.getLogger(__name__)


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
            print(f"[DEBUG] Alumni found: {alumni.username}")

            if password != alumni.password:  
                print("[ERROR] Password mismatch!")
                return Response(
                    {'error': 'Invalid credentials'},
                    status=status.HTTP_401_UNAUTHORIZED
                )

            
            refresh = RefreshToken.for_user(alumni)
            refresh['alumni_id'] = alumni.id
            refresh['email'] = alumni.email

            serializer = AlumniSerializer(alumni)

            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': serializer.data
            })

        except Alumni.DoesNotExist:
            print("[ERROR] Alumni not found!")
            return Response(
                {'error': 'Alumni not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            print(f"[ERROR] Unexpected error in LoginView: {str(e)}")
            traceback.print_exc()
            return Response(
                {'error': 'Something went wrong', 'details': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
class PostListCreateView(generics.ListCreateAPIView):
        queryset = Post.objects.all()
        serializer_class = PostSerializer
        authentication_classes = [AlumniJWTAuthentication]
        permission_classes = [permissions.IsAuthenticated]
        
        def create(self, request, *args, **kwargs):
            try:
                print("[DEBUG] Starting create method")
                print(f"[DEBUG] Request user: {request.user}")
                print(f"[DEBUG] Request data: {request.data}")
                
                serializer = self.get_serializer(data=request.data)
                print("[DEBUG] Created serializer")
                
                if not serializer.is_valid():
                    print(f"[ERROR] Serializer errors: {serializer.errors}")
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                    
                print(f"[DEBUG] Serializer is valid. Validated data: {serializer.validated_data}")
                
       
                try:
                    post = serializer.save(alumni=request.user)
                    alumni_emails = [alumini.email for alumini in Alumni.objects.all()]
                    Subject="New Post Posted"
                    message = f"A new post has been created by {request.user}."
                    email_from = settings.DEFAULT_FROM_EMAIL
                    send_mail(Subject, message, email_from, alumni_emails)
                    print("[DEBUG] Email sent to all alumni.")
                    print(f"[DEBUG] Post saved successfully: {post.id}")
                    return Response(self.get_serializer(post).data, status=status.HTTP_201_CREATED)
                except Exception as save_error:
                    print(f"[ERROR] Error saving post: {str(save_error)}")
                    import traceback
                    traceback.print_exc()
                    return Response(
                        {'error': f'Error saving post: {str(save_error)}'}, 
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
                    
            except Exception as e:
                print(f"[ERROR] Unexpected error in create: {str(e)}")
                import traceback
                traceback.print_exc()
                return Response(
                    {'error': f'Unexpected error: {str(e)}'}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        def post(self, request, *args, **kwargs):
            try:
                print(f"[DEBUG] Incoming POST request data: {request.data}")
                return super().post(request, *args, **kwargs)
            except Exception as e:
                print(f"[ERROR] Error in post method: {str(e)}")
                traceback.print_exc()
                raise


@method_decorator(csrf_exempt, name='dispatch')
class PostRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [AlumniJWTAuthentication]

    def get_queryset(self):
        print("[DEBUG] Starting get_queryset method")
        print(f"[DEBUG] Request user: {self.request.user}")

        if self.request.user.is_authenticated:
            if isinstance(self.request.user, Alumni):
                return Post.objects.filter(alumni=self.request.user)
            else:
                return Post.objects.none()
        return Post.objects.none()

@method_decorator(csrf_exempt, name='dispatch')
class LikePostView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [AlumniJWTAuthentication]

    def post(self, request, pk):
        try:
            post = Post.objects.get(pk=pk)
           
            alumni = self.request.user

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
        except Exception as e:
            import logging
            logging.error(f"Error in LikePostView: {str(e)}")
            return Response(
                {'error': 'An unexpected error occurred'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@method_decorator(csrf_exempt, name='dispatch')
class LikeProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [AlumniJWTAuthentication]

    def post(self, request, pk):
        try:
            target_post = Post.objects.get(pk=pk)
            liker_alumni = self.request.user  

            if liker_alumni in target_post.likes.all():
                target_post.likes.remove(liker_alumni)
                action = 'unliked'
            else:
                target_post.likes.add(liker_alumni)
                action = 'liked'

            return Response(
                {'status': f'Post {action}', 'likes_count': target_post.likes.count()},
                status=status.HTTP_200_OK
            )
        except Post.DoesNotExist:
            return Response({'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            import logging
            logging.error(f"Error in LikePostView: {str(e)}")
            return Response({'error': 'An unexpected error occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@method_decorator(csrf_exempt, name='dispatch')
class CommentCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [AlumniJWTAuthentication]

    def post(self, request, post_id):
        try:
            post = Post.objects.get(pk=post_id)
            # Directly use request.user as Alumni
            alumni = self.request.user
            
            serializer = CommentSerializer(data=request.data)

            if serializer.is_valid():
                serializer.save(post=post, alumni=alumni)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Post.DoesNotExist:
            return Response({'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            import logging
            logging.error(f"Error in CommentCreateView: {str(e)}")
            return Response({'error': 'An unexpected error occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@method_decorator(csrf_exempt, name='dispatch')
class CommentListView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [AlumniJWTAuthentication]

    def get(self, request, post_id):
        try:
            post = Post.objects.get(pk=post_id)
            comments = Comment.objects.filter(post=post)
            serializer = CommentSerializer(comments, many=True)

            return Response(serializer.data, status=status.HTTP_200_OK)
        except Post.DoesNotExist:
            return Response({'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            import logging
            logging.error(f"Error in CommentListView: {str(e)}")
            return Response({'error': 'An unexpected error occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class PostListOrSearchView(APIView):
    
    def get(self, request):
        try:
            search_query = request.GET.get('search', '').strip()
            logger.info(f"Search query received: {search_query}")

            if search_query:
                try:
                    users = Alumni.objects.filter(
                        Q(username__icontains=search_query) |
                        Q(company=search_query)
                    )
                    logger.info(f"Found {users.count()} users matching query")
                    
                    serializer = AlumniSerializer(users, many=True)
                    return Response(serializer.data, status=status.HTTP_200_OK)
                
                except Exception as e:
                    logger.error(f"Error during user search: {str(e)}", exc_info=True)
                    return Response(
                        {"error": "Error occurred while searching users"},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )

            try:
                posts = Post.objects.all().order_by('-posted_date')
                logger.info(f"Fetched {posts.count()} posts")
                
                serializer = PostSerializer(posts, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
                
            except Exception as e:
                logger.error(f"Error fetching posts: {str(e)}", exc_info=True)
                return Response(
                    {"error": "Error occurred while fetching posts"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
                
        except ValidationError as e:
            logger.error(f"Validation error: {str(e)}")
            return Response(
                {"error": "Invalid parameters provided"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        except Exception as e:
            logger.error(f"Unexpected error in PostListOrSearchView: {str(e)}", exc_info=True)
            return Response(
                {"error": "An unexpected error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class GetAlumniByUsernameView(RetrieveAPIView):
    serializer_class = AlumniSerializer

    def get(self, request, *args, **kwargs):
        try:
            username = request.query_params.get("username")
            if not username:
                return Response({"error": "Username parameter is required"}, status=status.HTTP_400_BAD_REQUEST)
            
            alumni = get_object_or_404(Alumni, username=username)
            
        
            alumni_serializer = self.get_serializer(alumni)
            
           
            posts = Post.objects.filter(alumni=alumni).order_by('-posted_date')

            enriched_posts = []
           
            for post in posts:
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
                        "likes": list(post.likes.values_list('id', flat=True)), 
                        "likes_count": len(list(post.likes.values_list('id', flat=True))),
                        "comments": comment_list  
                    },
                    
                })

            return Response({
                "alumni": alumni_serializer.data,
                "posts": enriched_posts
            }, status=status.HTTP_200_OK)

        except Exception as e:
            import logging
            logging.error(f"Error in GetAlumniByUsernameView: {str(e)}")
            return Response({"error": "An internal error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)