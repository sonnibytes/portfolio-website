from django.shortcuts import render


def project_list(request):
    return render(request, "projects/project_list.html")


def project_detail(request, slug):
    return render(request, "projects/project_detail.html", {"slug": slug})
