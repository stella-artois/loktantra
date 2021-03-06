import time
from sqlite3 import dbapi2 as sqlite3
from hashlib import md5
from datetime import datetime
from flask import Flask, request, session, url_for, redirect, \
     render_template, abort, g, flash, _app_ctx_stack, jsonify
from werkzeug import check_password_hash, generate_password_hash

import utils.message_utils as message_utils
import utils.search_utils as search_utils
import utils.user_utils as user_utils
import utils.department_utils as department_utils

# configuration
DATABASE = '/tmp/loktantra.db'
PER_PAGE = 30
DEBUG = True
SECRET_KEY = 'development key'
USERS = {
    'department' : 1,
    'user' : 2
}


# create our little application :)
app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('APP_SETTINGS', silent=True)
app.jinja_env.globals.update(getTags= message_utils.getTags)


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    top = _app_ctx_stack.top
    if not hasattr(top, 'sqlite_db'):
        top.sqlite_db = sqlite3.connect(app.config['DATABASE'])
        top.sqlite_db.row_factory = sqlite3.Row
    return top.sqlite_db


@app.teardown_appcontext
def close_database(exception):
    """Closes the database again at the end of the request."""
    top = _app_ctx_stack.top
    if hasattr(top, 'sqlite_db'):
        top.sqlite_db.close()


def init_db():
    """Creates the database tables."""
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


def query_db(query, args=(), one=False):
    """Queries the database and returns a list of dictionaries."""
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    return (rv[0] if rv else None) if one else rv


def get_user_id(username):
    """Convenience method to look up the id for a username."""
    rv = query_db('select user_id from user where username = ?',
                  [username], one=True)
    return rv[0] if rv else None


def format_datetime(timestamp):
    """Format a timestamp for display."""
    return datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d @ %H:%M')


def gravatar_url(email, size=80):
    """Return the gravatar image for the given email address."""
    return 'http://www.gravatar.com/avatar/%s?d=identicon&s=%d' % \
        (md5(email.strip().lower().encode('utf-8')).hexdigest(), size)


def get_user_type():
    if 'user_id' in session:
        return USERS['user']
    if 'department_id' in session:
        return USERS['department']

@app.before_request
def before_request():
    g.user = None
    if 'user_id' in session:
        g.user = query_db('select * from user where user_id = ?',
            [session['user_id']], one=True)
    if 'department_id' in session:
        g.user = query_db('select * from department where department_id = ?',
            [session['department_id']], one=True)

@app.route('/')
def timeline():
    """Shows a users timeline or if no user is logged in it will
    redirect to the public timeline.  This timeline shows the user's
    messages as well as all the messages of followed users.
    """
    if not g.user:
        return redirect(url_for('public_timeline'))
    user_type = get_user_type()
    if user_type == USERS['user']:
        messages = query_db('''
            select message.*, user.* from message, user
            where message.author_id = user.user_id and (
                user.user_id = ? or
                user.user_id in (select whom_id from follower
                                        where who_id = ?))
            order by message.pub_date desc limit ?''',
            [session['user_id'], session['user_id'], PER_PAGE])
        return render_template('timeline.html', messages = messages)

    elif user_type == USERS['department']:
        messages = department_utils.get_timeline(get_db(), session['department_id'])
        return render_template('timeline.html', messages = messages)


@app.route('/public')
def public_timeline():
    """Displays the latest messages of all users."""
    return render_template('timeline.html', messages=query_db('''
        select message.*, user.* from message, user
        where message.author_id = user.user_id
        order by message.pub_date desc limit ?''', [PER_PAGE]))


@app.route('/<username>')
def user_timeline(username):
    """Display's a users tweets."""
    profile_user = query_db('select * from user where username = ?',
                            [username], one=True)
    if profile_user is None:
        department_user = query_db('select * from department where username = ?',
                            [username], one=True)
        if department_user is None:
            flash('User doesn\'t exist.')
            return redirect(url_for('public_timeline'))
        else:
            db = get_db()
            muddas = department_utils.get_muddas(db, department_user['department_id'])
            return render_template('department-timeline.html',
                messages = department_utils.get_timeline(db, department_user['department_id']),
                department_user = department_user,
                assigned_muddas = muddas['assigned'],
                solved_muddas = muddas['solved'])

    else:
        if g.user:
            mudda_count = user_utils.get_mudda_count(get_db(), profile_user['user_id'])
            return render_template('user-timeline.html', messages=query_db('''
                select message.*, user.* from message, user where
                user.user_id = message.author_id and user.user_id = ?
                order by message.pub_date desc limit ?''',
                [profile_user['user_id'], PER_PAGE]),
                profile_user=profile_user, mudda_count=mudda_count)


@app.route('/<username>/follow')
def follow_user(username):
    """Adds the current user as follower of the given user."""
    if not g.user:
        abort(401)
    whom_id = get_user_id(username)
    if whom_id is None:
        abort(404)
    db = get_db()
    db.execute('insert into follower (who_id, whom_id) values (?, ?)',
              [session['user_id'], whom_id])
    db.commit()
    flash('You are now following "%s"' % username)
    return redirect(url_for('user_timeline', username=username))


@app.route('/<username>/unfollow')
def unfollow_user(username):
    """Removes the current user as follower of the given user."""
    if not g.user:
        abort(401)
    whom_id = get_user_id(username)
    if whom_id is None:
        abort(404)
    db = get_db()
    db.execute('delete from follower where who_id=? and whom_id=?',
              [session['user_id'], whom_id])
    db.commit()
    flash('You are no longer following "%s"' % username)
    return redirect(url_for('user_timeline', username=username))


@app.route('/add_message', methods=['POST'])
def add_message():
    """Registers a new message for the user."""
    if 'user_id' not in session:
        abort(401)
    if request.form['text']:
        db = get_db()
        db.execute('''insert into message (author_id, text, location, pub_date, tokens)
            values (?, ?, ?, ?, ?)''',
            (session['user_id'],
            request.form['text'],
            request.form['location'],
            int(time.time()),
            message_utils.get_message_as_token(request.form['text'])))
        db.commit()

        messages = db.execute('''select message_id from message where
            author_id = %s order by pub_date DESC LIMIT 1''' % (session['user_id']))
        message_id = messages.fetchone()[0]
        # Store hashtahgs in DB.
        hashtags = message_utils.extract_hashtags(request.form['text'])
        for hashtag in hashtags:
          db.execute('''insert into hashtag (message_id, text)
              values (?, ?)''', (int(message_id), hashtag))
          db.commit()
        flash('Your message was recorded')
    return redirect(url_for('timeline'))

@app.route('/_plus_one')
def plus_one():
    """Returns JSON response of number of upvotes."""
    message_id = int(request.args.get('message_id'))
    user_id = session['user_id']
    db = get_db()
    if message_utils.is_upvoted(db, message_id, user_id):
      message_utils.minus_one_message(db, message_id, user_id)
      status = "active"
    else:
      message_utils.plus_one_message(db, message_id, user_id)
      status = "inactive"
    return jsonify(result=len(message_utils.get_plus_ones(db, message_id)), status=status)

@app.route('/_add_comment')
def add_comment():
    """Returns JSON response of added comment."""
    message_id = int(request.args.get('message_id'))
    text = request.args.get('text')
    user_id = session['user_id']
    db = get_db()
    return jsonify(result=message_utils.make_comment(db, message_id, user_id, text))

@app.route('/_set_comments')
def set_comments():
    message_id = int(request.args.get('message_id'))
    user_id = session['user_id']
    db = get_db()
    return jsonify(result=message_utils.get_comments(db, message_id, user_id))

@app.route('/_set_status')
def set_status():
    message_id = int(request.args.get('message_id'))
    status = request.args.get('status')
    user_id = session['user_id']
    db = get_db()
    message_author = db.execute('''select * from message where author_id=%d '''% int(user_id))
    if message_author.fetchone():
      db.execute('''update message set status = "%s" where message_id = %d
          ''' % (status, int(message_id)))
      db.commit()
      return jsonify(result=status)
    else:
      if status is not 'Fixed':
        db.execute('''update message set status = "%s" where message_id = %d
          ''' % (status, int(message_id)))
        db.commit()
        return jsonify(result=status)


    return jsonify(result='')

@app.route('/_set_upvote_classes')
def set_upvote_classes():
  user_id = int(session['user_id'])
  message_id = int(request.args.get('message_id'))
  db = get_db()
  rows = db.execute('''select * from plus_one
      where user_id=%d and message_id=%d''' % (user_id, message_id))
  if rows.fetchone():
    return jsonify(result=1)
  else:
    return jsonify(result=0)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Logs the user in."""
    if g.user:
        return redirect(url_for('timeline'))
    error = None
    if request.method == 'POST':
        user = query_db('''select * from user where
            username = ?''', [request.form['username']], one=True)
        if user is None:
            error = 'Invalid username'
        elif not check_password_hash(user['pw_hash'],
                                     request.form['password']):
            error = 'Invalid password'
        else:
            flash('You are logged in')
            session['user_id'] = user['user_id']
            return redirect(url_for('timeline'))
    return render_template('login.html', error=error)


@app.route('/login-department', methods=['GET', 'POST'])
def login_department():
    """Logs the department in."""
    if g.user:
        return redirect(url_for('timeline'))
    error = None
    if request.method == 'POST':
        department = query_db('''select * from department where
            username = ?''', [request.form['username']], one=True)
        if department is None:
            error = 'Invalid username'
        elif not check_password_hash(department['pw_hash'],
                                     request.form['password']):
            error = 'Invalid password'
        else:
            flash('You are logged in')
            session['department_id'] = department['department_id']
            return redirect(url_for('timeline'))
    return render_template('login-department.html', error=error)


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Registers the user."""
    if g.user:
        return redirect(url_for('timeline'))
    error = None
    if request.method == 'POST':
        if not request.form['username']:
            error = 'You have to enter a username'
        elif not request.form['email'] or \
                 '@' not in request.form['email']:
            error = 'You have to enter a valid email address'
        elif not request.form['password']:
            error = 'You have to enter a password'
        elif request.form['password'] != request.form['password2']:
            error = 'The two passwords do not match'
        elif get_user_id(request.form['username']) is not None:
            error = 'The username is already taken'
        else:
            db = get_db()
            db.execute('''insert into user (
                username, full_name, email, birth_date, state, city, pw_hash)
                values (?, ?, ?, ?, ?, ?, ?)''',
                [request.form['username'],
                request.form['full_name'],
                request.form['email'],
                request.form['birth_date'],
                request.form['state'],
                request.form['city'],
                generate_password_hash(request.form['password'])])
            db.commit()
            user_utils.force_follow_department(db)
            flash('You were successfully registered and can login now')
            return redirect(url_for('login'))
    return render_template('register.html', error=error)


@app.route('/register-department', methods=['GET', 'POST'])
def register_department():
    """Registers a government affiliated department."""
    if g.user:
        return redirect(url_for('timeline'))
    error = None
    if request.method == 'POST':
        if not request.form['username']:
            error = 'You have to enter a username'
        elif not request.form['email'] or \
                 '@' not in request.form['email']:
            error = 'You have to enter a valid email address'
        elif not request.form['password']:
            error = 'You have to enter a password'
        elif request.form['password'] != request.form['password2']:
            error = 'The two passwords do not match'
        elif get_user_id(request.form['username']) is not None:
            error = 'The username is already taken'
        else:
            db = get_db()
            db.execute('''insert into department (
                username, email, department_name, state, city, pw_hash) values (?, ?, ?, ?, ?, ?)''',
                [request.form['username'],
                request.form['email'],
                request.form['department_name'],
                request.form['state'],
                request.form['city'],
                generate_password_hash(request.form['password'])])
            db.commit()
            user_utils.force_follow_department(db)

            department = query_db('''select * from department where
            username = ?''', [request.form['username']], one=True)

            department_utils.follow_tags(
                get_db(),
                department['department_id'], 
                request.form['follow_tags'])

            flash('''You were successfully registered. Verification is pending.
                If your email address ends in .gov or .gov.in your account will
                be automatically verified.''')
            return redirect(url_for('login_department'))
    return render_template('register-department.html', error=error)


@app.route('/search', methods=['GET'])
def search_hashtag():
  """Searches for messages containing a hashtag.
  """
  hashtag = request.args.get('hashtag')
  return render_template('timeline.html', messages=query_db('''
      select message.*, user.*, hashtag.* from message, user, hashtag
      where message.message_id = hashtag.message_id and
          user.user_id = message.author_id and
          hashtag.text = "%s"
      order by message.pub_date desc limit %d''' %
      (hashtag, PER_PAGE)))

@app.route('/search-keyword', methods=['GET'])
def search_keyword():
  """Searches for messages containing a keyword.
  """
  keyword = request.args.get('keyword')
  if keyword is None:
    pass
  messages = search_utils.get_messages_by_keyword(get_db(), keyword)
  return render_template('timeline.html', messages=messages)


@app.route('/logout')
def logout():
    """Logs the user out."""
    flash('You were logged out')
    user_type = get_user_type()
    if user_type == USERS['user']:
        session.pop('user_id', None)
    elif user_type == USERS['department']:
        session.pop('department_id', None)
    return redirect(url_for('public_timeline'))


# add some filters to jinja
app.jinja_env.filters['datetimeformat'] = format_datetime
app.jinja_env.filters['gravatar'] = gravatar_url


if __name__ == '__main__':
    init_db()
    app.run()
