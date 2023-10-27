from datetime import date, datetime, timedelta

def null_test(ttstr: str):
    if ttstr is None or ttstr == "":
        print("is None", ttstr)
    else:
        print("else", ttstr)

def less_than(datastr: str) -> bool:
    if datastr < "20231017":
        return True
    else:
        return False

def debug_check(check: str = "true") -> bool:
    if check is None or check.lower() == "" or check.lower() != "true":
        return False
    else:
        return True
def date_test():
    data_str = date.today()
    print(data_str)
    lastday = datetime.now() + timedelta(days=-2)

    date_str = datetime.today().strftime("%Y%m%d")
    print(date_str)
    print(lastday.strftime("%Y%m%d"))

    curdate = datetime.strptime("20231011", "%Y%m%d")
    print(curdate)

def date_add(datestr:str, days: int) -> datetime:
    r = datetime.strptime(datestr, "%Y%m%d") + timedelta(days=days)
    print("r = ", r)
    return r
def check_last_data(last_date: str, cur_date: str, days: int):
    print("last_date = ", last_date)
    print("expected = ", date_add(cur_date, days).strftime("%Y%m%d"))
    if last_date < date_add(cur_date, days).strftime("%Y%m%d"):
        print("cur_date = {}, last_date = {}. expected last_date = {} ".format(cur_date, last_date, date_add(cur_date, days).strftime("%Y%m%d")))

def str_join(column_name: list):
    print("----------------------")
    df = [[12]]
    min_row = min(len(df), 5)
    print("min_row", min_row)
    for i in range(min_row):
        projection = []
        for j in range(len(column_name)):
            projection.append(df[i][j])
        print(projection)


if __name__ == "__main__":
    #str_join(["col1"])
    date_test()
    #null_test("")
    print(less_than("20231021"))
    #date_add("20231020", -2)
    #date_add("20231020", -4)
    #date_add("20231016", -40)
    check_last_data("202309", "20231016", -60)
    print("debug_check: ", debug_check(check=None))
    print("debug_check: '' ", debug_check(""))
    print("debug_check: True ", debug_check("True"))
    r = debug_check("f")
    if not r:
        print("r = ", r)
    else:
        print("r is false")
    print("debug_check: true ", debug_check("true"))
    r = debug_check("true")
    if not r:
        print("false")
    else:
        print("true")
    print("debug_check: false ", debug_check("false"))
    print("debug_check: aa ", debug_check("aa"))


