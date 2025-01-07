import os
import mysql.connector

def get_db():
    mydb = mysql.connector.connect(
      host=os.environ['DB_HOST'],
      user=os.environ['DB_USER'],
      password=os.environ['DB_PASS'],
      database="rental_app_db"
    )

    return mydb

def add_id(user_id, filename):
    print(user_id)
    print(filename)
    db = get_db()
    curs = db.cursor()
    curs.execute(
        "UPDATE `renter` SET license = %s WHERE id2 = %s;", (filename, user_id)
    )
    db.commit()
    curs.close()
    db.close()
    return True


def add_square_id(user_id, square_id):
    db = get_db()
    curs = db.cursor()
    curs.execute(
        "UPDATE `renter` SET squareid = %s WHERE id2 = %s;", (square_id, user_id)
    )
    db.commit()
    curs.close()
    db.close()
    return True


def del_square_id(user_id):
    db = get_db()
    curs = db.cursor()
    curs.execute(
        "UPDATE `renter` SET squareid = NULL WHERE id2 = %s and id2 != %s;", (user_id, 'None')
    )
    db.commit()
    curs.close()
    db.close()
    return True


def set_complete_renter(user_id):
    db = get_db()
    curs = db.cursor()
    curs.execute(
        "UPDATE `renter` SET completed = 1 WHERE id2 = %s and id2 != %s;", (user_id, "None")
    )
    db.commit()
    curs.close()
    db.close()
    return True


def get_res_info(res_id):
    db = get_db()
    curs = db.cursor()
    curs.execute(
        "SELECT * FROM reservations WHERE id = %s and id != %s", (res_id, 'None')
    )

    res = curs.fetchone()
    curs.close()
    db.close()

    if not res:
        return None

    res = {
        'res_id':res[0], 'renter_id':res[1], 'equipment':res[2], 'start':res[3], 'end':res[4], 'n_days':res[5],
        'n_weeks':res[6], 'n_months':res[7], 'transport':res[8], 'renter_name':res[9], 'company':res[10], 'phone':res[11],
        'invoice_email':res[12], 'job_desc':res[13], 'exp_level':res[14], 'address1':res[15], 'address2':res[16], 'city':res[17],
        'state':res[18], 'zip':res[19], 'commerical_prop':res[20], 'note':res[21], 'event_id':res[22], 'era_signed_date':res[23],
        'era_signed_name':res[24], 'status':res[25], 'deposit_source_id':res[26], 'deposit_idempotency':res[27]
    }
    return res


def last_booking_id():
    db = get_db()
    curs = db.cursor()
    curs.execute(
        "SELECT last_insert_id() 'reservations';"
    )
    last_id = curs.fetchone()
    curs.close()
    db.close()

    return last_id[0] + 1


def last_event_id():
    db = get_db()
    curs = db.cursor()
    curs.execute(
        "select last_insert_id() 'events';"
    )
    last_id = curs.fetchone()
    curs.close()
    db.close()

    return last_id[0] + 1


def all_renter_profiles():
    db = get_db()
    curs = db.cursor()
    curs.execute(
        "SELECT * FROM renter"
    )

    ress = None
    ress = curs.fetchall()
    curs.close()
    db.close()

    new_ress = []

    if not ress:
        return new_ress

    for profile in ress:
        profile_dict = {
            "id": profile[0],
            "fname": profile[1],
            "lname": profile[2],
            "phone": profile[3],
            "email": profile[4],
            "contractor": profile[5] + 1,
            "license": profile[6],
            "insurance": profile[7],
            "completed": profile[8],
            "squareid": profile[9],
        }
        new_ress.append(profile_dict)

    return new_ress


def get_renter_profile(user_id, blanks=False):
    db = get_db()
    curs = db.cursor()
    curs.execute(
        "SELECT * FROM renter WHERE id2 = %s and id2 != %s", (user_id,'None')
    )

    profile = curs.fetchone()
    curs.close()
    db.close()

    if not profile:
        if blanks == True:
            profile_dict = {
                "id": "",
                "fname": "",
                "lname": "",
                "phone": "",
                "email": "",
                "contractor": "",
                "license": "",
                "insurance": "",
                "completed": "",
                "squareid": ""
            }
            return profile_dict
        return None

    profile_dict = {
        "id": profile[0],
        "fname": profile[1],
        "lname": profile[2],
        "phone": profile[3],
        "email": profile[4],
        "contractor": profile[5] + 1,
        "license": profile[6],
        "insurance": profile[7],
        "completed": profile[8],
        "squareid": profile[9],
    }
    return profile_dict


def add_esign(res_id, name, date):
    db = get_db()
    curs = db.cursor()
    curs.execute(
        "UPDATE `reservations` SET era_signed_date = %s, era_signed_name = %s WHERE id = %s;", (date, name, res_id)
    )
    db.commit()
    curs.close()
    db.close()


def approve_reservation(res_id):
    db = get_db()
    curs = db.cursor()
    curs.execute(
        "UPDATE `reservations` SET status = %s WHERE id = %s;", (1, res_id)
    )
    db.commit()
    curs.close()
    db.close()
    return True


def deny_reservation(res_id):
    db = get_db()
    curs = db.cursor()
    curs.execute(
        "UPDATE `reservations` SET status = %s WHERE id = %s;", (-1, res_id)
    )
    db.commit()
    curs.close()
    db.close()
    return True


def add_dep_source(res_id, source_id):
    db = get_db()
    curs = db.cursor()
    curs.execute(
        "UPDATE `reservations` SET deposit_source_id = %s WHERE id = %s;", (source_id, res_id)
    )
    db.commit()
    curs.close()
    db.close()
    return True


def hide_cal_event(event_id):
    db = get_db()
    curs = db.cursor()
    curs.execute(
        "UPDATE `events` SET bg = %s WHERE id = %s;", ('', int(event_id))
    )
    db.commit()
    curs.close()
    db.close()
    return True


def show_cal_event(event_id):
    db = get_db()
    curs = db.cursor()
    curs.execute(
        "UPDATE `events` SET bg='#FF5656' WHERE id = %s and id != %s;", (int(event_id), 'None')
    )
    db.commit()
    curs.close()
    db.close()
    return True


def add_dep_ide(res_id, ide):
    db = get_db()
    curs = db.cursor()
    curs.execute(
        "UPDATE `reservations` SET deposit_idempotency = %s WHERE id = %s;", (ide, res_id)
    )
    db.commit()
    curs.close()
    db.close()
    return True


def add_renter_profile(id_, fname, lname, phone, email, contractor, license, completed):
    db = get_db()
    curs = db.cursor()
    curs.execute(
        "INSERT INTO renter (id2, fname, lname, phone, email, contractor, license, insurance, completed, squareid) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
        (id_, fname, lname, phone, email, contractor, license, None, completed, None),
    )
    db.commit()
    curs.close()
    db.close()


def create_booking(event_id, renter_id, equipment, start, end, n_days, n_weeks,n_months,transport,renter_name,company,phone,invoice_email,job_desc, exp_level, address1,address2,city,state,zip,commerical_prop,text):
    db = get_db()
    curs = db.cursor()
    curs.execute(
        "INSERT INTO reservations (renter_id, equipment, start, end, n_days, n_weeks,n_months,transport,renter_name,company,phone,invoice_email,job_desc, exp_level, address1,address2,city,state,zip,commerical_prop,note,event_id, era_signed_date, era_signed_name, status, deposit_source_id, deposit_idempotency) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s , %s , %s, %s, %s)",
        (renter_id, equipment, start, end, n_days, n_weeks,n_months,transport,renter_name,company,phone,invoice_email,job_desc,exp_level, address1,address2,city,state,zip,commerical_prop,text,event_id, None, None, 0, None, None),
    )
    db.commit()
    curs.close()
    db.close()
