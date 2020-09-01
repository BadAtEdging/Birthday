from datetime import *
def time_str(delta):
    def f(a,b,name_a,name_b):
        answer = ''
        if a > 0:
            answer += f'{a} {name_a}'
        if a > 1:
            answer += 's'
        if answer and b != 0:
            answer += ' '
        if b > 0:
            answer += f'{b} {name_b}'
        if b > 1:
            answer += 's'
        return answer
    def dh(a,b):
        return f(a,b,'day','hour')
    def hm(a,b):
        return f(a,b,'hour','minute')
    def ms(a,b):
        return f(a,b,'minute','second')
    def easy(h,m,s):
        return f"{h:02}:{m:02}:{s:02}"
    s = delta.total_seconds()
    s = int(s)
    d = s//86400
    s %= 86400
    h = s//3600
    s %= 3600
    m = s//60
    s %= 60
    ans = ''
    if d:
        ans += f"{d} day"
        if d > 1:
            ans += 's'
        ans += ' '
    ans += easy(h,m,s)
    return ans
    # if h:
        # return hm(h,m)
    # if m or s:
        # return ms(m,s)
    # return '0 seconds'
def time_until(utc_timestamp):
    return time_str(utc_timestamp-datetime.utcnow())
if __name__ == '__main__':
    print(time_str(timedelta(days=1,hours=5,seconds=12931)))
    print(time_str(timedelta(hours=0)))
    print(time_until(datetime.utcnow()+timedelta(hours=5)))
