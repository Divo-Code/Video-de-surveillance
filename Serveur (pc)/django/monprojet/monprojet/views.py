from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required

@staff_member_required(login_url='/admin/')
def home(request):
    return render(request, "monprojet/index.html")