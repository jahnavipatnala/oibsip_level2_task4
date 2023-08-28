from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mail import Mail, Message
import secrets
import string

app = Flask(__name__)
app = Flask(__name__, static_folder='static')

app.config['MAIL_SERVER'] = 'smtp.example.com'  
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'your_username'
app.config['MAIL_PASSWORD'] = 'your_password'
mail = Mail(app)

valid_credentials = {}
reset_tokens = {}

def generate_token(length=32):
    token = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(length))
    return token

def send_reset_email(email, token):
    msg = Message('Password Reset', sender='noreply@example.com', recipients=[email])
    msg.body = f"Click the following link to reset your password: {url_for('reset_password', token=token, _external=True)}"
    mail.send(msg)

def get_email_from_token(token):
    for email, t in reset_tokens.items():
        if t == token:
            return email
    return None

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if valid_credentials.get(username) == password:
            return 'Login successful. Welcome, {}!'.format(username)
        else:
            return 'Invalid credentials. Please try again.'
    return render_template('login.html')
    pass

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        valid_credentials[username] = password
        return redirect(url_for('login'))
    return render_template('register.html')
    pass

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        if email in valid_credentials:
            token = generate_token()
            reset_tokens[email] = token
            send_reset_email(email, token)
            flash('A password reset email has been sent to your email address.')
            return redirect(url_for('login'))
    return render_template('forgot_password.html')

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if request.method == 'POST':
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']
        if new_password == confirm_password:
            email = get_email_from_token(token)
            if email and email in valid_credentials:
                valid_credentials[email] = new_password
                flash('Password reset successful. You can now log in with your new password.')
                return redirect(url_for('login'))
            else:
                flash('Invalid token.')
    return render_template('reset_password.html', token=token)

if __name__ == '__main__':
    app.run(debug=True)
