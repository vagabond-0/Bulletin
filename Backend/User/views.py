from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import Alumni, Post,Comment
from .serializer import AlumniSerializer, PostSerializer,CommentSerializer

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
            user = authenticate(username=alumni.user.username, password=password)
            
            if user:
                refresh = RefreshToken.for_user(user)
                serializer = AlumniSerializer(alumni)
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'user': serializer.data
                })
            else:
                return Response(
                    {'error': 'Invalid credentials'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
        except Alumni.DoesNotExist:
            return Response(
                {'error': 'Alumni not found'},
                status=status.HTTP_404_NOT_FOUND
            )

class PostListCreateView(generics.ListCreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def perform_create(self, serializer):
        try:
            alumni = Alumni.objects.get(user=self.request.user)
            serializer.save(alumni=alumni)
        except Alumni.DoesNotExist:
            raise ValidationError('User is not associated with an alumni profile')

class PostRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get_queryset(self):
        return Post.objects.filter(alumni__user=self.request.user)

class LikePostView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request, pk):
        try:
            post = Post.objects.get(pk=pk)
            post.likes += 1
            post.save()
            return Response({'likes': post.likes}, status=status.HTTP_200_OK)
        except Post.DoesNotExist:
            return Response(
                {'error': 'Post not found'},
                status=status.HTTP_404_NOT_FOUND
            )

class CommentCreateView(APIView):
    def post(self, request, post_id):
        try:
            post = Post.objects.get(pk=post_id)
        except Post.DoesNotExist:
            return Response({'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)
        
        request.data['post'] = post_id  # Ensure post is linked
        serializer = CommentSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()  # Save the comment
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class CommentListView(APIView):
    def get(self, request, post_id):
        try:
            post = Post.objects.get(pk=post_id)
        except Post.DoesNotExist:
            return Response({'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)

        comments = Comment.objects.filter(post=post)  
        serializer = CommentSerializer(comments, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

