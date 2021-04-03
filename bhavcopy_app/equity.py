import os,zipfile
from datetime import datetime
import pandas as pd
import redis
import requests
from django.conf import settings
from django.http import HttpResponse

rd = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT,decode_responses=True)


class Equity():
    headers=["SC_CODE","SC_NAME",\
            "OPEN",	"HIGH",	"LOW","CLOSE","LAST",\
            "PREVCLOSE","NO_TRADES","NO_OF_SHRS","NET_TURNOV"]    
    
    def __repr__(self):
        return f"Equity()"
    def _read_file(self,file_name):
        df=pd.read_csv(os.path.join(settings.STATIC_ROOT, file_name),
                    usecols=Equity.headers)
        return df 

    def _save_data_to_redis(self,data):
        rd.flushall()
        with rd.pipeline() as pipe:
            pipe.multi()
            for index ,row in data.iterrows():
                row=dict(row)
                pipe.hset(row['SC_NAME'].strip(), mapping=row)
                if (index+1) % 1000 == 0:
                    pipe.execute()
                    pipe.multi()
            pipe.execute()
    
    def _fetch_bhavcopy_from_source(self):
        filename=f"EQ{datetime.now().strftime('%d%m%y')}_CSV.ZIP"
        # filename="EQ010421_CSV.ZIP"
        url = f"https://www.bseindia.com/download/BhavCopy/Equity/{filename}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36'
            }
        try:
            response = requests.get(url,headers=headers)
            path=os.path.join(settings.STATIC_ROOT,filename)
            if response.status_code==200:
                with open(path,"wb") as f:
                    f.write(response.content)
                with zipfile.ZipFile(path, 'r') as f:
                    f.extractall(settings.STATIC_ROOT)
                return filename.split(".")[0].replace("_",".")
        except Exception as e:
            print(e)
        finally:
            if os.path.exists(path):
                os.remove(path)
        return ""
    
    def update_bhavcopy(self):
        filename=self._fetch_bhavcopy_from_source()
        if filename:
            data=self._read_file(filename)
            self._save_data_to_redis(data)
            os.remove(os.path.join(settings.STATIC_ROOT,filename))
            print("UPDATED NEW FILE")

    def get_bhavcopy(self,filter_by=""):
        filter_by = f"*{filter_by.upper()}*" if filter_by else None
        matched_keys=[]
        # print(filter_by)
        for record in rd.scan_iter(match=filter_by, count=50, _type="HASH"):
            matched_keys.append(record)
        output=[]
        # print(matched_keys)
        with rd.pipeline() as pipe:
            pipe.multi()
            for index ,key in enumerate(matched_keys):
                pipe.hgetall(key)
                if (index+1) % 1000 == 0:
                    output.extend(pipe.execute())
                    pipe.multi()
            output.extend(pipe.execute())
        return output
    
    def download_file(self,data):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="bhavcopy_equity.csv"'
        pd.DataFrame(data).to_csv(path_or_buf=response,index=False)
        return response