import pytz
from flask import Flask, request, render_template, redirect, url_for, abort, flash, Response, jsonify
import json
# If in branch use the following
# from .DBFunc import *
# If in main use the following
from DBFunc import *

app = Flask(__name__)
# NOTE: added for flush() usage
app.secret_key = "admin"


@app.route('/')
def index():
    """The index root directory of this website"""
    return redirect(url_for('home'))


@app.route('/home')
def home():
    """The home page of the website
    Shows recomendations based on the user profile or if not authenticated the most upvoted

    Also the end point of the search function where the search is a get method
    """
    name = "Example User"
    if 'x-kvd-payload' in request.headers:
        userjson = request.headers['x-kvd-payload']
        user = json.loads(userjson)
        name = user['user']

    data = [
        {
            'title': "Example 1",
            'img': url_for('static', filename='img/placeholder.png')
        }, {
            'title': "Example 2",
            'img': url_for('static', filename='img/placeholder.png')
        }, {
            'title': "Example 3",
            'img': url_for('static', filename='img/placeholder.png')
        }, {
            'title': "Example 4",
            'img': url_for('static', filename='img/placeholder.png')
        }, {
            'title': "Example 5",
            'img': url_for('static', filename='img/placeholder.png')
        }
    ]

    return render_template('home.html', title='Home', name=name, data=data)


@app.route('/resource')
@app.route('/resource/<int:uid>/<int:rid>', methods=["GET", "POST"])
def resource(uid=None, rid=None):
    """Page for a resource

    Shows information based on the resource type and content

    :param uid: The user id
    :param rid: The resource id
    If resource or user is invalid then redirect to 404 page
    """
    if (uid is None and rid is not None) or (uid is not None and rid is None):
        redirect(url_for('resource'))  # base resource page
    if uid is None or rid is None:
        return render_template('resource.html',
                               title='Resources',
                               subject=[enum_to_website_output(e) for e in Subject],
                               grade=[enum_to_website_output(e) for e in Grade],
                               tag=get_tags().keys(),
                               resources=find_resources())
    # individual resource page
    user, res = get_user_and_resource_instance(uid=uid, rid=rid)
    if not user or not res:
        # invalid user or resource, pop 404
        abort(404, description="Invalid user or resource id")
        # return redirect(url_for('home'))
    # elif is_user_session_expired(uid=uid):
    #     # user instance is expired, go back to login
    #     return redirect(url_for("login"))
    elif not is_resource_public(rid=rid) and not user_has_access_to_resource(uid=uid, rid=rid):
        # resource is private and user does not have access
        # todo: possibly a link to no access reminder page?
        abort(404, description=f"User {uid} does not have access to resource {rid}")

    if request.method == "GET":
        # show resource detail

        # convert to human readable form
        subject = enum_to_website_output(res.subject)
        grade = enum_to_website_output(res.grade)
        difficulty = enum_to_website_output(res.difficulty)

        # convert utc time to AEST
        created_at = res.created_at.astimezone(pytz.timezone("Australia/Brisbane"))

        # get a list of resource_comment objects
        resource_comment_list = get_resource_comments(rid=rid)
        # get a dict of resource_comment instance -> resource_comment_replies instances to that comment
        resource_comment_replies_list = get_resource_comment_replies(resource_comment_list)

        # FIXME: modify "base.html" webpage to resource page
        return render_template("resource_item.html", rid=rid, uid=uid,
                               res=res, difficulty=difficulty, subject=subject, grade=grade)
    elif request.method == "POST":
        # FIXME: here assume upvote and downvote are two separate buttons like Quora
        # example see https://predictivehacks.com/?all-tips=how-to-add-action-buttons-in-flask
        # update do upvote/downvote
        up, down = request.form.get("upvote"), request.form.get("downvote")
        vote_res = vote_resource(uid=uid, rid=rid, upvote=up is not None)
        if vote_res == ErrorCode.SAME_VOTE_TWICE:
            # the user voted the same vote twice
            # todo: here I do flash message, you can modify it
            flash("Oh please don't vote the same thing twice, will ya?")

        # reach here a vote is made or vote is invalid, now refresh resource page
        return redirect(url_for("resource", uid=uid, rid=rid))
    return render_template('base.html', title='Register')


@app.route('/search')
def search():
    title = request.args.get('title')
    return jsonify([i.serialize for i in find_resources(title=title)])
    # return Response(json.dumps([i.serialize for i in find_resources(title=title)]),  mimetype='application/json')


@app.route('/register')
def register():
    """Page for a user to register for an account

    Must provide: username, email, password (with conditions)

    Optionally provide: interests / subjects tags

    Other user fields are configured in profile()
    """
<<<<<<< HEAD
    return render_template('base.html', title='Register')
=======
    #emailInvalid, passwordDifferent, passwordInvalid = false, false, false
    """
    if (request.method == "GET"):
        emailInvalid = request.args.get("emailValid")
        passwordInvalid = request.args.get("passwordInvalid")
        passwordDifferent = request.args.get("passwordDifferent")
    """
    return render_template('register.html', title='Register')

@app.route('/register/create',  methods=["POST"])
def create_account():
    #Do backend stuff maybe?

    #Extra details page
    redirect(url_for('home'))

@app.route('/register/finalise', methods=["POST"])
def finalise_account():
    #do stuff

    #all backend stuff on this function
    redirect(url_for('home'))
>>>>>>> eec7564... About page can have code in each FAQ. FAQ's are provided by controller.py


@app.route('/login')
def login():
    """Login page for a user to authenticate

    Asks for the users email and password.

    Gives feedback on fail, redirects to referring page on success
     (through post data), if not refered then home page
    """
    return render_template('base.html', title='Login')


@app.route('/profile')
def profile():
    """The default view of a users profile,
    this can be used to view your own or other users profiles.
    Specified with the GET request
    /profile?<id / name>

    Shows the following content:
        Liked resources
        Created resources
        Your reviews / comments

    Additional options are available if viewing your own profile:
        Manage account settings
        Forums you are a part of
    """
    return render_template('base.html', title='Login')


@app.route('/profile/settings')
def settings():
    """The user configuration page,
    allows the user to edit their:
        Bio.
        Email.
        Password.
        Avatar.
        Interests
    """
    return render_template('base.html', title='Login')


@app.route('/about')
def about():
    """A brief page descibing what the website is about"""
    #FAQs can contain html code to run on page
    faqs = [
        ["How do I save this page","Saving has been a super useful mechanic in many different areas of software for years. It is most commonly done by using the shortcut <kbd>Ctrl + S</kbd>, and our page is no exception."],
        ["Can you talk like a computer?","Yeah Sure <br> <samp> Beep Boop Beep Beep Boop </samp>"],
        ["What is Lorem Ipsum?","Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum."],
        ["Can I type maths?", "Yes, yes you can. You can find <var>x</var> as much as you like."],
        ["Can I do my own HTML markup?", "Only in some <code>&lt;input&gt;</code> areas"]
    ]
    return render_template('about.html', title='About Us', name="About Us", faqs=faqs, num=len(faqs))


@app.route('/create')
@app.route('/create/<type>')
def create(type=None):
    """The user create a resource or channel

    If type is not resource or channel redirect to home

    If type == None then prompt the user to select which create type they want
    and redirect to that page


    Create Channel
    Allows the user to give a title, desc., tags

    Create resource
    Allows the user to give a title, desc., tags, upload content, link to similar
    """
    return render_template('base.html', title='Post')

@app.route('/forum')
@app.route('/forum/<fName>/<tName>')
def forum(fName=None, tName=None):
    """The user view a forum page

    The home forum page (fName == None, tName == None) shows the list of forums
    Allows user to create a channel etc.

    The forum/fName page shows the threads in that forum
    Allows users to add threads to the forum

    The forum/fName/tName shows the thread on that forum.
    Allows users to add comments to the forum post

    The forum/fName/tName?<id> shows the comment on that forum page or the top
    of page if not valid.

    If fName is not valid name redirect to home forum page
    If tName is not valid redirect to forum page
    """
    return render_template('base.html', title='Post')


@app.errorhandler(403)
def page_not_found(error):
    """Page shown with a HTML 403 status"""
    return render_template('errors/error_403.html'), 403


@app.errorhandler(404)
def page_not_found(error):
    """Page shown with a HTML 404 status"""
    return render_template('errors/error_404.html'), 404
