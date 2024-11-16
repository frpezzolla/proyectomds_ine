import timeit
import pandas as pd
if __name__ == "__main__":
    # ti = timeit.default_timer()
    # sss = pd.Series(list(range(100)))
    # print(timeit.default_timer()-ti)

    # ti = timeit.default_timer()
    # print(sss.count())    
    # print(timeit.default_timer()-ti)

    # ti = timeit.default_timer()
    # print(len(sss))
    # print(timeit.default_timer()-ti)
    # pass
    # print(list(range(10,0,-6)))

    dates = sorted([pd.Timestamp(1999+y, 1, 1) for y in range(10,0,-1)])

    print([date.date().isoformat() for date in dates])