from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate
from .models import CustomUser

# class SignUpForm(UserCreationForm):
#     email = forms.EmailField(required=True)
#     first_name = forms.CharField(max_length=30)
#     last_name = forms.CharField(max_length=30)
#     phone = forms.CharField(max_length=15, required=False)
    
#     class Meta:
#         model = CustomUser
#         fields = ('username', 'email', 'first_name', 'last_name', 'phone', 'password1', 'password2')

class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    phone = forms.CharField(max_length=15, required=False)
    
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'phone', 'password1', 'password2')
    
    def clean_email(self):
        email = self.cleaned_data['email']
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email
    
class LoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)
    show_password = forms.BooleanField(required=False, label="Show Password")
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password'].widget.attrs.update({'id': 'password-field'})
    
    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')
        
        if username and password:
            try:
                user = CustomUser.objects.get(username=username)
                if user.is_locked:
                    raise forms.ValidationError("Account is locked. Contact admin for password reset.")
                
                user_auth = authenticate(username=username, password=password)
                if user_auth is None:
                    user.increment_failed_attempts()
                    remaining_attempts = 3 - user.failed_login_attempts
                    if remaining_attempts > 0:
                        raise forms.ValidationError(f"Invalid credentials. {remaining_attempts} attempts remaining.")
                    else:
                        raise forms.ValidationError("Account locked after 3 failed attempts. Contact admin.")
                else:
                    user.reset_failed_attempts()
                    
            except CustomUser.DoesNotExist:
                raise forms.ValidationError("Invalid credentials.")
        
        return cleaned_data