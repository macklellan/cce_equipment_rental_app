# (A) LOAD SQLITE MODULE
from db_lib import get_db2

from calendar import monthrange

# (B) SAVE EVENT
def save (start, end, txt, color, bg, eq, id=None):

    # (B2) DATA & SQL
    dict = {"start":start, "end":end, "text":txt, "color":color, "bg":bg, "eq":eq, "id":id}

    if id is None:
        sql = "INSERT INTO events (start, end_, text, color, bg, eq) VALUES (%(start)s, %(end)s, %(text)s, %(color)s, %(bg)s, %(eq)s)"
    else:
        sql = "UPDATE events SET start=%(start)s, end=%(end)s, text=%(text)s, color=%(color)s, bg=%(bg)s, eq=%(eq)s WHERE id=%(id)s"

    db = get_db2();

    db.run(sql, dict)

    return True


# (D) GET EVENTS
def get(month, year, eq):


    # (D2) DATE RANGE CALCULATIONS
    daysInMonth = str(monthrange(year, month)[1])
    month = month if month>=10 else "0" + str(month)
    dateYM = str(year) + "-" + str(month) + "-"
    start = dateYM + "01 00:00:00"
    end = dateYM + daysInMonth + " 23:59:59"

    db = get_db2();

    rows = db.all(
            "SELECT * FROM events WHERE ((start BETWEEN %(start)s AND %(end)s) OR (end_ BETWEEN %(start)s AND %(end)s) OR (start <= %(start)s AND end_ >= %(end)s))",
            {"start":start, "end":end}
    )


    if len(rows)==0:
        return None

    # s & e : start & end date
    # c & b : text & background color
    # t : event text
    data = {}
    for r in rows:
        if str(r[6]) == eq:
            data[r[0]] = {
              "s" : r[1], "e" : r[2],
              "c" : r[4], "b" : r[5],
              "t" : r[3], "e2": r[6]
            }
    return data
