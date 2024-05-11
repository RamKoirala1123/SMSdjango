from django.contrib.auth import authenticate
from django.http import JsonResponse

from rest_framework.views import APIView
from rest_framework.parsers import JSONParser, FormParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from authentication.permissions import IsNotAuthenticated
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken

from authentication.serializers import NoticeSerializers, UserSerializer
from authentication.models import User,  Notice

# Create your views here.


class LoginView(APIView):
    parser_classes = (JSONParser,)
    permission_classes = (IsNotAuthenticated,)

    def get(self, request, *args, **kwargs):
        if request.user and request.user.is_authenticated:
            return JsonResponse({'success': 'Logged In'})
        return JsonResponse({'error': 'User is not logged in'})

    def post(self, request, *args, **kwargs):
        username = request.data.get(
            "username") if 'username' in request.data else request.data.get('email', '')
        password = request.data.get('password', '')
        status = {'error': 'Invalid (email or username)/password.'}
        if len(username) > 0 and len(password) > 0:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                if user.is_active:
                    refresh = RefreshToken.for_user(user)
                    return JsonResponse(data={"refresh": str(refresh), "access": str(refresh.access_token)}, status=200)
                else:
                    status = {'error': 'Account is not active.'}
            else:
                status = {'error': 'Invalid Credentials'}
        return JsonResponse(status, status=401)


class UserDetail(APIView):
    parser_classes = (JSONParser,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, username):
        status = 401
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            data = {'error': 'User does not exist'}
        else:
            serializer = UserSerializer(
                instance=user, many=False, context={'request': request})
            data = serializer.data
            delkey = ('date_joined', 'email', 'is_active', 'usertype',
                      'dob', 'is_staff', 'is_active')
            for key in delkey:
                data.pop(key, None)
            status = 200
        return JsonResponse(data=data, status=status)

    def post(self, request, *args, **kwargs):
        serializer = UserSerializer(instance=request.user, many=False, context={'request': request})
        return JsonResponse(serializer.data, status=200)

    def put(self, request, username):
        status = 401
        data = {'error': 'User not created nor updated'}
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            data = {'error': 'User does not exist'}
        else:
            if request.user == user:
                serializer = UserSerializer(
                    instance=request.user, data=request.data, partial=True, context={'request': request})
                if serializer.is_valid():
                    serializer.save()
                    data = serializer.data
                    status = 200
                else:
                    data = serializer.errors
        return JsonResponse(data, status=status)

    def delete(self, request, username):
        status = 401
        data = {'error': 'User not deleted'}
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            data = {'error': 'User does not exist'}
        else:
            if request.user == user:
                user.delete()
                data = {'success': 'User deleted'}
                status = 200
        return JsonResponse(data, status=status)


@api_view(['POST'])
@permission_classes([AllowAny, ])
def Create_User(request):
    serializer = UserSerializer(
        data=request.data, context={"request": request})
    if serializer.is_valid():
        serializer.save()
        return JsonResponse(serializer.data, status=201)
    return JsonResponse(serializer.errors, status=400)


@permission_classes([IsAuthenticated, ])
@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def Upload_Profile(request):
    user = request.user
    try:
        image = request.data['image']
    except KeyError:
        return JsonResponse({'error': 'No image uploaded'}, status=400)
    else:
        user.image = image
        user.save()
        return JsonResponse({'success': 'Image uploaded'}, status=201)


@permission_classes([IsAuthenticated, ])
@api_view(['POST'])
# @parser_classes([MultiPartParser, FormParser])
@parser_classes([JSONParser,])
def Add_Notice(request):    
    serializer = NoticeSerializers(
        data=request.data, context={"request": request})
    if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=201)
    return JsonResponse(serializer.errors, status=400)

class NoticeView(APIView):
    permission_classes = (AllowAny,)
    def get(self, request):
        notice = Notice.objects.all()
        serializer = NoticeSerializers(
            notice, context={'request': request}, many=True)
        return JsonResponse(serializer.data, status=200, safe=False)