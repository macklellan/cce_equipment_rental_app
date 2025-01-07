from flask_login import UserMixin

from db_lib import get_db, get_renter_profile, add_renter_profile
from square_lib import get_cc

class User(UserMixin):
    def __init__(self, id_, name, email, profile_pic, renter_profile=None):
        self.id = id_
        self.name = name
        self.email = email
        self.profile_pic = profile_pic
        self.renter_profile = renter_profile


    def profile_complete(self):
        if self.renter_profile == None:
            return False

        return int(self.renter_profile['completed'])


    def is_admin(self):
        if self.email == 'ryanmcclellan2@gmail.com':
            return True
        return False


    def square_billing_c(self):
        if self.renter_profile == None:
            self.refresh_renter_profile()

        # no square profile
        if self.renter_profile['squareid'] is None:
            return None

        if self.renter_profile['squareid'] != 'None':
            return True
        return False


    def square_billing_cc(self):
        if self.renter_profile == None:
            self.refresh_renter_profile()

        # no square profile
        if self.renter_profile['squareid'] is None:
            return None

        cc_list = get_cc(self.renter_profile['squareid'])

        if bool(cc_list) == True:
            return cc_list['cards'][0]['id']
        return None



    def profile_error(self):
        return None


    def reservations(self, allrecords=False):
        db = get_db()
        curs = db.cursor()

        ress = None
        if allrecords and self.is_admin():

            curs.execute(
                "SELECT * FROM reservations"
            )

        else:
            curs.execute(
                "SELECT * FROM reservations WHERE renter_id = %s and renter_id != %s;", (self.id, 'None')
            )

        ress = curs.fetchall()

        new_ress = []

        if not ress:
            return new_ress

        for res in ress:
            new_row  = {
                    'res_id':res[0], 'renter_id':res[1], 'equipment':res[2], 'start':res[3], 'end':res[4], 'n_days':res[5],
                    'n_weeks':res[6], 'n_months':res[7], 'transport':res[8], 'renter_name':res[9], 'company':res[10], 'phone':res[11],
                    'invoice_email':res[12], 'job_desc':res[13], 'exp_level':res[14], 'address1':res[15], 'address2':res[16], 'city':res[17],
                    'state':res[18], 'zip':res[19], 'commerical_prop':res[20], 'note':res[21], 'event_id':res[22], 'status':res[25]
                }
            new_ress.append(new_row)

        return new_ress


    def create_renter_profile(self, fname, lname, phone, email, contractor, license, completed):
        add_renter_profile(self.id, fname, lname, phone, email, contractor, license, completed)
        self.renter_profile = get_renter_profile(self.id)


    @staticmethod
    def get(user_id):
        db = get_db()
        curs = db.cursor()
        curs.execute(
            "SELECT * FROM user WHERE id = %s and id != %s;", (user_id, 'None')
        )
        user = curs.fetchone()
        curs.close()
        db.close()

        if not user:
            return None

        user = User(
            id_=user[0], name=user[1], email=user[2], profile_pic=user[3], renter_profile=get_renter_profile(user_id)
        )
        return user


    @staticmethod
    def create(id_, name, email, profile_pic):
        db = get_db()
        curs = db.cursor()
        curs.execute(
            "INSERT INTO user (id, name, email, profile_pic) VALUES (%s, %s, %s, %s)",
            (id_, name, email, profile_pic),
        )
        db.commit()
        curs.close()
        db.close()
