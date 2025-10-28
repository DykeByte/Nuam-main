# accounts/forms.py - CREAR ESTE ARCHIVO
from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import re


class RegistroForm(forms.Form):
    """Formulario de registro con validaciones robustas"""
    
    username = forms.CharField(
        max_length=150,
        required=True,
        label='Nombre de Usuario',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Solo letras, números y guiones bajos',
            'pattern': '[a-zA-Z0-9_]+',
            'title': 'Solo letras, números y guiones bajos'
        })
    )
    
    email = forms.EmailField(
        required=True,
        label='Correo Electrónico',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'ejemplo@correo.com'
        })
    )
    
    password = forms.CharField(
        min_length=8,
        required=True,
        label='Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Mínimo 8 caracteres'
        })
    )
    
    password2 = forms.CharField(
        min_length=8,
        required=True,
        label='Confirmar Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Repite tu contraseña'
        })
    )
    
    def clean_username(self):
        """Validar nombre de usuario"""
        username = self.cleaned_data.get('username')
        
        # 1. Solo letras, números y guiones bajos
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            raise ValidationError(
                'El nombre de usuario solo puede contener letras, números y guiones bajos (_).'
            )
        
        # 2. Debe empezar con letra
        if not username[0].isalpha():
            raise ValidationError(
                'El nombre de usuario debe comenzar con una letra.'
            )
        
        # 3. Mínimo 3 caracteres
        if len(username) < 3:
            raise ValidationError(
                'El nombre de usuario debe tener al menos 3 caracteres.'
            )
        
        # 4. Verificar que no exista
        if User.objects.filter(username=username).exists():
            raise ValidationError(
                'Este nombre de usuario ya está en uso.'
            )
        
        return username
    
    def clean_email(self):
        """Validar correo electrónico"""
        email = self.cleaned_data.get('email')
        
        # 1. Validar formato de email
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, email):
            raise ValidationError(
                'Ingresa un correo electrónico válido (ejemplo@correo.com).'
            )
        
        # 2. No permitir correos temporales comunes
        dominios_bloqueados = [
            'tempmail.com', 'throwaway.email', '10minutemail.com',
            'guerrillamail.com', 'mailinator.com'
        ]
        dominio = email.split('@')[1].lower()
        if dominio in dominios_bloqueados:
            raise ValidationError(
                'No se permiten correos temporales.'
            )
        
        # 3. Verificar que no exista
        if User.objects.filter(email=email).exists():
            raise ValidationError(
                'Este correo electrónico ya está registrado.'
            )
        
        return email.lower()
    
    def clean_password(self):
        """Validar contraseña robusta"""
        password = self.cleaned_data.get('password')
        
        # 1. Mínimo 8 caracteres
        if len(password) < 8:
            raise ValidationError(
                'La contraseña debe tener al menos 8 caracteres.'
            )
        
        # 2. Debe contener al menos una letra mayúscula
        if not re.search(r'[A-Z]', password):
            raise ValidationError(
                'La contraseña debe contener al menos una letra mayúscula.'
            )
        
        # 3. Debe contener al menos una letra minúscula
        if not re.search(r'[a-z]', password):
            raise ValidationError(
                'La contraseña debe contener al menos una letra minúscula.'
            )
        
        # 4. Debe contener al menos un número
        if not re.search(r'\d', password):
            raise ValidationError(
                'La contraseña debe contener al menos un número.'
            )
        
        # 5. Debe contener al menos un carácter especial
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValidationError(
                'La contraseña debe contener al menos un carácter especial (!@#$%^&*...).'
            )
        
        # 6. No permitir contraseñas comunes
        contraseñas_comunes = [
            '12345678', 'password', 'Password1', 'qwerty123', 
            'abc12345', '123456789', 'password1', 'Qwerty123'
        ]
        if password in contraseñas_comunes:
            raise ValidationError(
                'Esta contraseña es demasiado común. Elige una más segura.'
            )
        
        # 7. No debe contener el username
        username = self.data.get('username', '')
        if username.lower() in password.lower():
            raise ValidationError(
                'La contraseña no debe contener tu nombre de usuario.'
            )
        
        return password
    
    def clean(self):
        """Validación general del formulario"""
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password2 = cleaned_data.get('password2')
        
        # Verificar que las contraseñas coincidan
        if password and password2:
            if password != password2:
                raise ValidationError({
                    'password2': 'Las contraseñas no coinciden.'
                })
        
        return cleaned_data