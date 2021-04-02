from django.shortcuts import render
from rest_framework.decorators import api_view
from django.http import JsonResponse

# Create your views here.

@api_view(['GET'])
def display_bhavcopy(request):
    render_page=request.query_params.get("render","1")
    filter_data=request.query_params.get("filter","")
    print(render_page,filter_data)
    body=[
            {"EquityID":"1231231","EquityName":"asdasd","High":"23.23","Low":"234.234","Open":23424,"Close":345} for i in range(100) 
    ]
    data = {
        "headers": ["EquityID","EquityName","High","Low","Open","Close"],
        "body": body,
    }
    if render_page=="1":
        return render(request,"table.html",data)
    body=[
        {"EquityID":"1231231","EquityName":"asdasd","High":"23.23","Low":"234.234","Open":23424,"Close":345} for i in range(20) 
    ]
    data = {
        "headers": ["EquityID","EquityName","High","Low","Open","Close"],
        "body": body,
    }
    return JsonResponse(data)

@api_view(['GET'])
def get_equity_data(request):
    
    return JsonResponse(data)

@api_view(['POST'])
def download_bhavcopy(request):
    return render(request,"index.html")

