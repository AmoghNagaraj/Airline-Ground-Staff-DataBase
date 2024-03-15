from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL

app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'My$QL625'
app.config['MYSQL_DB'] = 'airline_ground_staff_db'
mysql = MySQL(app)

app.secret_key = 'your_secret_key'


@app.route('/')
def home():
    return redirect(url_for('login'))


@app.before_request
def require_login():
    allowed_routes = ['login', 'logout']
    if request.endpoint not in allowed_routes and 'staff_name' not in session:
        return redirect('/login')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        staff_name = request.form['staff_name']
        id_number = request.form['id_number']
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM ground_staff WHERE staff_name = %s AND id_number = %s", (staff_name, id_number))
        user = cur.fetchone()
        if user:
            session['staff_name'] = staff_name
            return redirect(url_for('index'))
        else:
            return 'Error: Invalid login credentials'
    return render_template('login.html')


@app.route('/index', methods=['GET'])
def index():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM flights")
    flights = cur.fetchall()
    cur.close()
    return render_template('index2.html', flights=flights)


@app.route('/add_flight', methods=['POST'])
def add_flight():
    if request.method == 'POST':
        flight_number = request.form['flight_number']
        origin = request.form['origin']
        destination = request.form['destination']
        departure_time = request.form['departure_time']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO flights (flight_number, origin, destination, departure_time) VALUES (%s, %s, %s, %s)",
                    (flight_number, origin, destination, departure_time))
        mysql.connection.commit()
        cur.close()
    return redirect(url_for('index'))


@app.route('/del_flight/<string:flight_number>', methods=['GET', 'POST'])
def del_flight(flight_number):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM flights WHERE flight_number = %s", [flight_number])
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('index'))


@app.route('/logout', methods=['POST'])
def logout():
    session.pop('staff_name', None)
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
