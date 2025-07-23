# The primary goal of this work is to build up a Model of Skin Cancer Detection System utilizing Machine Learning Algorithms. After experimenting with many different architectures for the CNN model It is found that adding the BatchNormalization layer after each Dense, and MaxPooling2D layer can help increase the validation accuracy. In future, a mobile application can be made.
from flask import Flask, request, render_template
from PIL import Image
import numpy as np
import skin_cancer_detection as SCD
from flask import Flask, request, render_template, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash

import string, random

import sqlite3
import os

print("Templates folder contents:", os.listdir("templates"))

app = Flask(__name__)


app.secret_key = os.environ.get("SECRET_KEY", os.urandom(24))

import sqlite3
import os
def init_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    ''')

    cursor.execute("PRAGMA table_info(users)")
    columns = [col[1] for col in cursor.fetchall()]
    if "profile_image" not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN profile_image TEXT")

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            image_path TEXT,
            prediction TEXT,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    conn.commit()
    conn.close()
    print("✔ Tables created or already exist.")



    #profile
import os
import sqlite3

from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash

UPLOAD_FOLDER = 'static/profile_images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
#profile   
import os
import sqlite3
from flask import Flask, request, session, redirect, render_template
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Replace this with a secure key!

#profile
@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'email' not in session:
        return redirect('/login')

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    user = cursor.execute("SELECT * FROM users WHERE email=?", (session['email'],)).fetchone()
    if not user:
        return "❌ User not found"

    message = ""

    if request.method == 'POST':
        new_username = request.form['username']
        new_email = request.form['email']
        old_password = request.form['old_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']

        if not check_password_hash(user[3], old_password):
            message = "⚠️ Old password is incorrect"
        elif new_password != confirm_password:
            message = "⚠️ New passwords do not match"
        else:
            try:
                hashed_password = generate_password_hash(new_password)
                cursor.execute("""
                    UPDATE users 
                    SET username=?, email=?, password=?
                    WHERE email=?
                """, (new_username, new_email, hashed_password, session['email']))
                conn.commit()
                session['email'] = new_email
                session['username'] = new_username
                message = "✅ Profile updated successfully!"

                user = cursor.execute("SELECT * FROM users WHERE email=?", (new_email,)).fetchone()
            except sqlite3.IntegrityError:
                message = "⚠️ Username or email already taken"

    conn.close()
    return render_template('profile.html', user=user, message=message)






# signup
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        # ✅ Add this check right here:
        if len(password) < 6:
            return "❌ Password too short. <a href='/signup'>Try again</a>"

        hashed_password = generate_password_hash(password)

        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                       (username, email, hashed_password))
        conn.commit()
        conn.close()
        return redirect(url_for("login"))
    
    return render_template("signup.html")

# login

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM users WHERE email = ?", (email,))
        result = cursor.fetchone()

        if result and check_password_hash(result[0], password):
            # Get the username from the email
            cursor.execute("SELECT username FROM users WHERE email = ?", (email,))
            username = cursor.fetchone()[0]
            conn.close()

            # Save both email and username in session
            session["email"] = email
            session["username"] = username
            return redirect(url_for("home"))

        conn.close()
        return "Invalid credentials. <a href='/login'>Try again</a>"

    return render_template("login.html")


#logout
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

app.config['DEBUG'] = True

    
    
#resource
@app.route("/resource")
def resource():
    return render_template("resource.html")

#about
@app.route('/about')
def about():
    return render_template('about.html')

#route
@app.route("/")
def root():
    return redirect(url_for("home"))

#run home
@app.route("/home")
def home():
    if "username" not in session:
        return redirect(url_for("login"))
    return render_template("home.html")

#mail configuration 
from flask_mail import Mail, Message

# Mail Configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'ma4676866@gmail.com'     # your email
app.config['MAIL_PASSWORD'] = 'sznmwatlrnocdsfq'         # Gmail app password (not your normal password)

mail = Mail(app)

#forgot password
@app.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form["email"]

        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()

        if user:
            # ✅ Generate random password
            new_password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))

            # ✅ Hash the new password
            hashed_password = generate_password_hash(new_password)

            # ✅ Update in database
            cursor.execute("UPDATE users SET password = ? WHERE email = ?", (hashed_password, email))
            conn.commit()
            conn.close()

            # ✅ Send email
            msg = Message("Your New Password", sender="ma4676866@gmail.com", recipients=[email])
            msg.body = f"Hello,\n\nYour new password is: {new_password}\n\nPlease login and change it."
            mail.send(msg)

            return "✅ New password has been sent to your email."
        else:
            conn.close()
            return "❌ Email not found in database."

    return render_template("forgot_password.html")



#contact
@app.route('/contact')
def contact():
    return render_template("contact.html")

# The primary goal of this work is to build up a Model of Skin Cancer Detection System utilizing Machine Learning Algorithms. After experimenting with many different architectures for the CNN model It is found that adding the BatchNormalization layer after each Dense, and MaxPooling2D layer can help increase the validation accuracy. In future, a mobile application can be made.

#history
@app.route("/history")
def history():
    if "username" not in session:
        return redirect(url_for("login"))

    username = session["username"]
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    user_id = cursor.fetchone()[0]
    cursor.execute("SELECT prediction, date FROM history WHERE user_id = ? ORDER BY date DESC LIMIT 3", (user_id,))
    records = cursor.fetchall()
    conn.close()

    return render_template("history.html", records=records)



@app.route("/showresult", methods=["GET", "POST"])
def show():
    if "username" not in session:
        return redirect(url_for("login"))

    pic = request.files["pic"]
    inputimg = Image.open(pic).convert("RGB")
    inputimg = inputimg.resize((28, 28))
    img = np.array(inputimg).reshape(-1, 28, 28, 3).astype('float32') / 255.0

    model = SCD.get_model()
    result = model.predict(img)
    result = result.tolist()
    max_prob = max(result[0])
    class_ind = result[0].index(max_prob)
    result_label = SCD.classes[class_ind]
    




    if class_ind == 0:
        info = "Actinic keratosis also known as solar keratosis or senile keratosis are names given to intraepithelial keratinocyte dysplasia. As such they are a pre-malignant lesion or in situ squamous cell carcinomas and thus a malignant lesion."

    elif class_ind == 1:
        info = "Basal cell carcinoma is a type of skin cancer. Basal cell carcinoma begins in the basal cells — a type of cell within the skin that produces new skin cells as old ones die off.Basal cell carcinoma often appears as a slightly transparent bump on the skin, though it can take other forms. Basal cell carcinoma occurs most often on areas of the skin that are exposed to the sun, such as your head and neck"
    elif class_ind == 2:
        info = "Benign lichenoid keratosis (BLK) usually presents as a solitary lesion that occurs predominantly on the trunk and upper extremities in middle-aged women. The pathogenesis of BLK is unclear; however, it has been suggested that BLK may be associated with the inflammatory stage of regressing solar lentigo (SL)1"
    elif class_ind == 3:
        info = "Dermatofibromas are small, noncancerous (benign) skin growths that can develop anywhere on the body but most often appear on the lower legs, upper arms or upper back. These nodules are common in adults but are rare in children. They can be pink, gray, red or brown in color and may change color over the years. They are firm and often feel like a stone under the skin. "
    elif class_ind == 4:
        info = "A melanocytic nevus (also known as nevocytic nevus, nevus-cell nevus and commonly as a mole) is a type of melanocytic tumor that contains nevus cells. Some sources equate the term mole with ‘melanocytic nevus’, but there are also sources that equate the term mole with any nevus form."
    elif class_ind == 5:
        info = "Pyogenic granulomas are skin growths that are small, round, and usually bloody red in color. They tend to bleed because they contain a large number of blood vessels. They’re also known as lobular capillary hemangioma or granuloma telangiectaticum."
    elif class_ind == 6:
        info = "Melanoma, the most serious type of skin cancer, develops in the cells (melanocytes) that produce melanin — the pigment that gives your skin its color. Melanoma can also form in your eyes and, rarely, inside your body, such as in your nose or throat. The exact cause of all melanomas isn't clear, but exposure to ultraviolet (UV) radiation from sunlight or tanning lamps and beds increases your risk of developing melanoma."
    elif class_ind == 7:
        info = "its not a cancer image please choose correct image "
    if class_ind in range(0, 7):
        username = session["username"]
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        user_id = cursor.fetchone()[0]
        cursor.execute("INSERT INTO history (user_id, prediction) VALUES (?, ?)", (user_id, result_label))
        conn.commit()
        conn.close()

    return render_template("result.html", result=result_label, info=info)

    


#if __name__ == "__main__":
   # from waitress import serve
    #print(" Starting production server with Waitress...")
   # serve(app, host="0.0.0.0", port=5000)

    # Start app
if __name__ == "__main__":
    init_db()
    app.run(debug=True)



# The primary goal of this work is to build up a Model of Skin Cancer Detection System utilizing Machine Learning Algorithms. After experimenting with many different architectures for the CNN model It is found that adding the BatchNormalization layer after each Dense, and MaxPooling2D layer can help increase the validation accuracy. In future, a mobile application can be made.

# The primary goal of this work is to build up a Model of Skin Cancer Detection System utilizing Machine Learning Algorithms. After experimenting with many different architectures for the CNN model It is found that adding the BatchNormalization layer after each Dense, and MaxPooling2D layer can help increase the validation accuracy. In future, a mobile application can be made.
