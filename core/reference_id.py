# from tax.models import DemandNotice
from datetime import date


def generate_ref_id():
    today = date.today()
    year = str(today.year)[-2:]
    month = str(today.month).zfill(2)
    
    if DemandNotice.objects.all().exists(): 
        last = str(DemandNotice.objects.all().last())
    else:
        last = 0
    referenceid = "LA"+year+month + str(int(last) + 1).zfill(8)
    return referenceid