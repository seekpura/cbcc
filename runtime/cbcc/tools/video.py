def timing(segments,target_seconds):
    total=sum(float(x.get('seconds',0)) for x in segments)
    return {'total_seconds':round(total,3),'target_seconds':target_seconds,'delta':round(total-float(target_seconds),3),'pass':total<=float(target_seconds)}
