from accounts.api.serializers import UserSerializer
from comments.models import Comment
from django.contrib.contenttypes.models import ContentType
from likes.models import Like
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from tweets.models import Tweet


class LikeSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Like
        fields = ('user', 'created_at')


class LikeSerializerForCreateAndCancel(serializers.ModelSerializer):
    object_id = serializers.IntegerField()
    content_type = serializers.ChoiceField(choices=['comment', 'tweet'])

    class Meta:
        model = Like
        fields = ('object_id', 'content_type')

    def _get_model_class(self, data):
        if data['content_type'] == 'comment':
            return Comment
        if data['content_type'] == 'tweet':
            return Tweet
        return None


    def validate(self, data):
        model_class = self._get_model_class(data)
        if model_class is None:
            raise ValidationError({
                'content_type': 'Content type does not exist'
            })
        liked_object = model_class.objects.filter(id=data['object_id']).first()
        if liked_object is None:
            raise ValidationError({'object_id': 'object does not exist'})
        return data


class LikeSerializerForCreate(LikeSerializerForCreateAndCancel):

    def get_or_create(self):
        model_class = self._get_model_class(self.validated_data)
        content_type = ContentType.objects.get_for_model(model_class)
        return Like.objects.get_or_create(
            user=self.context['request'].user,
            content_type=content_type,
            object_id=self.validated_data['object_id'],
        )


class LikeSerializerForCancel(LikeSerializerForCreateAndCancel):

    def cancel(self):
        model_class = self._get_model_class(self.validated_data)
        content_type = ContentType.objects.get_for_model(model_class)
        Like.objects.filter(
            user=self.context['request'].user,
            content_type=content_type,
            object_id=self.validated_data['object_id'],
        ).delete()
