import os
import postgres



def get_db2():
    return postgres.Postgres(url=os.environ['POSTGRES_URL'])


def add_id(user_id, filename):

    db = get_db2()

    with db.get_cursor() as curs:
        curs.execute(
            f"UPDATE renters SET license = '{filename}' WHERE id2 = '{user_id}';"
        )

    return True


def add_square_id(user_id, square_id):
    db = get_db2()

    with db.get_cursor() as curs:
        curs.execute(
            f"UPDATE renters SET squareid = '{square_id}' WHERE id2 = '{user_id}';"
        )

    return True


def del_square_id(user_id):
    db = get_db2()

    with db.get_cursor() as curs:
        curs.execute(
            f"UPDATE renters SET squareid = NULL WHERE id2 = '{user_id}';"
        )

    return True


def set_complete_renter(user_id):
    db = get_db2()

    with db.get_cursor() as curs:
        curs.execute(
            f"UPDATE renters SET completed = True WHERE id2 = '{user_id}';"
        )

    return True


def get_res_info(res_id):
    db = get_db2()

    res = None

    with db.get_cursor() as curs:
        curs.execute(
            f"SELECT * FROM reservations WHERE id = '{res_id}' ;"
        )

        res = curs.fetchone()

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
    db = get_db2()

    last_id = None

    with db.get_cursor() as curs:
        curs.execute(
            "SELECT MAX(ID) FROM reservations;"
        )
        last_id = curs.fetchone()

    if not last_id:
        return None
    return last_id[0]


def last_event_id():
    db = get_db2()

    last_id = None

    with db.get_cursor() as curs:
        curs.execute(
            "SELECT MAX(ID) FROM events;"
        )
        last_id = curs.fetchone()

    if not last_id:
        return None
    return last_id[0]


def all_renter_profiles():
    db = get_db2()

    ress = None

    with db.get_cursor() as curs:
        curs.execute(
            "SELECT * FROM renters"
        )
        ress = curs.fetchall()


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
    db = get_db2()

    profile = None
    with db.get_cursor() as curs:
        curs.execute(
            f"SELECT * FROM renters WHERE id2 = '{user_id}' and id2 != 'None';"
        )
        profile = curs.fetchone()


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
    db = get_db2()

    with db.get_cursor() as curs:
        curs.execute(
            f"UPDATE reservations SET era_signed_date = '{date}', era_signed_name = '{name}' WHERE id = '{res_id}';"
        )


def approve_reservation(res_id):
    db = get_db2()

    with db.get_cursor() as curs:
        curs.execute(
            f"UPDATE reservations SET status = 1 WHERE id = '{res_id}';"
        )

    return True

def deny_reservation(res_id):
    db = get_db2()

    with db.get_cursor() as curs:
        curs.execute(
            f"UPDATE reservations SET status = -1 WHERE id = '{res_id}';"
        )

    return True

def update_reservation_status(res_id, status_int):
    db = get_db2()

    with db.get_cursor() as curs:
        curs.execute(
            f"UPDATE reservations SET status = '{status_int}' WHERE id = '{res_id}';"
        )

    return True

def add_dep_source(res_id, source_id):
    db = get_db2()

    with db.get_cursor() as curs:
        curs.execute(
            f"UPDATE reservations SET deposit_source_id = '{source_id}' WHERE id = '{res_id}';"
        )

    return True


def hide_cal_event(event_id):
    db = get_db2()

    with db.get_cursor() as curs:
        curs.execute(
            f"UPDATE events SET bg = ' ' WHERE id = '{int(event_id)}';"
        )

    return True


def show_cal_event(event_id):
    db = get_db2()

    with db.get_cursor() as curs:
        curs.execute(
            f"UPDATE events SET bg='#FF5656' WHERE id = '{int(event_id)}';"
        )

    return True


def add_dep_ide(res_id, ide):
    db = get_db2()

    with db.get_cursor() as curs:
        curs.execute(
            f"UPDATE reservations SET deposit_idempotency = '{ide}' WHERE id = '{res_id}';"
        )

    return True


def add_renter_profile(id_, fname, lname, phone, email, contractor, license, completed):
    db = get_db2()

    db.run("INSERT INTO renters (id2, fname, lname, phone, email, contractor, license, insurance, completed, squareid) VALUES (%(id)s, %(fname)s, %(lname)s, %(phone)s, %(email)s, %(contractor)s, %(license)s, NULL, %(completed)s, NULL)",
            {"id":id_, "fname":fname, "lname":lname, "phone":phone, "email":email, "contractor":contractor, "license":license, "completed":completed}
    )



def create_booking(event_id, renter_id, equipment, start, end, n_days, n_weeks,n_months,transport,renter_name,company,phone,invoice_email,job_desc, exp_level, address1,address2,city,state,zip,commerical_prop,text):
    db = get_db2()

    db.run(
            "INSERT INTO reservations (renter_id, equipment, start, end_, n_days, n_weeks,n_months,transport,renter_name,company,phone,invoice_email,job_desc, exp_level, address1,address2,city,state,zip,commerical_prop,note,event_id, era_signed_date, era_signed_name, status, deposit_source_id, deposit_idempotency) "
            "VALUES (%(renter_id)s, %(equipment)s, %(start)s, %(end)s, %(n_days)s, %(n_weeks)s, %(n_months)s, %(transport)s, %(renter_name)s, %(company)s, %(phone)s, %(invoice_email)s, %(job_desc)s, %(exp_level)s,"
            "%(address1)s, %(address2)s, %(city)s, %(state)s, %(zip)s, %(commerical_prop)s, %(text)s, %(event_id)s, NULL , NULL , 0, NULL, NULL)",
            {"event_id":event_id, "renter_id":renter_id, "equipment":equipment, "start":start, "end":end, "n_days":n_days, "n_weeks":n_weeks, "n_months":n_months, "transport":transport, "renter_name":renter_name,
            "company":company, "phone":phone, "invoice_email":invoice_email, "job_desc":job_desc, "exp_level":exp_level, "address1":address1, "address2":address2, "city":city, "state":state,
            "zip":zip, "commerical_prop":commerical_prop, "text":text}
        )

    return True
