from dateutil.parser import parse
import datetime

if __name__ == "__main__":
    date_orig = "1996-09-24T01:59:03.000Z"
    date_orig_parsed = parse(date_orig)
    gmt = date_orig_parsed + datetime.timedelta(weeks=int("1024"))
    gmt_offset = gmt + datetime.timedelta(hours=int("-5"))
    print(str(gmt_offset))