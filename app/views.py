from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.views import View
from .models import Teacher
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.db.models import ObjectDoesNotExist
from django.core.paginator import Paginator #import Paginator
from django import forms
from .forms import TeacherForm
from django.contrib import messages
from zipfile import ZipFile
from django.conf import settings
from io import BytesIO
import os
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import io
import csv
# Create your views here.
#
class dashboard(View):

    def get(self, request):
        teachers = Teacher.objects.all()
        return render(request, 'dashboard.html', {'teachers': teachers, 'filename': 'dashboard'})


class htmlView(View):

    def get(self, request, tagname):

        # Teacher List
        if tagname in ["teachers"]:
            last_name = request.GET.get("last_name")
            subjects_taught = request.GET.get("subjects_taught")
            teachers = Teacher.objects

            if last_name or subjects_taught:
                if subjects_taught:
                    teachers = teachers.filter(subjects_taught__contains=subjects_taught)
                if last_name:
                    teachers = teachers.filter(last_name__contains=last_name)
            else:
                teachers = teachers.all()

            paginator = Paginator(teachers, 5)
            page_number = request.GET.get('page')
            teachers = paginator.get_page(page_number)
            return render(request, 'teacher/list.html', {'teachers': teachers, 'filename': tagname, 'subjects_taught': subjects_taught, 'last_name': last_name})

        # Teacher Upload
        if tagname in ["teacher-upload"]:
            if request.user.is_authenticated:
                if request.session.get('url_redirect'):
                    del request.session['url_redirect']

                return render(request, 'teacher/upload.html', {'filename': tagname})
            else:
                request.session['url_redirect'] = "/teacher-upload"

                return HttpResponseRedirect('/login')
        # Login
        if tagname in ["login"]:
            if request.user.is_authenticated:
                if request.session.get('url_redirect'):
                    return HttpResponseRedirect(request.session.get('url_redirect'))

                return HttpResponseRedirect('/teachers')
            else:
                return render(request, 'login.html', {'filename': tagname})
        if tagname in ["logout"]:
            if request.user.is_authenticated:
                logout(request)
                messages.success(request, "You have successfully logged out")
            return HttpResponseRedirect('/teachers')
        else:
            return render(request, '404.html')

    def post(self, request, tagname):

        # Login Update
        if tagname in ["teacher-upload"]:
            if request.user.is_authenticated:
                error_all = {}
                error_string = str()
                try:
                    # Zip File Getting
                    zip_file = ZipFile(request.FILES['image_details'])

                    # Form Validation
                    form = UploadFileForm(request.POST, request.FILES)
                    if form.is_valid():

                        # CSV Data Fetching
                        csv_file = request.FILES['teachers_details']
                        if not csv_file.name.endswith('.csv'):
                            error = 'File is not CSV type'
                            return HttpResponse(error)
                            # if file is too large, return
                        if csv_file.multiple_chunks():
                            error = "Uploaded file is too big (%.2f MB)." % (csv_file.size / (1000 * 1000),)
                            return HttpResponse(error)
                        file_data = csv_file.read().decode("utf-8")
                        io_string = io.StringIO(file_data)
                        lines = file_data.split("\n")
                        headers = lines[0].lower().strip().replace(" ", "_")
                        array_corrector = headers.split(",")

                        next(io_string)
                        # return HttpResponse(csv.reader(io_string))
                        i = 0

                        for row in csv.reader(io_string):
                            i = i + 1
                            data_dict = {}
                            data_dict[array_corrector[0]] = row[0]
                            data_dict[array_corrector[1]] = row[1]
                            data_dict[array_corrector[2]] = row[2]
                            data_dict[array_corrector[3]] = row[3]
                            data_dict[array_corrector[4]] = row[4]
                            data_dict[array_corrector[5]] = row[5]
                            data_dict[array_corrector[6]] = row[6]
                            list_of_subjects_taught = []
                            subjects_taught = []
                            if data_dict["subjects_taught"]:
                                subjects_taught = data_dict["subjects_taught"].split(",")

                            # Unique Subjects
                            for single_entry in subjects_taught:
                                single_entry = single_entry.strip()
                                if single_entry not in list_of_subjects_taught:
                                    list_of_subjects_taught.append(single_entry)

                            subjects_taught_total = len(list_of_subjects_taught)
                            data_dict["subjects_taught"] = ', '.join(list_of_subjects_taught)
                            form = TeacherForm(data_dict)
                            try:
                                if form.is_valid():

                                    # Validate  Subjects greater than 5
                                    if subjects_taught_total > 5:
                                        error_string = error_string + ' <br> Row- ' + str(
                                            i) + ' No More than 5 Subjects'
                                        continue
                                    # getting Suitable profile picture for the teacher
                                    if len(data_dict['profile_picture']) >= 3:
                                        name = data_dict['profile_picture']
                                        try:
                                            data = zip_file.read(data_dict['profile_picture'])
                                            from PIL import Image
                                            image = Image.open(BytesIO(data))
                                            image.load()
                                            image = Image.open(BytesIO(data))
                                            image.verify()
                                            name = os.path.split(name)[1]

                                            # You now have an image which you can save
                                            path = os.path.join(settings.MEDIA_ROOT, "app/static/storage/profile",
                                                                name)

                                            saved_path = default_storage.save(path, ContentFile(data))
                                            data_dict["profile_path"] = saved_path

                                        except ImportError as e:
                                            error_all[str(i)] = form.errors.as_json()
                                            error_string = error_string + ' <br> Row- ' + str(i) + ' Image Not Exist'
                                            pass
                                        except Exception as e:
                                            error_all[str(i)] = form.errors.as_json()
                                            error_string = error_string + ' <br> Row- ' + str(i) + ' Image Not Exist'

                                        form = TeacherForm(data_dict)
                                        try:
                                            if form.is_valid():
                                                print("true")
                                            else:
                                                error_all[str(i)] = form.errors.as_json()
                                                error_string = error_string + ' <br> Row- ' + str(i) + ' ' + ' '.join(
                                                    [' '.join(x for x in l) for l in list(form.errors.values())])

                                                continue

                                        except Exception as e:

                                            error_all[str(i)] = form.errors.as_json()
                                            error_string = error_string + ' <br> Row- ' + str(i) + 'Please Check data'
                                            continue
                                # form Save
                                    form.save()
                                else:

                                    if subjects_taught_total > 5:
                                        error_string = error_string + ' <br> Row- ' + str(
                                            i) + ' No More than 5 Subjects'

                                    error_string = error_string + ' <br> Row- ' + str(i) + ' ' + ' '.join(
                                        [' '.join(x for x in l) for l in list(form.errors.values())])
                            except Exception as e:
                                error_string = error_string + ' <br> Row- ' + str(i) + 'Please Check the data'
                                pass
                    else:
                        messages.add_message(request, messages.ERROR, "Unable to upload file")
                        return HttpResponseRedirect("/teacher-upload")

                except Exception as e:
                    messages.add_message(request, messages.ERROR, "Unable to upload file.")
                    return HttpResponseRedirect("/teacher-upload")

                if len(error_string.strip()) >= 1:
                    messages.add_message(request, messages.WARNING, error_string)

                    return HttpResponseRedirect("/teacher-upload")
                else:
                    messages.add_message(request, messages.SUCCESS, 'Uploaded Successfully !!')
                    return HttpResponseRedirect("/teachers")
            else:
                return HttpResponseRedirect('/login')

        # Login Update
        if tagname == "login":
            if request.user.is_authenticated:
                return HttpResponseRedirect('/teacher-upload')
            else:
                username = request.POST.get("username")
                password = request.POST.get("password")
                try:
                    if "@" in username:
                        user = User.objects.get(email=username)
                    else:
                        user = User.objects.get(username=username)
                    user = authenticate(request, username=user.username, password=password)
                    if user is not None:
                        login(request, user)
                        messages.success(request, "You have successfully logged in")
                        if request.session.get('url_redirect'):
                            return HttpResponseRedirect(request.session.get('url_redirect'))

                        return HttpResponseRedirect("/teachers")
                    else:
                        messages.add_message(request, messages.ERROR, "Wrong password")
                except ObjectDoesNotExist:
                    messages.add_message(request, messages.ERROR, "User not found")

                return HttpResponseRedirect("/login")

class teacherView(View):

    def get(self, request, id):
        teacher = Teacher.objects.filter(id = id).first()
        return render(request, 'teacher/teacher_view.html', {'teacher': teacher, 'filename': 'teacherview'})

class UploadFileForm(forms.Form):
    teachers_details = forms.FileField()
    image_details = forms.FileField(allow_empty_file=False)
