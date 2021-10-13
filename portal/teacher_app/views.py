from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from .models import Subject, Teacher
from django.contrib.auth.models import User
from django.db.models import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.views.generic.base import TemplateResponseMixin, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.core.files import File

from django import forms
from .forms import TeacherForm, ImportFileForm
from django.contrib import messages
from zipfile import ZipFile
from django.conf import settings
from io import BytesIO
import os
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import io
import csv
import zipfile
from io import TextIOWrapper


class DashboardView(View):
    model = Teacher
    template_name = 'dashboard.html'

    def get(self, request):
        teachers = self.model.objects.all()
        return render(request, self.template_name, {'teachers': teachers, 'filename': 'dashboard'})


class TeachersView(ListView):
    paginate_by = 2
    model = Teacher
    template_name = 'teacher/teachers_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        array_last_name = []
        array_subjects_thought = []
        all_teachers = self.model.objects.values_list('last_name', flat=True).exclude(
            last_name='').filter(last_name__isnull=False).order_by('last_name').distinct()
        all_subjects = Subject.objects.values_list('display_name', flat=True).filter(
            display_name__isnull=False).exclude(display_name='').order_by('display_name').distinct()
        for teacher in all_teachers:
            letter_first = teacher.strip().upper()[0]
            if letter_first not in array_last_name:
                array_last_name.append(letter_first)
        for subject in all_subjects:
            letter_first = subject.strip()
            if letter_first not in array_subjects_thought:
                array_subjects_thought.append(letter_first)
        context['array_last_name'] = array_last_name
        context['filename'] = 'teachers'
        context['array_subjects_thought'] = array_subjects_thought
        return context

    def get_queryset(self):
        teachers = self.model.objects.all()
        last_name = self.request.GET.get("last_name")
        subjects_taught = self.request.GET.get("subjects_taught")
        if last_name or subjects_taught:
            if subjects_taught:
                teachers = teachers.filter(subjects__display_name__contains=subjects_taught)
            if last_name:
                teachers = teachers.filter(last_name__istartswith=last_name)
        return teachers


class TeacherProfileView(DetailView):
    model = Teacher


class UploadTeachersView(LoginRequiredMixin, TemplateResponseMixin, View):
    template_name = 'teacher/teacher_upload.html'

    def get(self, request):
        form = ImportFileForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        zippath = settings.MEDIA_ROOT.joinpath('tmp').joinpath('teachers.zip')
        form = ImportFileForm(request.POST, request.FILES)
        if form.is_valid():
            images = request.FILES['images']
            with open(zippath, 'wb+') as destination:
                for chunk in images.chunks():
                    destination.write(chunk)

            names = request.FILES['names']
            archive = zipfile.ZipFile(zippath, 'r')
            data_bytes = TextIOWrapper(request.FILES['names'].file,
                                       encoding='utf-8')
            data_reader = csv.DictReader(data_bytes)
        try:
            for row in data_reader:

                if row['First Name'].strip() == '' or row['Email Address'].strip() == '':
                    raise Exception('First Name / Email cant be blank')
                teacher = Teacher()
                teacher.first_name = row['First Name'].strip()
                teacher.last_name = row['Last Name'].strip()
                teacher.email = row['Email Address'].strip()
                teacher.phone = row['Phone Number'].strip()
                teacher.room_no = row['Room Number'].strip()
                teacher.save()
                subjects = row['Subjects taught'].split(',')
                if row['Profile picture'] in archive.namelist():
                    image = archive.open(row['Profile picture'], 'r')
                    df = File(image)
                    teacher.profile_picture.save(row['Profile picture'], df, save=True)
                for subj in subjects:
                    if subj != '':
                        subject, _ = Subject.objects.get_or_create(name=subj.strip().upper())
                        if teacher.subjects.count() < 5:
                            teacher.subjects.add(subject)
            messages.success(request, 'Data inserted successfully')
        except Exception as e:
            messages.info(request, e)
        finally:
            # 634657778
            os.remove(zippath)
        return render(request, self.template_name, {'form': form})


class ErrorView(View):

    def get(self, request, tagname):

        return render(request, '404.html')

    def post(self, request, tagname):

        # Login Update
        if tagname in ["portal-upload"]:
            if request.user.is_authenticated:
                error_all = {}
                error_string = str()
                try:
                    # Zip File Getting
                    zip_file = ZipFile(request.FILES['image_details'])

                    # Form Validation
                    form = ImportFileForm(request.POST, request.FILES)
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
                                    # getting Suitable profile picture for the portal
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
                                            path = os.path.join(settings.MEDIA_ROOT,
                                                                "teacherapp/static/storage/profile",
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
                        return HttpResponseRedirect("/portal-upload")

                except Exception as e:
                    messages.add_message(request, messages.ERROR, "Unable to upload file.")
                    return HttpResponseRedirect("/portal-upload")

                if len(error_string.strip()) >= 1:
                    messages.add_message(request, messages.WARNING, error_string)

                    return HttpResponseRedirect("/portal-upload")
                else:
                    messages.add_message(request, messages.SUCCESS, 'Uploaded Successfully !!')
                    return HttpResponseRedirect("/teachers")
            else:
                return HttpResponseRedirect('/login')

        # Login Update
        if tagname == "login":
            if request.user.is_authenticated:
                return HttpResponseRedirect('/portal-upload')
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
