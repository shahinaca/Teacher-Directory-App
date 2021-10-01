from django import forms

from .models import Teacher


class TeacherForm(forms.ModelForm):
    first_name = forms.CharField(
        required=True)
    last_name = forms.CharField(
        required=True)
    profile_picture = forms.CharField(
        required=False)
    email_address = forms.CharField(
        required=True)
    phone_number = forms.CharField(
        required=False)
    room_number = forms.CharField(
        required=False)
    subjects_taught = forms.CharField(
        required=False)
    profile_path = forms.CharField(
        required=False)

    class Meta:
        model = Teacher
        fields = [
            'first_name',
            'last_name',
            'profile_picture',
            'email_address',
            'phone_number',
            'room_number',
            'subjects_taught',
            'profile_path'
        ]

    def __init__(self, *args, **kwargs):
        super(TeacherForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].error_messages = {'required': 'The field First Name is required. '}
        self.fields['last_name'].error_messages = {'required': 'The field Last Name is required. '}
        self.fields['email_address'].error_messages = {'required': 'The field Email is required. '}
