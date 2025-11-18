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
    
    # Hacemos archivo_nombre opcional para generarlo automáticamente
    archivo_nombre = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.HiddenInput()  # Campo oculto
    )

    class Meta:
        model = CargaMasiva
        fields = ['tipo_carga', 'mercado', 'archivo_nombre']  # ← AGREGADOS
        widgets = {
            'tipo_carga': forms.Select(attrs={'class': 'form-control'}),
            'mercado': forms.Select(attrs={'class': 'form-control'}),
        }

    def clean_archivo_nombre(self):
        """Si no se proporciona, usar el nombre del archivo subido"""
        archivo_nombre = self.cleaned_data.get('archivo_nombre')
        archivo = self.files.get('archivo')
        
        # Si no hay nombre, usar el del archivo
        if not archivo_nombre and archivo:
            return archivo.name
        
        return archivo_nombre or 'sin_nombre.xlsx'

    def clean_archivo(self):
        """Validar el archivo subido"""
        archivo = self.cleaned_data.get('archivo')
        
        if archivo:
            # Validar tamaño (5MB máximo)
            if archivo.size > 5 * 1024 * 1024:
                raise forms.ValidationError("El archivo no debe superar 5MB")
            
            # Validar extensión
            nombre = archivo.name.lower()
            if not (nombre.endswith('.xlsx') or nombre.endswith('.xls') or nombre.endswith('.csv')):
                raise forms.ValidationError("Solo se aceptan archivos .xlsx, .xls o .csv")
        
        return archivo

    def save(self, commit=True, user=None, file_path=None):
        carga = super().save(commit=False)

        if user:
            carga.iniciado_por = user
        if file_path:
            carga.archivo_path = file_path
        
        # Si no hay archivo_nombre, asignarlo del archivo
        if not carga.archivo_nombre:
            archivo = self.cleaned_data.get('archivo')
            if archivo:
                carga.archivo_nombre = archivo.name

        if commit:
            carga.save()
        return carga