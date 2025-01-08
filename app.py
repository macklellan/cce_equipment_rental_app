
try:
    from flask import Flask, abort, request, redirect, url_for, session, send_from_directory, render_template, jsonify, make_response, send_file
    from flask_login import LoginManager, current_user, login_required, login_user, logout_user
    from datetime import timedelta, datetime
    from oauthlib.oauth2 import WebApplicationClient
    from functools import wraps

    import os
    import requests
    import json
    # import logging
    import sys
    import calendar_lib as evt

    # local
    from pdfer import gen, esign
    from user import User
    import db_lib
    from db_lib import get_renter_profile
    import square_lib
    import files

    # fix working directory so hard links work correctly
    BASEDIR = os.path.abspath(os.path.dirname(__file__))
    os.chdir(BASEDIR)

    # logging.basicConfig(filename='log.log',
    #                         filemode='a',
    #                         format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
    #                         datefmt='%H:%M:%S',
    #                         level=logging.DEBUG)
    #
    # logger = logging.getLogger(__name__)

    # app config
    app = Flask(__name__)

    app.secret_key = os.environ.get("SECRET_KEY") or os.urandom(24)

    # User session management setup
    # https://flask-login.readthedocs.io/en/latest
    login_manager = LoginManager()
    login_manager.init_app(app)


    # Flask-Login helper to retrieve a user from our db
    @login_manager.user_loader
    def load_user(user_id):
        return User.get(user_id)

    # Configuration
    GOOGLE_CLIENT_ID = gcid = os.environ['GOOGLE_CLIENT_ID']
    GOOGLE_CLIENT_SECRET = os.environ['GOOGLE_CLIENT_SECRET']
    GOOGLE_DISCOVERY_URL = (
    "https://accounts.google.com/.well-known/openid-configuration"
    )

    # OAuth 2 client setup
    client = WebApplicationClient(GOOGLE_CLIENT_ID)

    def get_google_provider_cfg():
        return requests.get(GOOGLE_DISCOVERY_URL).json()

    def get_google_cl_id():
        return os.environ['GOOGLE_CLIENT_ID']

    # admin endpoint wrapper
    # @login_required

    # admin endpoint wrapper
    # @admin_required
    def admin_required(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # logger.debug(request)
            # logger.info("request: {}  from: {}".format(request.path, str(request.remote_addr)))
            admin_list = ['ryanmcclellan2@gmail.com']
            if current_user.email not in admin_list:
                return abort(401)
            else:
                return f(*args, **kwargs)

        return decorated_function

    #####
    # # #
    # # #
    #####       EQUIPMENT DEFINTIONS
    # # #
    # # #
    #####

    category_dict = {'Compact Earth Moving':{'img':'bobcat-e42.webp'}, 'Generators':{'img':'generator.webp'}, 'Hand and Power Tools':{'img':'demohammer.jpg'}, 'Trailers':{'img':'trailer.webp'}}

    category_dict_all = {'Compact Earth Moving':{'img':'bobcat-e42.webp'}, 'Compaction':{'img':'compaction.webp'}, 'Generators':{'img':'generator.webp'}, 'Hand and Power Tools':{'img':'demohammer.jpg'},
        'Mowers':{'img':'mower.webp'}, 'Trailers':{'img':'trailer.webp'}, 'UTV':{'img':'utv.webp'}}

    cat_list = list(category_dict.keys())

    equipment_dict = {'2024_Bobcat_E26': {
            'brand': 'Bobcat',
            'model': 'E-26',
            'yr': '2024',
            'img': 'E26.jpg',
            'sn': '2024E26',
            'wt': '7500',
            'ppd': 225,
            'ppw': 875,
            'dfee': 200,
            'ifee': 25,
            'category': 'Compact Earth Moving',
            'note':'7500 Lb Mini Excavator',
            'note2':'Long Arm, X-change',
            'avl': True
        },'2024_Bobcat_E42': {
                'brand': 'Bobcat',
                'model': 'E-42',
                'yr': '2024',
                'img': 'bobcat-e42.webp',
                'sn': '2024E42',
                'wt': '10000',
                'ppd': 400,
                'ppw': 1500,
                'dfee': 200,
                'ifee': 25,
                'category': 'Compact Earth Moving',
                'note':'10000 Lb Mini Excavator',
                'note2':'X-change',
                'avl': False
        }}

    eq_d = equipment_dict

    att_list = {'2024_Bobcat_E26':['16" Toothed Bucket','Hydraulic Thumb (Equiped Standard)'],
                '2024_Bobcat_E42':['24" Toothed Bucket','Hydraulic Thumb (Equiped Standard)']}

    def tuples(iterable, arity):
        return [iterable[i:i+arity] for i in range(0, len(iterable), arity)]

    #####
    # # #
    # # #
    #####       PUBLIC INFO ENDPOINTS
    # # #
    # # #
    #####


    # RE-ROUTE INDEX TO RENTAL
    @app.route('/')
    def index():
        return render_template('index.html', gcid=gcid)

    # ABOUT PAGE *NEED TO REVIEW*
    @app.route('/about')
    def about():
        return render_template('about.html', gcid=gcid)

    # WEBSITE TERMS OF USE
    @app.route('/terms')
    def terms():
        return render_template('terms.html', gcid=gcid)

    # RESERVATION TERMS
    @app.route('/terms/reserve')
    def terms_reserve():
        return render_template('terms_reserve.html', gcid=gcid)

    # FOR DISPLAYING EQUIPMENT CATEGORIES & SELECTING EQUIPMENT -> LINK TO CALENDAR
    @app.route('/rentals')
    @app.route('/rentals/<category>')
    def rentals(category=None):
        if category == None:
            return render_template('rental_categories.html', gcid=gcid, cat_list=tuples(cat_list,4), cat_dict=category_dict)
        else:
            session['url'] = url_for('rentals', category=category)
            res = {key : val for key, val in equipment_dict.items()
                   if val['category'] == category}
            eq_list = list(res.keys())
            return render_template('rental_equipment_list.html', category=category, gcid=gcid, eq_list=tuples(eq_list, 3), eq_dict=res, att_list=att_list)

    #####
    # # #
    # # #
    #####       PRIVATE CUSTOMER ENDPOINTS
    # # #
    # # #
    #####


    # PROFILE PAGE
    # view, add, or edit profile info for the current user
    @app.route('/profile', methods=["GET", "POST"])
    @login_required
    def profile():
        profile_dict = get_renter_profile(current_user.id, True)

    # Submit New Profile Data
        if request.method == 'POST':
            if 'pbutton' in request.form:
                fname = request.form['fname']
                lname = request.form['lname']
                phone = request.form['phone']
                email = request.form['email']
                contractor = request.form['contractor']

                if phone is None or not (9 <= sum(c.isdigit() for c in phone) <= 11):
                    return render_template('profile.html', error="Invalid Phone Number", pro=profile_dict)

                if None in (fname, lname, phone, email):
                    return render_template('profile.html', error="An error occurred. Missing required information.", pro=profile_dict)

                current_user.create_renter_profile(fname, lname, phone, email, contractor, "", False)
                # includes blanks
                profile_dict = get_renter_profile(current_user.id, True)
                return render_template('profile.html', pro=profile_dict)

    # Submit New ID photo
            elif 'lbutton' in request.form:
                f = request.files['file']
                fname = current_user.id + f.filename
                files.upload_image(f, fname)
                db_lib.add_id(current_user.id, fname)

                if current_user.profile():
                    db_lib.set_complete_renter(current_user.id)
                return render_template('profile.html', success="Added ID Photo/Scan, Created Renter Profile! Admin will review for any issues.", pro=profile_dict)

    # Update Profile Data
            elif 'ubutton' in request.form:
                return render_template('profile.html', error="Cannot update profile at this time.", pro=profile_dict)

    # Delete/Hide Profile Data
            elif 'dbutton' in request.form:
                return render_template('profile.html', error="For prompt removal of your profile and renter information, please contact admin @ westerncarolinarentals@gmail.com. Thank You!", pro=profile_dict)

    # View Profile Data & Form
        else:

            if not current_user.renter_profile:
                return render_template('profile.html', pro=profile_dict, notice="Please complete your renter profile.")

            return render_template('profile.html', pro=profile_dict)



    @app.route("/profile_pic", methods=['GET'])
    @login_required
    def view_profile_pic():
        profile_dict = get_renter_profile(current_user.id)

        try:
            filename = profile_dict['license']
            file_path = os.path.join(ID_PIC_FOLDER, filename)
            tries = 2

            for x in range(tries):
                if not os.path.isfile(file_path):
                    files.download_image(filename)
                else:
                    return send_file(file_path)

                return make_response(f"File '{filename}' not found.", 404)
        except Exception as e:
            return make_response(f"Error: {str(e)}", 500)



    # View list of reservtions for the current user
    @app.route('/reservations', methods=["GET"])
    @login_required
    def reservation_list():
        profile_dict = get_renter_profile(current_user.id, True)
        res_list = current_user.reservations()
        return render_template('reservation_list.html', res_list=res_list, pro=profile_dict)



    #####
    # # #
    # # #
    #####       RESERVATION ENDPOINTS
    # # #
    # # #
    #####


    # Reservation flow handler, initiated from calender view.
    @app.route('/reserve/<equipment>', methods=["POST"])
    @login_required
    def reserve(equipment=None):
        profile_dict = get_renter_profile(current_user.id, True)

        if equipment_dict[equipment] is None or equipment_dict[equipment]['avl'] == False:
            return abort(404)

        if 'evtSave2' in request.form:
            start_date = request.form['evtStart']
            sd = datetime.strptime(start_date, '%Y-%m-%d').date()

            if datetime.strptime(start_date, '%Y-%m-%d') <= datetime.today():
                return redirect(session['url'])

            n_days = int(request.form['evtDays'])
            end = (sd + timedelta(days=n_days-1)).strftime('%Y-%m-%d')
            return render_template('reservation_create.html', equip=equipment, pro=profile_dict, start=start_date, end=end, n_days=n_days, rate=eq_d[equipment]['ppd'], dfee=eq_d[equipment]['dfee'], ifee=eq_d[equipment]['ifee'])

        if 'rbutton' in request.form:
            start = request.form['start']
            n_days = int(request.form['ndays'])
            end = request.form['end']
            trans = request.form['trans']
            fname = request.form['fname']
            lname = request.form['lname']
            company = request.form['comp']
            phone = request.form['phone']
            email = request.form['email']
            job_desc = request.form['job_desc']
            exp_level = request.form['exp_level']
            address1 = request.form['inputAddress']
            address2 = request.form['inputAddress2']
            city = request.form['inputCity']
            state = request.form['inputState']
            zip = request.form['inputZip']
            residential = (request.form['residential'] != 'Residential')
            notes = request.form['notes']
            ok = evt.save(start, end, "RESERVED", '#FFFFFF', '#FF5656', equipment, None)
            db_lib.create_booking(db_lib.last_event_id(), current_user.id, equipment, start, end, n_days, 0,0,trans,fname + ' ' + lname,company,phone,email,job_desc, exp_level, address1,address2,city,state,zip,residential,notes)
            return redirect(url_for("reservation", id=db_lib.last_booking_id()))



    # Reservation editor/ viewer
    @app.route('/reservation/<id>', methods=["GET"])
    @login_required
    def reservation(id=None):
        res_info = db_lib.get_res_info(id)

        # validate user / view
        # must be admin or match reservation to view
        if current_user.id != res_info['renter_id'] and not current_user.is_admin():
            return abort(403)

        profile_dict = get_renter_profile(current_user.id, True)
        session['url'] = url_for("reservation", id=id)

        # generalized so admin can view correctly
        billing = square_lib.square_billing_c(res_info['renter_id'])
        billing_cc = square_lib.square_billing_cc(res_info['renter_id'])
        last_4 = square_lib.square_billing_cc_last4(res_info['renter_id'])

        print(billing_cc)

        if res_info['transport'] == 'C&E Provided':
            res_info['transport2'] = 1
        else:
            res_info['transport2'] = 0

        esig = res_info['era_signed_date']

        depo = (res_info['deposit_source_id'] is not None)

        return render_template('reservation_view.html', res=res_info, pro=profile_dict, esig=esig, depo=depo, billing_c=billing, billing_cc=billing_cc, last_4=last_4, ppd=equipment_dict)



    # Add billing profile (square customer profile)
    # initiated from reservation editor view
    @app.route('/billprofile', methods=["POST"])
    @login_required
    def billing_profile():
        profile_dict = get_renter_profile(current_user.id, True)

        # billing details from request
        billing_dict = {
            'fname': request.form['fname'],
            'lname': request.form['lname'],
            'add1': request.form['address'],
            'add2': request.form['address2'],
            'country': request.form['country'],
            'state': request.form['state'],
            'city': request.form['city'],
            'zip': request.form['zip'],
            }

        # existing square profile, abort
        if current_user.square_billing_c():
            return abort(403)

        square_lib.add_customer(billing_dict, profile_dict)
        return redirect(session['url'])


    # Delete billing profile. Removes square id association, along with billing info.
    # Billing info retained for records in square..
    # initiated from reservation editor view
    @app.route('/billprofiledel', methods=["GET"])
    @login_required
    def delete_billing():
        profile_dict = db_lib.del_square_id(current_user.id)
        return redirect(session['url'])


    # Add credit card to square customer profile
    # initiated from reservation editor view
    @app.route('/c_update/<res_id>', methods=["POST"])
    @login_required
    def card_update(res_id=None):
        res_info = db_lib.get_res_info(res_id)

        # validate user / view
        # must match reservation
        if current_user.id != res_info['renter_id']:
            return abort(403)

        profile_dict = get_renter_profile(current_user.id, True)

        # token retreived from square websdk
        card_source_id = json.loads(request.data)['token']

        square_lib.add_cc(profile_dict['squareid'], card_source_id)
        return redirect(url_for("reservation", id=res_id))


    # initiate deposit for a reservation / customer
    # initiated from reservation editor view
    @app.route('/start_deposit/<res_id>', methods=["GET"])
    @login_required
    def start_deposit(res_id=None):
        res_info = db_lib.get_res_info(res_id)

        # validate user / view
        # must match reservation
        if current_user.id != res_info['renter_id']:
            return abort(403)

        profile_dict = get_renter_profile(current_user.id, True)
        square_lib.start_deposit(res_id, profile_dict['squareid'], current_user.square_billing_cc())
        return redirect(url_for("reservation", id=res_id))



    PDF_FOLDER = 'temp/'
    ID_PIC_FOLDER = 'temp'


    # view rental agreement
    # generate rental agreement if not already
    @app.route("/vera/<res_id>", methods=['GET'])
    @login_required
    def vera(res_id=None):
        res_info = db_lib.get_res_info(res_id)

        # validate user / view
        # must be admin or match reservation to view
        if current_user.id != res_info['renter_id'] and not current_user.is_admin():
            return abort(403)

        # if rental agreement exists
        try:

            filename = res_id + '.pdf'  # Sanitize the filename
            file_path = os.path.join(PDF_FOLDER, filename)

            if not os.path.isfile(file_path) and (res_info['era_signed_date'] is not None):
                try:
                    files.download_pdf(filename)
                except Exception as e:
                    print('Whoops')

            if os.path.isfile(file_path):
                return send_file(file_path)
            else:
                if current_user.id != res_info['renter_id']:
                    return make_response(f"AGREEMENT NOT GENERATED BY RENTER YET", 404)
                # else generate new rental agreement
                gen(res_id, res_info['renter_name'], equipment_dict)
                return make_response(f"GENERATED NEW RENTAL AGREEMENT PDF. PLEASE REFRESH TO VIEW.", 404)
        except Exception as e:
            raise e
            return make_response(f"Error: {str(e)}", 500)



    # sign agreement for reservation
    # ADD LOGIN CHECK AGAIN
    @app.route("/sera/<res_id>", methods=['GET'])
    @login_required
    def sera(res_id=None):
        res_info = db_lib.get_res_info(res_id)

        # validate user / view
        if current_user.id != res_info['renter_id']:
            return abort(403)

        # if rental agreement exists

        # actually just regen with signed flag (:)
        gen(res_id, res_info['renter_name'], equipment_dict, signed=True)

        # this does nothing...
        esign(res_id, res_info['renter_name'], datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        # this def needs to be here
        db_lib.add_esign(res_id, res_info['renter_name'], datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        # upload to cloud
        files.upload_pdf("temp/" + res_id + ".pdf", res_id + ".pdf")

        return redirect(url_for("reservation", id=res_id))



    # view id
    # ADD LOGIN CHECK AGAIN
    @app.route("/vid/<user_id>", methods=['GET'])
    @admin_required
    def getidpic(user_id=None):
        profile_dict = get_renter_profile(user_id, True)
        try:
            filename = profile_dict['license']
            file_path = os.path.join(ID_PIC_FOLDER, filename)
            if os.path.isfile(file_path):
                return send_file(file_path)
            else:
                return make_response(f"File '{filename}' not found.", 404)
        except Exception as e:
            return make_response(f"Error: {str(e)}", 500)


    #####
    # # #
    # # #
    #####       CALENDAR PAGES & LOGIC
    # # #
    # # #
    #####

    # (B) ROUTES
    # (B1) CALENDAR PAGE
    @app.route("/calendar/<equipment>", methods=["GET", "POST"])
    @login_required
    def calendar(equipment=None):
        profile_dict = get_renter_profile(current_user.id, True)
        session['url'] = url_for('calendar', equipment=equipment)
        return render_template("calendar.html", equip=equipment, note=equipment_dict[equipment]['note'], pro=profile_dict)

    # (B2) ENDPOINT - GET EVENTS
    @app.route("/calendar/get/", methods=["POST"])
    @login_required
    def get():
          data = dict(request.form)
          events = evt.get(int(data["month"]), int(data["year"]), str(data['equipment']))
          print(data)
          return "{}" if events is None else events


    #####
    # # #
    # # #
    #####       ADMIN ONLY ENDPOINTS
    # # #
    # # #
    #####


    # View list of reservtions for the current user
    @app.route('/admin2', methods=["GET"])
    @app.route('/admin2/approve_reservation/<approve>', methods=["GET"])
    @app.route('/admin2/deny_reservation/<deny>', methods=["GET"])
    @login_required
    @admin_required
    def reservation_list_admin(approve=None, deny=None):

        if approve is not None:
            res_info = db_lib.get_res_info(approve)
            db_lib.approve_reservation(approve)
            db_lib.show_cal_event(res_info['event_id'])
            return redirect(url_for("reservation_list_admin"))

        if deny is not None:
            res_info = db_lib.get_res_info(deny)
            db_lib.deny_reservation(deny)
            db_lib.hide_cal_event(res_info['event_id'])
            return redirect(url_for("reservation_list_admin"))

        profile_dict = get_renter_profile(current_user.id, True)
        res_list = current_user.reservations(allrecords=True)
        return render_template('reservation_list_admin.html', res_list=res_list, pro=profile_dict)


    # View list of users/renters
    @app.route('/admin3', methods=["GET"])
    @login_required
    @admin_required
    def renters_list_admin():
        r_list = db_lib.all_renter_profiles()
        return render_template('users_list_admin.html', user_list=r_list)


    #####
    # # #
    # # #
    #####       LOGIN & OAUTH ROUTES
    # # #
    # # #
    #####

    @app.route("/login", methods=["GET", "POST"])
    def login():
        # Find out what URL to hit for Google login
        google_provider_cfg = get_google_provider_cfg()
        authorization_endpoint = google_provider_cfg["authorization_endpoint"]

        # Use library to construct the request for Google login and provide
        # scopes that let you retrieve user's profile from Google
        request_uri = client.prepare_request_uri(
            authorization_endpoint,
            redirect_uri=request.base_url + "/callback",
            scope=["email"],
        )
        print(GOOGLE_CLIENT_ID)
        print(request_uri)
        return redirect(request_uri)


    @app.route("/login/callback")
    def callback():
        # Get authorization code Google sent back to you
        code = request.args.get("code")

        # Find out what URL to hit to get tokens that allow you to ask for
        # things on behalf of a user
        google_provider_cfg = get_google_provider_cfg()
        token_endpoint = google_provider_cfg["token_endpoint"]

        # Prepare and send a request to get tokens! Yay tokens!
        token_url, headers, body = client.prepare_token_request(
            token_endpoint,
            authorization_response=request.url,
            redirect_url=request.base_url,
            code=code
        )
        token_response = requests.post(
            token_url,
            headers=headers,
            data=body,
            auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
        )

        # Parse the tokens!
        client.parse_request_body_response(json.dumps(token_response.json()))

        # Now that you have tokens (yay) let's find and hit the URL
        # from Google that gives you the user's profile information,
        # including their Google profile image and email
        userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
        uri, headers, body = client.add_token(userinfo_endpoint)
        userinfo_response = requests.get(uri, headers=headers, data=body)

        # You want to make sure their email is verified.
        # The user authenticated with Google, authorized your
        # app, and now you've verified their email through Google!
        if userinfo_response.json().get("email_verified"):
            unique_id = userinfo_response.json()["sub"]
            users_email = userinfo_response.json()["email"]
            picture = userinfo_response.json()["picture"]
            # users_name = userinfo_response.json()["given_name"]
            users_name = 'Unknown'
        else:
            return "User email not available or not verified by Google.", 400

        # Create a user in your db with the information provided
        # by Google
        user = User(
            id_=unique_id, name=users_name, email=users_email, profile_pic=picture
        )

        # Doesn't exist? Add it to the database.
        if not User.get(unique_id):
            User.create(unique_id, users_name, users_email, picture)

        # Begin user session by logging the user in
        login_user(user)

        # Send user back to previous page
        try:
            if session['url']:
                return redirect(session['url'])
        except Exception as e:
            return redirect(url_for("index"))

        return redirect(url_for("index"))


    @app.route("/login/t123")
    def lt():
        user = User(
            id_='103913063181484802819', name='users_name', email='users_email', profile_pic='picture'
        )

        # Begin user session by logging the user in
        login_user(user)

        # Send user back to previous page
        try:
            if session['url']:
                return redirect(session['url'])
        except Exception as e:
            return redirect(url_for("index"))

        return redirect(url_for("index"))


    @app.route("/logout")
    @login_required
    def logout():
        logout_user()
        return redirect(url_for("index"))


#####
# # #
# # #
#####       ERRORS
# # #
# # #
#####

    # 404 not found page
    @app.errorhandler(404)
    def error_page(error):
        return render_template('404.html'), 404

    @app.errorhandler(401)
    def permission_error(e):
        return render_template('404.html'), 401

    # # returns text file used for ownership validation for SSL Certificate. (zerossl.com)
    # @app.route('/.well-known/pki-validation/<a>')
    # def test(a=None):
    #     logger.info(request)
    #     try:
    #         return send_from_directory('/opt/app/wearable/authorization-handler', '313733BD8EF952D0573BBC536E990A4D.txt')
    #     except Exception as e:
    #         logger.error("[DASHBOARD] error registering operator\n{}".format(e))
    #         return str(e)


    if __name__ == "__main__":
        # app.run(host='0.0.0.0', ssl_context="adhoc")
        #app.run(ssl_context="adhoc", debug=True, port=5000)
        app.run(host='0.0.0.0', port=5000, ssl_context='adhoc', debug=True)


except Exception as e:
    print(e)
    print("\nThere was a problem starting the program:\n\t *Check readme.txt*\n")
    raise e
