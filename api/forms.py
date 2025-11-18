# api/forms.py
from django import forms
from .models import CargaMasiva

class CargaMasivaForm(forms.ModelForm):
    """Formulario para subir archivos de carga masiva"""

    archivo = forms.FileField(
        required=True,
        label="Archivo Excel/CSV",
        widget=forms.ClearableFileInput(attrs={
            "class": "form-control",
            "accept": ".xlsx,.xls,.csv"
        })
    )

    class Meta:
        model = CargaMasiva
        fields = ['archivo_nombre']

    def save(self, commit=True, user=None, file_path=None):
        carga = super().save(commit=False)

        if user:
            carga.iniciado_por = user
        if file_path:
            carga.archivo_path = file_path

        if commit:
            carga.save()
        return carga
