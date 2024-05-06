from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from .models import Category, Comment, Post

User = get_user_model()


class CreateUserForm(UserCreationForm):

    class Meta:
        model = User
        fields = ('username', 'email')


class UserEditForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email')


class CreatePostForm(forms.ModelForm):
    category = forms.ModelChoiceField(
        queryset=Category.objects,
        empty_label=None
    )

    class Meta:
        model = Post
        exclude = ('author', 'comment_count')
        widgets = {
            'pub_date': forms.DateInput(attrs={'type': 'date'})
        }


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('text',)
