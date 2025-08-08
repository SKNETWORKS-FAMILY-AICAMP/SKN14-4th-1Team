from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django import forms

# 사용자 상세정보를 저장할 모델
class UserDetail(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    birthday = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=[('M', 'Male'), ('F', 'Female')], null=True, blank=True) # max_length=10 => 1로 수정
    is_pregnant = models.BooleanField(default=False)
    health_concerns = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.user.username

# 회원가입 시 사용할 폼
class UserForm(UserCreationForm):
    email = forms.EmailField(required=True)
    birthday = forms.DateField(label="생년월일", required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    gender = forms.ChoiceField(label='성별', choices=[('M', 'Male'), ('F', 'Female')], required=False)
    is_pregnant = forms.BooleanField(label='임신여부', required=False)
    health_concerns = forms.CharField(label='건강 관심사', 
                                      widget=forms.Textarea, 
                                      required=False)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")