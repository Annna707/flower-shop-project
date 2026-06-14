from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User

from .models import Profile

INPUT = {'class': 'form-control'}


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Логин'
        self.fields['password'].label = 'Пароль'
        self.fields['username'].widget.attrs.update({
            **INPUT,
            'placeholder': 'Введите логин',
            'autocomplete': 'username',
        })
        self.fields['password'].widget.attrs.update({
            **INPUT,
            'placeholder': 'Введите пароль',
            'autocomplete': 'current-password',
        })
        self.error_messages['invalid_login'] = (
            'Неверный логин или пароль. Проверьте данные и попробуйте снова.'
        )


class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'password1', 'password2')
        labels = {
            'username': 'Логин',
            'password1': 'Пароль',
            'password2': 'Подтверждение пароля',
        }
        widgets = {
            'username': forms.TextInput(attrs={
                **INPUT,
                'placeholder': 'Придумайте логин',
                'autocomplete': 'username',
            }),
            'password1': forms.PasswordInput(attrs={
                **INPUT,
                'placeholder': 'Не менее 8 символов',
                'autocomplete': 'new-password',
            }),
            'password2': forms.PasswordInput(attrs={
                **INPUT,
                'placeholder': 'Повторите пароль',
                'autocomplete': 'new-password',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].help_text = (
            'Минимум 8 символов. Пароль не должен быть слишком простым '
            'или похожим на логин.'
        )


class ProfileEditForm(forms.ModelForm):
    first_name = forms.CharField(
        max_length=150,
        required=False,
        label='Имя',
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    last_name = forms.CharField(
        max_length=150,
        required=False,
        label='Фамилия',
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
    )

    class Meta:
        model = Profile
        fields = ['phone', 'address', 'birth_date']
        widgets = {
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+7 (900) 123-45-67',
            }),
            'address': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Город, улица, дом, квартира',
            }),
            'birth_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
            }),
        }
        labels = {
            'phone': 'Телефон',
            'address': 'Адрес по умолчанию',
            'birth_date': 'Дата рождения',
        }

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
        self.fields['first_name'].initial = user.first_name
        self.fields['last_name'].initial = user.last_name
        self.fields['email'].initial = user.email

    def save(self, commit=True):
        profile = super().save(commit=False)
        self.user.first_name = self.cleaned_data['first_name']
        self.user.last_name = self.cleaned_data['last_name']
        self.user.email = self.cleaned_data['email']
        self.user.save()
        profile.user = self.user
        if commit:
            profile.save()
        return profile
