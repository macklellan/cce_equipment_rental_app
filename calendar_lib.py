# (A) LOAD SQLITE MODULE
from db_lib import get_db

from calendar import monthrange

# (B) SAVE EVENT
def save (start, end, txt, color, bg, eq, id=None):
  # (B1) CONNECT
  db = get_db()
  cursor = db.cursor()

  # (B2) DATA & SQL
  data = (start, end, txt, color, bg, eq)
  if id is None:
    sql = "INSERT INTO `events` (`start`, `end`, `text`, `color`, `bg`, `eq`) VALUES (%s,%s,%s,%s,%s,%s)"
  else:
    sql = "UPDATE `events` SET `start`=%s, `end`=%s, `text`=%s, `color`=%s, `bg`=%s, `eq`=%s WHERE `id`=%s"
    data = data + (id,)

  # (B3) EXECUTE
  cursor.execute(sql, data)
  db.commit()
  db.close()
  return True

# (C) DELETE EVENT
def delete(id):
  # (C1) CONNECT
  conn = sqlite3.connect(DBFILE)
  cursor = conn.cursor()

  # (C2) EXECUTE
  cursor.execute("DELETE FROM `events` WHERE `id`=%s", (id,))
  conn.commit()
  conn.close()
  return True

# (D) GET EVENTS
def get(month, year, eq):
  # (D1) CONNECT
  db = get_db()
  cursor = db.cursor()

  # (D2) DATE RANGE CALCULATIONS
  daysInMonth = str(monthrange(year, month)[1])
  month = month if month>=10 else "0" + str(month)
  dateYM = str(year) + "-" + str(month) + "-"
  start = dateYM + "01 00:00:00"
  end = dateYM + daysInMonth + " 23:59:59"

  # (D3) GET EVENTS
  cursor.execute(
    "SELECT * FROM `events` WHERE ((`start` BETWEEN %s AND %s) OR (`end` BETWEEN %s AND %s) OR (`start` <= %s AND `end` >= %s))",
    (start, end, start, end, start, end)
  )
  rows = cursor.fetchall()
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
