import os,zipfile,traceback,logging
from datetime import datetime
import pandas as pd
import redis
import requests
from django.conf import settings
from django.http import HttpResponse

logger = logging.getLogger(__name__)
try:
    rd = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT,decode_responses=True)
except Exception as e:
    logger.error(traceback.format_exe())

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

    def _save_data_to_redis(self,data,date):
        '''
            Parameters:
                data (Pandas dataframe): Dataframe contains csv data for bhavcopy
                date (datetime object): Date for which the 
                                        bhavcopy is fetched
            Returns: None
        '''
        try:
            rd.flushall()
            rd.set("BHAVCOPY_DATE",date.strftime("%d-%m-%Y"))
            with rd.pipeline() as pipe:
                pipe.multi()
                for index ,row in data.iterrows():
                    row=dict(row)
                    pipe.hset(row['SC_NAME'].strip(), mapping=row)
                    if (index+1) % 1000 == 0:
                        pipe.execute()
                        pipe.multi()
                pipe.execute()
        except Exception as e:
            logger.error(traceback.format_exc())
    
    def _fetch_bhavcopy_from_source(self,date):
        '''
            Parameters:
                date (datetime object): Date for which the 
                                        bhavcopy to be fetch from source
            Returns: 
                filename (str): .csv filename if the file was downloaded
                                from source else empty string is returned
        '''
        try:
            filename=f"EQ{date.strftime('%d%m%y')}_CSV.ZIP"
            # filename="EQ010421_CSV.ZIP"
            url = f"https://www.bseindia.com/download/BhavCopy/Equity/{filename}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36'
                }
            response = requests.get(url,headers=headers)
            path=os.path.join(settings.STATIC_ROOT,filename)
            if response.status_code==200:
                with open(path,"wb") as f:
                    f.write(response.content)
                with zipfile.ZipFile(path, 'r') as f:
                    f.extractall(settings.STATIC_ROOT)
                return filename.split(".")[0].replace("_",".")
        except Exception as e:
            logger.error(traceback.format_exc())
        finally:
            if os.path.exists(path):
                os.remove(path)
        return ""
    
    def update_bhavcopy(self,date):
        '''
            Parameters:
                date (datetime object): Date for which the 
                                        bhavcopy to be fetch from source
            Returns: None
        '''
        filename=self._fetch_bhavcopy_from_source(date)
        if filename:
            data=self._read_file(filename)
            self._save_data_to_redis(data,date)
            os.remove(os.path.join(settings.STATIC_ROOT,filename))
            logger.debug("UPDATED NEW FILE")

    def get_bhavcopy(self,filter_by=""):
        '''
            Parameters:
                filter_by (str): equity name pattern to filter
            Returns:
                ouptut (List[Dict]): Bhavcopy equity data from Redis
                date (str): dd-mm-yyyy formated string

        '''
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
        date=rd.get("BHAVCOPY_DATE") or datetime.now().strftime('%d-%m-%Y')
        return output,date
    
    def download_file(self,data,date):
        '''
            Parameters:
                data (List[Dict]): Data for download
                date (str): dd-mm-yyyy formated string 
            Returns:
                response (httpResponse): Return http response object with
                                        csv attachment type
        '''
        response = HttpResponse(content_type='text/csv')
        filename=f'"bhavcopy_equity_{date}.csv"'
        response['Content-Disposition'] = f"attachment; filename={filename}"
        pd.DataFrame(data).to_csv(path_or_buf=response,index=False)
        return response