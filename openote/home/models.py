from django.db import models


# Create your models here.


class HTTPLog(models.Model):
    time = models.DateTimeField(auto_now_add=True)
    method = models.CharField(max_length=16)
    header = models.TextField(default="{}")
    body = models.BinaryField(default="")  # 使用二进制形式存放 能兼容文本数据和二进制数据
    host = models.TextField(default="")
    source = models.CharField(max_length=64)


class DNSLog(models.Model):
    time = models.DateTimeField(auto_now_add=True)
    content = models.CharField(max_length=128)
    source = models.CharField(max_length=64)


class FileService(models.Model):
    time = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=64)
    headers = models.TextField(default="")
    is_binary = models.BooleanField(default=False)
    content = models.TextField(default="")


class XSSProject(models.Model):
    id = models.AutoField(primary_key=True)
    project_name = models.CharField(max_length=64)


class XSSRecord(models.Model):
    time = models.DateTimeField(auto_now_add=True)
