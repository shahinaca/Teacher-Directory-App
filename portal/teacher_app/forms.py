from django import forms
from django.core.validators import FileExtensionValidator

from .models import Teacher


class ImportFileForm(forms.Form):
    names = forms.FileField(validators=[FileExtensionValidator(allowed_extensions=['csv'])])
    images = forms.FileField(validators=[FileExtensionValidator(allowed_extensions=['zip'])])

    def clean(self):
        pass


class TeacherForm(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = [
            'first_name',
            'last_name',
            'profile_picture',
            'email_address',
            'phone_number',
            'room_number',
            'subjects_taught'
        ]

    def __init__(self, *args, **kwargs):
        super(TeacherForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].error_messages = {'required': 'The field First Name is required. '}
        self.fields['last_name'].error_messages = {'required': 'The field Last Name is required. '}
        self.fields['email_address'].error_messages = {'required': 'The field Email is required. '}
