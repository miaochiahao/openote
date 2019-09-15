import json

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.template import loader
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from .data.black_list import black_list
from .models import HTTPLog, DNSLog, FileService


# Create your views here.


def login_view(request):
    template = loader.get_template("login.html")

    if request.method == "GET":
        context = {

        }

    elif request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse('http'))
        else:
            context = {
                'msg': "用户名或密码错误"
            }
    return HttpResponse(template.render(context, request))


@login_required()
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse('login'))


@login_required()
def index_view(request):
    return HttpResponseRedirect(reverse('http'))


@login_required()
def http_view(request):
    template = loader.get_template("http_log.html")
    all_logs = HTTPLog.objects.all().order_by("-time")
    paginator = Paginator(all_logs, 10)
    page = request.GET.get("page", "1")
    try:
        ten_logs = paginator.page(page)
    except PageNotAnInteger:
        ten_logs = paginator.page(1)
    except EmptyPage:
        ten_logs = paginator.page(paginator.num_pages)

    results = []
    for l in ten_logs.object_list:
        t = {
            "host": l.host,
            "method": l.method,
            "time": l.time,
            "source": l.source,
            "log_id": l.id,
        }
        results.append(t)

    context = {
        "results": results,
        "ten_logs": ten_logs,
    }

    return HttpResponse(template.render(context, request))


@login_required()
def delete_http_record(request):
    HTTPLog.objects.all().delete()
    return HttpResponse("success")


@login_required()
def delete_dns_record(request):
    DNSLog.objects.all().delete()
    return HttpResponse("success")


@login_required()
def dns_view(request):
    template = loader.get_template("dns_log.html")
    all_logs = DNSLog.objects.all().order_by("-time")
    paginator = Paginator(all_logs, 10)
    page = request.GET.get("page", "1")
    try:
        ten_logs = paginator.page(page)
    except PageNotAnInteger:
        ten_logs = paginator.page(1)
    except EmptyPage:
        ten_logs = paginator.page(paginator.num_pages)

    results = []
    for l in ten_logs.object_list:
        t = {
            "content": l.content,
            "source": l.source,
            "time": l.time,
        }
        results.append(t)

    context = {
        "results": results,
        "ten_logs": ten_logs,
    }

    return HttpResponse(template.render(context, request))


@login_required()
def xss_view(request):
    template = loader.get_template("xss.html")
    context = {

    }
    return HttpResponse(template.render(context, request))


@login_required()
def file_service_view(request):
    template = loader.get_template("file_service.html")
    all_logs = FileService.objects.all().order_by("-time")
    paginator = Paginator(all_logs, 10)
    page = request.GET.get("page", "1")
    try:
        ten_logs = paginator.page(page)
    except PageNotAnInteger:
        ten_logs = paginator.page(1)
    except EmptyPage:
        ten_logs = paginator.page(paginator.num_pages)

    results = []
    for l in ten_logs.object_list:
        t = {
            "name": l.name,
            "content": l.content,
            "source": l.id,
            "time": l.time,
        }
        results.append(t)

    context = {
        "results": results,
        "ten_logs": ten_logs,
    }

    return HttpResponse(template.render(context, request))


@login_required()
def add_file_service(request):
    template = loader.get_template("add_file_service.html")

    context = {

    }
    return HttpResponse(template.render(context, request))


def return_file(request, file_uri):

    return HttpResponse(file_uri)


@login_required()
def manage_file_templates(request):
    template = loader.get_template("manage_file_templates.html")

    context = {

    }
    return HttpResponse(template.render(context, request))

# 此处禁用csrf_token 保证POST请求顺利
# TODO: black_list
@csrf_exempt
def handle_http_request(request):
    if request.get_full_path() in black_list:
        return HttpResponse("nope")

    header = {}
    for k in request.headers.keys():
        v = request.headers.get(k)
        header[k] = v
    header = json.dumps(header)
    method = request.method
    host = request.get_full_path()
    source = request.META['REMOTE_ADDR']
    body = request.body
    log = HTTPLog(method=method, header=header, body=body, host=host, source=source)
    log.save()

    return HttpResponse("ok")


@login_required()
def http_details(request, log_id):
    log = get_object_or_404(HTTPLog, id=log_id)

    header = json.loads(log.header)
    body = log.body
    method = log.method
    host = log.host
    source = log.source
    time = log.time

    context = {
        "log_id": log_id,
        "method": method,
        "host": host,
        "header": header,
        "body": body,
        "source": source,
        "time": time
    }
    template = loader.get_template("http_single_record.html")
    return HttpResponse(template.render(context, request))


@login_required()
def download_http_body(request, log_id):
    log = get_object_or_404(HTTPLog, id=log_id)
    body = log.body
    print(type(body))
    response = HttpResponse(body, content_type="application/octet-stream")
    response['Content-Disposition'] = "inline; filename=log_body_{}".format(log_id)
    return response
