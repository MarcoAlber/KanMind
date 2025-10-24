from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.models import User


class EmailAuthTokenSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("Benutzer mit dieser Email existiert nicht")
        
        user = authenticate(username=user.username, password=password)

        if not user:
            raise serializers.ValidationError("Ungültige Anmeldedaten.")

        data['user'] = user
        return data


class RegistrationSerializer(serializers.ModelSerializer):
    repeated_password = serializers.CharField(write_only=True)
    fullname = serializers.CharField()

    class Meta:
        model = User
        fields = ['fullname', 'email', 'password', 'repeated_password']
        extra_kwargs = {
            'password': {
                'write_only': True
            }
        }

    def validate(self, data):
        if data['password'] != data['repeated_password']:
            raise serializers.ValidationError({'repeated_password': 'Passwords do not match'})
        return data    

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Diese E-Mail wird bereits verwendet.")
        return value
    
    def create(self, validated_data):
        password = validated_data.pop('password')
        validated_data.pop('repeated_password')
        full_name = validated_data.pop('fullname')

        parts = full_name.strip().split()
        first_name = parts[0]
        last_name = ' '.join(parts[1:])
  
        account = User(email=self.validated_data['email'],  username=self.validated_data['email'], first_name=first_name, last_name=last_name)
        account.set_password(password)
        account.save()
        return account