from flask import Flask, request, jsonify, render_template
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
from flask_bcrypt import Bcrypt
from flask_mail import Mail, Message
from models import get_user_by_username, get_user_by_email, add_user
import uuid

app = Flask(__name__)
app.config.from_object('config.Config')

jwt = JWTManager(app)
bcrypt = Bcrypt(app)
mail = Mail(app)

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = bcrypt.generate_password_hash(data.get('password')).decode('utf-8')

    if get_user_by_username(username) or get_user_by_email(email):
        return jsonify({"msg": "User already exists"}), 400

    add_user(username, email, password)
    return jsonify({"msg": "User registered successfully"}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = get_user_by_username(username)
    if user and bcrypt.check_password_hash(user[3], password):
        access_token = create_access_token(identity=username)
        return jsonify(access_token=access_token), 200

    return jsonify({"msg": "Bad username or password"}), 401

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        user = get_user_by_email(email)

        if user:
            reset_token = str(uuid.uuid4())
            cur = mysql.connection.cursor()
            cur.execute("UPDATE users SET reset_token = %s WHERE email = %s", (reset_token, email))
            mysql.connection.commit()
            cur.close()

            reset_link = f'http://localhost:5000/reset_password/{reset_token}'
            msg = Message('Password Reset Request', sender='noreply@example.com', recipients=[email])
            msg.body = f'To reset your password, visit the following link: {reset_link}'
            mail.send(msg)

            return jsonify({"msg": "Password reset email sent"}), 200

        return jsonify({"msg": "Email not found"}), 404

    return render_template('forgot_password.html')

@app.route('/reset_password/<reset_token>', methods=['GET', 'POST'])
def reset_password(reset_token):
    if request.method == 'POST':
        new_password = request.form.get('password')
        hashed_password = bcrypt.generate_password_hash(new_password).decode('utf-8')

        cur = mysql.connection.cursor()
        cur.execute("UPDATE users SET password = %s, reset_token = NULL WHERE reset_token = %s", (hashed_password, reset_token))
        mysql.connection.commit()
        cur.close()

        return jsonify({"msg": "Password has been reset"}), 200

    return '''
        <form method="POST">
            <input type="password" name="password" placeholder="New Password" required>
            <input type="submit" value="Reset Password">
        </form>
    '''

if __name__ == '__main__':
    app.run(debug=True)
