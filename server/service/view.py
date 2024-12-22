from flask import render_template

from service import app
import bili


@app.route('/')
def mainPage():
    return render_template('base.html', homepage=True)


@app.route('/verify')
def verifyPage():
    return render_template('verify.html', **{
        'botUid': bili.selfUid,
        'botName': bili.selfName,
    })


@app.route('/oauth/authorize')
def oauthAuthorizePage():
    return render_template('authorize.html')


@app.route('/user')
def userPage():
	return render_template('user.html')


@app.route('/oauth/application/new')
def appCreatePage():
	return render_template('create_app.html')
