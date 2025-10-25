from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import status 
from.serializers import RegistrationSerializer, EmailAuthTokenSerializer
from django.contrib.auth.models import User


class RegistrationView(APIView):
    """
    API endpoint for registering a new user.
    Allows anyone to create an account and returns an auth token on success.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        """
        Handle POST request to register a new user.
        Returns auth token, full name, email, and user ID if successful.
        """
        serializer = RegistrationSerializer(data=request.data)

        data = {}
        if serializer.is_valid():
            try:
                saved_account = serializer.save()
                token, _ = Token.objects.get_or_create(user=saved_account)

                data = {
                    'token': token.key,
                    'fullname': saved_account.first_name.capitalize() + ' ' + saved_account.last_name.capitalize(),
                    'email': saved_account.email,
                    'user_id': saved_account.id
                    }
                
                return Response(data, status=status.HTTP_201_CREATED)
            
            except:
                return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CustomLoginView(APIView):
    """
    API endpoint for user login using email and password.
    Returns auth token and user info on successful login.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        """
        Handle POST request to authenticate a user.
        Returns token, email, full name, and user ID if credentials are valid.
        """
        serializer = EmailAuthTokenSerializer(data=request.data)

        if serializer.is_valid():
            try:
                user = serializer.validated_data['user']
                token, _ = Token.objects.get_or_create(user=user)
                full_name = f"{user.first_name} {user.last_name}"

                data = {
                    'token': token.key,
                    'email': user.email,
                    'fullname': full_name,
                    'user_id': user.id
                }

                return Response(data, status=status.HTTP_200_OK)
            
            except:
                return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class EmailCheckView(APIView):
    """
    API endpoint to check if a given email exists in the system.
    Requires authentication.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Handle GET request with 'email' query parameter.
        Returns user ID, email, and full name if found.
        Returns 404 if email does not exist.
        """
        email = request.query_params.get('email')

        if not email:
            return Response(
                {"error": "Die E-Mail-Adresse fehlt oder hat ein falsches Format."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = User.objects.get(email=email)
            return Response({
                'id': user.id,
                'email': user.email,
                'fullname': f'{user.first_name} {user.last_name}'.strip()
            },status=status.HTTP_200_OK)
        
        except User.DoesNotExist:
            return Response({'error': 'E-Mail-Adresse wurde nicht gefunden'},
                             status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({
                "error": "Ein interner Serverfehler ist aufgetreten"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)