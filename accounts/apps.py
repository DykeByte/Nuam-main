# accounts/apps.py
from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'
    
    def ready(self):
        """Importar señales cuando la app esté lista"""
        import accounts.models  # Esto asegura que las señales se registren