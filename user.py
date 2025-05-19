from flask_login import UserMixin
from db_lib import get_db2, get_renter_profile, add_renter_profile
from square_lib import get_cc


class User(UserMixin):
    def __init__(self, id_, name, email, profile_pic, renter_profile=None):
        self.id = id_
        self.name = name
        self.email = email
        self.profile_pic = profile_pic
        self.renter_profile = renter_profile


    def profile_complete(self):
        self.renter_profile = get_renter_profile(self.id)

        if self.renter_profile == None:
            return False

        return int(self.renter_profile['completed'])


    def is_admin(self):
        admin_list = ['ryanmacklellan@gmail.com', 'mackenziecranford0197@gmail.com', 'ryanmcclellan2@gmail.com']
        if self.email in admin_list:
            return True

        return False


    def square_billing_c(self):
        if self.renter_profile == None:
            self.renter_profile = get_renter_profile(self.id)

        # no square profile
        if self.renter_profile['squareid'] is None:
            return None

        if self.renter_profile['squareid'] != 'None':
            return True
        return False


    def square_billing_cc(self):
        if self.renter_profile == None:
            self.renter_profile = get_renter_profile(self.id)

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
        db = get_db2()

        ress = None

        if allrecords and self.is_admin():

            with db.get_cursor() as curs:
                curs.execute("SELECT * FROM reservations")
                ress = curs.fetchall()

        else:

            with db.get_cursor() as curs:
                curs.execute(f"SELECT * FROM reservations WHERE renter_id = '{self.id}';")
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
    def static_create_renter_profile(id, fname, lname, phone, email, contractor, license, completed):
        add_renter_profile(id, fname, lname, phone, email, contractor, license, completed)
        return True



    @staticmethod
    def get(user_id):

        db = get_db2();

        user = None

        with db.get_cursor() as curs:
            curs.execute(f"SELECT * FROM users WHERE id = '{user_id}' ;")
            user = curs.fetchone()

        if not user:
            return None

        user = User(
            id_=user[0], name=user[1], email=user[2], profile_pic=user[3], renter_profile=get_renter_profile(user_id)
        )

        return user


    @staticmethod
    def create(id_, name, email, profile_pic):
        db = get_db2()
        with db.get_cursor() as curs:
            curs.execute(
                f"INSERT INTO users (id, name, email, profile_pic) VALUES ('{id_}', '{name}', '{email}', '{profile_pic}')"
            )
