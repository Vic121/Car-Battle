import datetime
import time


def reveal_league_name(ln):
    """
    Zamienia nazwe ligi na ID (na sztywno)
    """
    if ln == "premiership" or ln == "angielska" or ln == "english":
        return 1
    elif ln == "ligue-1" or ln == "francuska" or ln == "french":
        return 5
    elif ln == "primera-division" or ln == "hiszpanska" or ln == "spanish":
        return 4
    elif ln == "bundesliga" or ln == "niemiecka" or ln == "german":
        return 6
    elif ln == "orange-ekstraklasa" or ln == "polska" or ln == "polish":
        return 8
    elif ln == "serie-a" or ln == "wloska" or ln == "italian":
        return 3
    elif ln == "liga-mistrzow" or ln == "champions-league":
        return 9
    elif ln == "liga-kibicow" or ln == "supporters-league":
        return 10
    elif ln == "euro-2008":
        return 11
    elif ln == "puchar-uefa" or ln == "uefa-cup":
        return 12
    else:
        return 0


def reveal_country_name(cn):
    """
    Zamienia nazwe kraju na ID (na sztywno)
    """
    if cn == "anglia" or cn == "england" or cn == "united-kingdom":
        return 177
    elif cn == "francja" or cn == "france":
        return 66
    elif cn == "hiszpania" or cn == "spain":
        return 155
    elif cn == "niemcy" or cn == "germany":
        return 65
    elif cn == "polska" or cn == "poland":
        return 1
    elif cn == "wlochy" or cn == "italy":
        return 83
    elif cn == "holandia" or cn == "netherlands":
        return 117
    else:
        return 0


def reveal_status_name(sn):
    """
    Zamienia pelna nazwe statusu na skrot (na sztywno)

    ('o', 'Open'),
    ('d', 'During'),
    ('f', 'Finished'),
    ('l', 'Cancelled'),
    ('p', 'Postponed'),
    """

    if sn == "trwajace" or sn == "started":
        return "d"
    elif sn == "nadchodzace" or sn == "upcoming":
        return "o"
    elif sn == "zakonczone" or sn == "finished":
        return "f"
    elif sn == "nie-rozegrane" or sn == "postponed":
        return "p"
    else:
        return 0


def reveal_month_name(mn):
    if mn == "styczen" or mn == "january":
        return 2008, 1
    elif mn == "luty" or mn == "february":
        return 2008, 2
    elif mn == "marzec" or mn == "march":
        return 2008, 3
    elif mn == "kwiecien" or mn == "april":
        return 2008, 4
    elif mn == "maj" or mn == "may":
        return 2008, 5
    elif mn == "czerwiec" or mn == "june":
        return 2008, 6
    elif mn == "lipiec" or mn == "july":
        return 2007, 7
    elif mn == "sierpien" or mn == "august":
        return 2007, 8
    elif mn == "wrzesien" or mn == "september":
        return 2007, 9
    elif mn == "pazdziernik" or mn == "october":
        return 2007, 10
    elif mn == "listopad" or mn == "november":
        return 2007, 11
    elif mn == "grudzien" or mn == "december":
        return 2007, 12


def mkDateTime(dateString, strFormat="%Y-%m-%d"):
    # Expects "YYYY-MM-DD" string
    # returns a datetime object
    eSeconds = time.mktime(time.strptime(dateString, strFormat))
    return datetime.datetime.fromtimestamp(eSeconds)


def formatDate(dtDateTime, strFormat="%Y-%m-%d"):
    # format a datetime object as YYYY-MM-DD string and return
    return dtDateTime.strftime(strFormat)


def mkFirstOfMonth2(dtDateTime):
    # what is the first day of the current month
    ddays = int(dtDateTime.strftime("%d")) - 1  # days to subtract to get to the 1st
    delta = datetime.timedelta(days=ddays)  # create a delta datetime object
    return dtDateTime - delta  # Subtract delta and return


def mkFirstOfMonth(dtDateTime):
    # what is the first day of the current month
    # format the year and month + 01 for the current datetime, then form it back
    # into a datetime object
    return mkDateTime(formatDate(dtDateTime, "%Y-%m-01"))


def mkLastOfMonth(dtDateTime):
    dYear = dtDateTime.strftime("%Y")  # get the year
    dMonth = str(int(dtDateTime.strftime("%m")) % 12 + 1)  # get next month, watch rollover
    dDay = "1"  # first day of next month
    nextMonth = mkDateTime("%s-%s-%s" % (dYear, dMonth, dDay))  # make a datetime obj for 1st of next month
    delta = datetime.timedelta(seconds=1)  # create a delta of 1 second
    return nextMonth - delta  # subtract from nextMonth and return


def get_months():
    months = (
        (datetime.date(2007, 7, 1)),
        (datetime.date(2007, 8, 1)),
        (datetime.date(2007, 9, 1)),
        (datetime.date(2007, 10, 1)),
        (datetime.date(2007, 11, 1)),
        (datetime.date(2007, 12, 1)),
        (datetime.date(2008, 1, 1)),
        (datetime.date(2008, 2, 1)),
        (datetime.date(2008, 3, 1)),
        (datetime.date(2008, 4, 1)),
        (datetime.date(2008, 5, 1)),
    )

    return months


def get_weeks():
    weeks = []
    start = datetime.datetime(2007, 7, 29, 0, 0, 0)
    end = datetime.datetime(2008, 5, 18, 0, 0, 0)

    monday = start
    sunday = start
    while 1:
        if monday > end:
            return weeks

        monday = sunday + datetime.timedelta(days=1)
        sunday = monday + datetime.timedelta(days=6)
        weeks.append((monday, sunday))
