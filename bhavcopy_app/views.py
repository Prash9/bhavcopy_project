from django.shortcuts import render
from rest_framework.decorators import api_view
from django.http import JsonResponse
import bleach
import pandas as pd

from .equity import Equity
# Create your views here.

@api_view(['GET'])
def display_bhavcopy(request):
    render_page=bleach.clean(request.query_params.get("render","1"))
    filter_by=bleach.clean(request.query_params.get("filter",""))
    download=bleach.clean(request.query_params.get("download","0"))
    # print(render_page,filter_by)
    eq=Equity()
    # eq.update_bhavcopy()
    body,bhavcopy_date=eq.get_bhavcopy(filter_by=filter_by)
    data = {
        "headers": eq.headers,
        "body": body,
        "bhavcopy_date":bhavcopy_date
    }
    if render_page=="1":
        return render(request,"table.html",data)
    if download=="1":
        return eq.download_file(data["body"],data["bhavcopy_date"])

    return JsonResponse(data)
