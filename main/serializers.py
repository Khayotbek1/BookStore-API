from rest_framework.serializers import ModelSerializer
from .models import *

class AccountSerializer(ModelSerializer):
    class Meta:
        model = Account
        fields = ['id', 'username', 'password', 'first_name', 'last_name', 'image']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        return Account.objects.create_user(**validated_data)


class ImageSerializer(ModelSerializer):
    class Meta:
        model = Image
        fields = ['id', 'image']

class BookSerializer(ModelSerializer):
    images = ImageSerializer(many=True, read_only=True)
    class Meta:
        model = Book
        fields = '__all__'

class BookPostSerializer(ModelSerializer):
    class Meta:
        model = Book
        fields = '__all__'

        extra_kwargs = {
            'account': {'read_only': True}
        }


class BookMarkSoldSerializer(ModelSerializer):
    class Meta:
        model = Book
        fields = ('id', 'sold')
        extra_kwargs = {
            'sold': {'read_only': True}
        }
