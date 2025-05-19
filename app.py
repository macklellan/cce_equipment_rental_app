# CCE
# Ryan McClellan 2025

# Main application for equipment rental and reservation website.

# initialization wrapped in try/catch
try:
    from flask import Flask, abort, request, redirect, url_for, session, send_from_directory, render_template, jsonify, make_response, send_file
    from flask_login import LoginManager, current_user, login_required, login_user, logout_user
    from datetime import timedelta, datetime
    from oauthlib.oauth2 import WebApplicationClient
    from functools import wraps
    import os
    import requests
    import json
    import sys
    from pathlib import Path
    import files
    import random
    import string

    # local imports
    from pdfer import gen, esign
    from user import User
    import db_lib
    from db_lib import get_renter_profile
    import calendar_lib as evt
    import square_lib



#############################################
# # #                                   # # # #
# # #                                   # # # # #
#####       APP CONFIGURATION           ###########
# # #                                   # # # # #
# # #                                   # # # #
#############################################



    # app config
    app = Flask(__name__)
    app.secret_key = os.environ.get("SECRET_KEY") or os.urandom(24)
    app.config['SESSION_COOKIE_SECURE'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'None'
    # app.config['SERVER_NAME'] = 'rent.carolinac-e.com'

    # temporary files, renter uploaded images stored in Azure
    TMP_DIR = Path("/tmp")

    # User session management setup
    # https://flask-login.readthedocs.io/en/latest
    login_manager = LoginManager()
    login_manager.init_app(app)

    # Flask-Login helper to retrieve a user from our db
    @login_manager.user_loader
    def load_user(user_id):
        return User.get(user_id)

    # Google Oauth Config
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

    # Square payment processor config
    SQ_APP_ID = os.environ['SQUARE_APP_ID']
    SQ_LOC = os.environ['SQUARE_LOC']
    SQ_ENV = os.environ['SQUARE_ENV']
    PROD = False

    if SQ_ENV == 'production':
        PROD = True



#############################################
# # #                                   # # # #
# # #                                   # # # # #
#####       ACCESS CONTROL              ###########
# # #                                   # # # # #
# # #                                   # # # #
#############################################



    def user_only(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):

            code = dict(session).get('login_token', None)
            res_id = dict(session).get('res_id_access', None)

            if current_user.is_authenticated and code is None:
                return f(*args, **kwargs)
            else:
                return abort(401)

        return decorated_function


    # admin endpoint wrapper
    def admin_required(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):

            if current_user.is_admin:
                return f(*args, **kwargs)

            return abort(401)

        return decorated_function


    # simple access endpoint wrapper
    # used in addition to
    def simple_access(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):

            # token vars
            code = dict(session).get('login_token', None)
            res_id = dict(session).get('res_id_access', None)

            # no access token vars
            if code is None or res_id is None:
                # user is logged in
                if current_user.is_authenticated:
                    return f(*args, **kwargs)
                return abort(401)

            # access token vars check out
            if db_lib.get_access_link_code(res_id) == code:
                return f(*args, **kwargs)

            return abort(401)

        return decorated_function



#############################################
# # #                                   # # # #
# # #                                   # # # # #
#####       EQUIPMENT DATA              ###########
# # #                                   # # # # #
# # #                                   # # # #
#############################################



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

    att_list = {'2024_Bobcat_E26':['16" Toothed Bucket','Hydraulic Thumb (Equipped Standard)'],
                '2024_Bobcat_E42':['24" Toothed Bucket','Hydraulic Thumb (Equipped Standard)']}

    def tuples(iterable, arity):
        return [iterable[i:i+arity] for i in range(0, len(iterable), arity)]



#############################################
# # #                                   # # # #
# # #                                   # # # # #
#####       PUBLIC ACCESS               ###########
# # #                                   # # # # #
# # #                                   # # # #
#############################################



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
            category = category.replace('%20', ' ')
            session['url'] = url_for('rentals', category=category)
            res = {key : val for key, val in equipment_dict.items()
                   if val['category'] == category}
            eq_list = list(res.keys())
            return render_template('rental_equipment_list.html', category=category, gcid=gcid, eq_list=tuples(eq_list, 3), eq_dict=res, att_list=att_list)



#############################################
# # #                                   # # # #
# # #                                   # # # # #
#####       RENTER "PROFILE"            ###########
# # #                                   # # # # #
# # #                                   # # # #
#############################################



    # PROFILE PAGE
    # view, add, or edit profile info for the current user
    @app.route('/profile', methods=["GET", "POST"])
    @app.route('/profile/<flow>', methods=["GET"])
    @user_only
    def profile(flow=None):
        profile_dict = get_renter_profile(current_user.id, True)

        if flow is not None and flow == 'cal_b':
            session['cal_b'] = True

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

                phone = ''.join(filter(str.isdigit, phone))

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

                if not current_user.profile_complete():
                    db_lib.set_complete_renter(current_user.id)

                if session.get('cal_b') == True:
                    session.pop('cal_b')
                    return redirect(session['url'])

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
    @user_only
    def view_profile_pic():
        profile_dict = get_renter_profile(current_user.id)

        try:
            filename = profile_dict['license']
            file_path = TMP_DIR / filename
            tries = 2

            for x in range(tries):

                if not os.path.isfile(file_path):
                    files.download_image(filename)

                if os.path.isfile(file_path):
                    return send_file(file_path)

                return make_response(f"File '{filename}' not found.", 404)
        except Exception as e:
            return make_response(f"Error: {str(e)}", 500)



    # View list of reservtions for the current user
    @app.route('/reservations', methods=["GET"])
    @user_only
    def reservation_list():
        res_list = current_user.reservations()
        return render_template('reservation_list.html', res_list=res_list)



#############################################
# # #                                   # # # #
# # #                                   # # # # #
#####       RESERVATION CONTROL         ###########
# # #                                   # # # # #
# # #                                   # # # #
#############################################



    # Reservation flow handler, initiated from calender view.
    @app.route('/reserve/<equipment>', methods=["POST"])
    @user_only
    def reserve(equipment=None):
        profile_dict = get_renter_profile(current_user.id, True)

        if equipment_dict[equipment] is None or equipment_dict[equipment]['avl'] == False:
            return abort(404)

        if 'evtSave2' in request.form:
            start_date = request.form['evtStart']
            sd = datetime.strptime(start_date, '%Y-%m-%d').date()
            sd2 = sd.strftime('%Y-%m-%d')

            # return error for reservation start times out of range
            if datetime.strptime(start_date, '%Y-%m-%d') <= datetime.today():
                error_msg = 'Selected date not available ({})'.format(sd2)
                session['url'] = url_for('calendar', equipment=equipment)
                session['cal_error_show'] = 'Selected date not available ({})'.format(sd2)
                return redirect(url_for('calendar', equipment=equipment))

            n_days = int(request.form['evtDays'])
            n_weeks = int(request.form['evtWeeks'])
            end = (sd + timedelta(days=n_days-1, weeks=n_weeks)).strftime('%Y-%m-%d')


            return render_template('reservation_create.html', equip=equipment, eq_dict=eq_d, att_list=att_list, pro=profile_dict, start=sd2, end=end, n_days=n_days, n_weeks=n_weeks, rate=eq_d[equipment]['ppd'], rate2=eq_d[equipment]['ppw'],  dfee=eq_d[equipment]['dfee'], ifee=eq_d[equipment]['ifee'])

        if 'rbutton' in request.form:
            start = request.form['start']
            n_days = int(request.form['ndays'])
            n_weeks = int(request.form['nweeks'])
            end = request.form['end']
            trans = request.form['trans']
            fname = request.form['fname']
            lname = request.form['lname']
            company = request.form['comp']
            phone = request.form['phone']
            if sum(c.isdigit() for c in phone) == 10:
                phone = ''.join(filter(str.isdigit, phone))
            else:
                return make_response("Error: Bad phone input. Please go back and correct.", 202)

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
            db_lib.create_booking(db_lib.last_event_id(), current_user.id, equipment, start, end, n_days, n_weeks ,0,trans,fname + ' ' + lname,company,phone,email,job_desc, exp_level, address1,address2,city,state,zip,residential,notes)
            ok = evt.save(start, end, "RESERVED", '#FFFFFF', '#FF5656', equipment, None)
            return redirect(url_for("reservation", id=db_lib.last_booking_id()))


    def token_access(id):
        access_to_res = dict(session).get('res_id_access', None)

        # temp access code match
        if access_to_res is not None:
            if int(access_to_res) == int(id):
                return True

        return False


    # Reservation editor/ viewer
    @app.route('/reservation/<id>', methods=["GET"])
    @login_required
    @simple_access
    def reservation(id=None):

        res_info = db_lib.get_res_info(id)

        if res_info is None:
            return abort(403)

        # validate user
        # must match renter id attatched to reservation, admin, or have access token that matches
        if current_user.id != res_info['renter_id'] and not current_user.is_admin() and not token_access(id):
            return abort(403)


        profile_dict = get_renter_profile(current_user.id, True)
        session['url'] = url_for("reservation", id=id)

        # generalized so admin can view correctly
        billing = square_lib.square_billing_c(res_info['renter_id'])
        billing_cc = square_lib.square_billing_cc(res_info['renter_id'])
        last_4 = square_lib.square_billing_cc_last4(res_info['renter_id'])

        if res_info['transport'] == 'C&E Provided':
            res_info['transport2'] = 1
        else:
            res_info['transport2'] = 0

        res_info['start'] = res_info['start'].strftime('%Y-%m-%d')
        res_info['end'] = res_info['end'].strftime('%Y-%m-%d')

        esig = res_info['era_signed_date']

        depo = (res_info['deposit_source_id'] is not None)

        equipment = res_info['equipment']

        return render_template('reservation_view.html', res=res_info, pro=profile_dict, esig=esig, depo=depo, billing_c=billing,
        billing_cc=billing_cc, last_4=last_4, ppd=equipment_dict, sq_app_id=SQ_APP_ID, sq_loc=SQ_LOC, prod=PROD, eq_dict=eq_d,
        equip = res_info['equipment'], att_list=att_list,
        n_days=res_info['n_days'], n_weeks=res_info['n_weeks'], rate=eq_d[equipment]['ppd'], rate2=eq_d[equipment]['ppw'],  dfee=eq_d[equipment]['dfee'], ifee=eq_d[equipment]['ifee'])



    # Add billing profile (square customer profile)
    # initiated from reservation editor view
    @app.route('/billprofile', methods=["POST"])
    @login_required
    @simple_access
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
    @simple_access
    def delete_billing():
        profile_dict = db_lib.del_square_id(current_user.id)
        return redirect(session['url'])


    # Add credit card to square customer profile
    # initiated from reservation editor view
    @app.route('/c_update/<res_id>', methods=["POST"])
    @login_required
    @simple_access
    def card_update(res_id=None):

        res_info = db_lib.get_res_info(res_id)

        # validate user / view
        # must be admin or match reservation id to view
        if current_user.id != res_info['renter_id'] and not current_user.is_admin() and not token_access(id):
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
    @simple_access
    def start_deposit(res_id=None):
        res_info = db_lib.get_res_info(res_id)

        # validate user / view
        # must be admin or match reservation id to view
        if current_user.id != res_info['renter_id'] and not current_user.is_admin() and not token_access(id):
            return abort(403)

        profile_dict = get_renter_profile(current_user.id, True)
        square_lib.start_deposit(res_id, profile_dict['squareid'], current_user.square_billing_cc())
        return redirect(url_for("reservation", id=res_id))



    PDF_FOLDER = TMP_DIR
    ID_PIC_FOLDER = 'tmp/'


    # view rental agreement
    # generate rental agreement if not already

    @app.route("/vera/<res_id>", methods=['GET'])
    @login_required
    @simple_access
    def vera(res_id=None):
        res_info = db_lib.get_res_info(res_id)

        # validate user / view
        # must be admin or match reservation id to view
        if current_user.id != res_info['renter_id'] and not current_user.is_admin() and not token_access(id):
            return abort(403)

        try:

            filename = res_id + '.pdf'  # Sanitize the filename
            file_path = TMP_DIR / filename

            #print("path: ")
            #print(file_path)

            # retry download/send/generate/send flow 3 times
            for x in range(2):

                # if file not found but supposed to be signed
                if not os.path.isfile(file_path) and (res_info['era_signed_date'] is not None):
                    # attempt download
                    try:
                        files.download_pdf(file_path, filename)
                    except Exception as e:
                        raise e
                        #print('Whoops')

                if os.path.isfile(file_path):
                    return send_file(file_path)

                # if file not found

                if res_info['era_signed_date'] is not None:
                    return make_response("Error: Unable to view at this time. Please contact administrator.", 500)

                else:
                    if current_user.id != res_info['renter_id']:
                        return make_response(f"AGREEMENT NOT GENERATED BY RENTER YET", 404)
                    # else generate new rental agreement
                    gen(res_id, res_info['renter_name'], equipment_dict)
                    if os.path.isfile(file_path):
                        return send_file(file_path)

            return make_response("Error: Unable to generate at this time...", 404)

        except Exception as e:
            raise e
            return make_response(f"Error: {str(e)}", 500)





    # sign agreement for reservation
    # ADD LOGIN CHECK AGAIN
    @app.route("/sera/<res_id>", methods=['GET'])
    @login_required
    @simple_access
    def sera(res_id=None):

        res_info = db_lib.get_res_info(res_id)

        # validate user / view
        # must be admin or match reservation id to view
        if current_user.id != res_info['renter_id'] and not current_user.is_admin() and not token_access(id):
            return abort(403)

        # if rental agreement exists

        # actually just regen with signed flag (:)
        gen(res_id, res_info['renter_name'], equipment_dict, signed=True)

        # this does nothing...
        esign(res_id, res_info['renter_name'], datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        # this def needs to be here
        db_lib.add_esign(res_id, res_info['renter_name'], datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        fname = res_id + ".pdf"
        # upload to cloud
        files.upload_pdf(TMP_DIR / fname, res_id + ".pdf")

        return redirect(url_for("reservation", id=res_id))



    # endpoint for viewing a user license/id picture
    # returns raw file, no error checking
    @app.route("/vid/<user_id>", methods=['GET'])
    @admin_required
    def getidpic(user_id=None):
        try:

            filename = profile_dict['license']
            file_path = TMP_DIR / filename
            tries = 2

            for x in range(tries):

                if not os.path.isfile(file_path):
                    files.download_image(filename)

                if os.path.isfile(file_path):
                    return send_file(file_path)

                return make_response(f"File '{filename}' not found.", 404)

        except Exception as e:
            return make_response(f"Error: {str(e)}", 500)



#############################################
# # #                                   # # # #
# # #                                   # # # # #
#####       CALENDAR PAGES & LOGIC      ###########
# # #                                   # # # # #
# # #                                   # # # #
#############################################



    # endpoint for rental equipment calendar
    # shows available / taken dates for specified equipment
    @app.route("/calendar/<equipment>", methods=["GET", "POST"])
    @user_only
    def calendar(equipment=None, error=None):
        profile_dict = get_renter_profile(current_user.id, True)
        session['url'] = url_for('calendar', equipment=equipment)

        # processing error
        if session.get('cal_error_show'):
            error = session.pop('cal_error_show')

        return render_template("calendar.html", equip=equipment, note=equipment_dict[equipment]['note'], pro=profile_dict, error_msg=error)


    # backend method for retreiving rental dates for calendar
    @app.route("/calendar/get/", methods=["POST"])
    @login_required
    def get():
          data = dict(request.form)
          events = evt.get(int(data["month"]), int(data["year"]), str(data['equipment']))
          return "{}" if events is None else events



#############################################
# # #                                   # # # #
# # #                                   # # # # #
#####       ADMIN ONLY SECTION          ###########
# # #                                   # # # # #
# # #                                   # # # #
#############################################



    # View list of all equipment reservtions
    @app.route('/admin2', methods=["GET"])
    @app.route('/admin2/approve_reservation/<approve>', methods=["GET"])
    @app.route('/admin2/deny_reservation/<deny>', methods=["GET"])
    @app.route('/admin2/start_fuf/<start>', methods=["GET"])
    @app.route('/admin2/complete_fuf/<complete>', methods=["GET"])
    @app.route('/admin2/pend_fuf/<pend>', methods=["GET"])
    @admin_required
    def reservation_list_admin(approve=None, deny=None, start=None, complete=None, pend=None):

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

        if pend is not None:
            res_info = db_lib.get_res_info(pend)
            db_lib.update_reservation_status(pend, 0)
            return redirect(url_for("reservation_list_admin"))

        if start is not None:
            res_info = db_lib.get_res_info(start)
            if res_info['status'] < 1:
                return render_template('reservation_list_admin.html', error="Can't start fufillment on un-approved reservations!")
            else:
                db_lib.update_reservation_status(start, 2)
                return redirect(url_for("reservation_list_admin"))

        if complete is not None:
            res_info = db_lib.get_res_info(complete)
            if res_info['status'] < 1:
                return render_template('reservation_list_admin.html', error="Can't complete fufillmnent on un-approved reservations!")
            else:
                db_lib.update_reservation_status(complete, 3)
                return redirect(url_for("reservation_list_admin"))

        res_list = current_user.reservations(allrecords=True)

        res_list_sorted = sorted(res_list, key=lambda x: x["res_id"], reverse=True)

        return render_template('reservation_list_admin.html', res_list=res_list_sorted)


    # View list of users/renters
    @app.route('/admin/renters', methods=["GET"])
    @admin_required
    def renters_list_admin():
        r_list = db_lib.all_renter_profiles()
        return render_template('users_list_admin.html', user_list=r_list)


    # create / get access link for reservation
    @app.route('/admin5/<res_id>', methods=["GET"])
    @admin_required
    def get_access_link(res_id=None):
        access_link_code = db_lib.get_access_link_code(res_id)
        res_info = db_lib.get_res_info(res_id)

        if access_link_code == None:
            rs = ''.join(random.choices(string.ascii_letters + string.digits, k=36))
            db_lib.add_access_link(res_id, rs)

            # create new user and renter profile only used by this reservation....
            if not User.get(rs):
                User.create(rs, 'Temporary User', 'Temporary User', 'Temporary User')
                User.static_create_renter_profile(rs, res_info['renter_name'], '', res_info['phone'], res_info['invoice_email'], True, "", True)
                db_lib.update_reservation_renter(res_id, rs)

            access_link_code = db_lib.get_access_link_code(res_id)


        data = { "link" : url_for("logintoken", code=access_link_code, _external=True)}
        return jsonify(data)



#############################################
# # #                                   # # # #
# # #                                   # # # # #
#####       LOGIN AND OAUTH             ###########
# # #                                   # # # # #
# # #                                   # # # #
#############################################



    # Simple reservation access via link
    @app.route("/logintoken/<code>", methods=["GET"])
    def logintoken(code=None):
        res_id = db_lib.check_access_link_code(code)
        if res_id == None:
            return abort(404)
        else:
            session['login_token'] = code
            session['res_id_access'] = res_id

            if not User.get(code):
                return abort(401)

            user = User.get(code)

            login_user(user)

            return redirect(url_for("reservation", id=res_id))


    @app.route("/login", methods=["GET", "POST"])
    def login():
        # Find out what URL to hit for Google login
        google_provider_cfg = get_google_provider_cfg()
        authorization_endpoint = google_provider_cfg["authorization_endpoint"]

        redirect_uri = request.base_url + "/callback"

        #print(" REDIR URI: " + redirect_uri)

        redirect_uri = redirect_uri.replace('https', 'http').replace('http', 'https')

        #print(" FIXED REDIR URI: " + redirect_uri)

        # Use library to construct the request for Google login and provide
        # scopes that let you retrieve user's profile from Google
        request_uri = client.prepare_request_uri(
            authorization_endpoint,
            redirect_uri=redirect_uri,
            scope=["email"],
        )

        #print("REDIR REQUEST URI: " + request_uri)

        return redirect(request_uri)


    @app.route("/login/callback")
    def callback():
        # Get authorization code Google sent back to you
        code = request.args.get("code")

        # Find out what URL to hit to get tokens that allow you to ask for things on behalf of a user
        google_provider_cfg = get_google_provider_cfg()
        token_endpoint = google_provider_cfg["token_endpoint"]
        auth_resp = request.url.replace('https', 'http').replace('http', 'https')
        redir_uri = request.base_url.replace('https', 'http').replace('http', 'https')

        #print("Token endpoint: " + token_endpoint)
        #print("Callback auth_resp URI: " + auth_resp)
        #print("Callback REDIR URI: " + redir_uri)

        # Prepare and send a request to get tokens! Yay tokens!
        token_url, headers, body = client.prepare_token_request(
            token_endpoint,
            authorization_response=auth_resp,
            redirect_url=redir_uri,
            code=code
        )

        #print("Token URL: " + token_url)

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

        #print("userinfo endpoint: " + userinfo_endpoint)
        #print("userinfo uri: " + uri)

        userinfo_response = requests.get(uri, headers=headers, data=body)

        #print("userinfo response: " + str(userinfo_response.json()))

        # You want to make sure their email is verified.
        # The user authenticated with Google, authorized your
        # app, and now you've verified their email through Google!
        if userinfo_response.json().get("email_verified"):
            unique_id = str(userinfo_response.json()["sub"])
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

        #print("user id: " + user.id)

        # Doesn't exist? Add it to the database.
        if not User.get(unique_id):
            User.create(unique_id, users_name, users_email, picture)
            #print("Created new user")
        else:
            print("Existing User")
        # Begin user session by logging the user in
        login_user(user)
        #print("Logged in!!")

        # Send user back to previous page
        try:
            if session['url']:
                #print("Session Redirect")
                return redirect(session['url'])
        except Exception as e:
            #print("index redirect - missing session url")
            return redirect(url_for("index"))

        #print("index Redirect")
        return redirect(url_for("index"))



    @app.route("/logout")
    @login_required
    def logout():
        logout_user()
        [session.pop(key) for key in list(session.keys())]
        return redirect(url_for("index"))



#############################################
# # #                                   # # # #
# # #                                   # # # # #
#####       ERRORS                     ###########
# # #                                   # # # # #
# # #                                   # # # #
#############################################



    # 404 not found page
    @app.errorhandler(404)
    def error_page(error):
        return render_template('404.html'), 404

    @app.errorhandler(403)
    def permission_error(e):
        return render_template('403.html'), 403

    @app.errorhandler(401)
    def permission_error(e):
        return render_template('401.html'), 401



    if __name__ == "__main__":
        # app.run(host='0.0.0.0', ssl_context="adhoc")
        app.run(ssl_context="adhoc", debug=True, port=5000)
        # app.run(host='0.0.0.0', port=5000, ssl_context='adhoc', debug=True)
        # app.run(host='0.0.0.0', port=5000, ssl_context='adhoc')


except Exception as e:
    print(e)
    print("\nThere was a problem starting the program:\n\t *Check readme.txt*\n")
    raise e
