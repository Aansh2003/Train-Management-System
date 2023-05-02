from flask import Flask, render_template, request, redirect, url_for, session,render_template_string
from trainmanagement import TrainData
from bs4 import BeautifulSoup

app = Flask(__name__)
app.secret_key = 'your_secret_key'

login_det = {'admin': 'admin'}
print(list(login_det.keys()))
logged_in = []

filehtml = 'templates/home.html'

with open(filehtml) as file:
    htmlFile = file.read()
    soup2 = BeautifulSoup(htmlFile,features="lxml")

filehtml2 = 'templates/employee_home.html'

with open(filehtml2) as file:
    htmlFile = file.read()
    soup3 = BeautifulSoup(htmlFile,features="lxml")

my_db = TrainData('ruru','password','localhost')
schedule_id = []

filehtml3 = 'templates/cust_schedules.html'

with open(filehtml3) as file:
    htmlFile = file.read()
    soup5 = BeautifulSoup(htmlFile,features="lxml")

@app.route('/', methods=['GET'])
def home():
    if 'username' in session:
        print(session['username'])
        my_string = str(soup2)
        soup = BeautifulSoup(my_string)
        head = soup.find("container2")
        l = my_db.get_user_booking_details(session['username'])
        print(l)
        if len(l)==0:
            message = "No bookings yet."
            print(message)
            return render_template('home.html', username=session['username'],info=message)
        else:
            for value in l:
                new_p = soup.new_tag("p",**{'class':'back'})
                new_p1 = soup.new_tag("p",**{'class':'booking'})
                new_p1.string = "Scheduled ID:"+str(value[0])+" Train ID:"+str(value[5])
                new_p2 = soup.new_tag("p",**{'class':'booking'})
                new_p2.string = "Start:"+str(value[6])+" End:"+str(value[7])
                new_p.append(new_p1)
                new_p.append(new_p2)
                head.append(new_p)
            return render_template_string(str(soup),username=session['username'])
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        out = my_db.get_user_password(username)
        print(out)
        if out == False:
            return render_template('login.html',error='Invalid username or password.')
        elif out != password:
            return render_template('login.html',error='Invalid username or password.')
        else:
            session['username'] = username
            return redirect(url_for('home'))
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        fname = request.form['fname']
        sname = request.form['sname']
        phone = request.form['phone']
        sex = request.form['gender']
        if sex == 0:
            gender = 'M'
        elif sex == 1:
            gender = 'F'
        else:
            gender = 'O'
        password = request.form['password']
        out = my_db.set_user_data(username,password,fname,sname,email,phone,gender)
        print(out)
        if out != 1:
            return render_template('register.html',error='Invalid details')
        print('Succesfully registered'+username)
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/emp_home')
def emp_home():
    if 'username' in session:
        print(session['username'])
        my_string = str(soup3)
        soup4 = BeautifulSoup(my_string)
        head = soup4.find("container2")
        l = my_db.get_scheduled_train_details()
        print(l)
        if len(l)==0:
            message = "No Schedules yet."
            print(message)
            return render_template('employee_home.html', username=session['username'],info=message)
        else:
            for value in l:
                new_p = soup4.new_tag("p",**{'class':'back'})
                new_p1 = soup4.new_tag("p",**{'class':'booking'})
                new_p1.string = "Scheduled ID:"+str(value[1])+" Train ID:"+str(value[0])+" Free: "+str(value[4])+'|'+str(value[6])
                new_p2 = soup4.new_tag("p",**{'class':'booking'})
                new_p2.string = "Start:"+str(value[9])
                new_p3 = soup4.new_tag("p",**{'class':'booking'})
                new_p3.string = "End:"+str(value[10])
                new_p.append(new_p1)
                new_p.append(new_p2)
                new_p.append(new_p3)
                head.append(new_p)
            return render_template_string(str(soup4),username=session['username'])
    return redirect(url_for('emp_login'))

@app.route('/emp_login', methods=['GET', 'POST'])
def emp_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        out = my_db.get_employee_password(username)
        print(out)
        if out == False:
            return render_template('employee_login.html',error='Invalid username or password.')
        elif out != password:
            return render_template('employee_login.html',error='Invalid username or password.')
        else:
            session['username'] = username
            return redirect(url_for('emp_home'))
    return render_template('employee_login.html')

@app.route('/book', methods=['GET', 'POST'])
def book():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['number']
        trav_from = request.form['start_loc']
        trav_to = request.form['end_loc']
        date = request.form['date']
        no_adults = request.form['adult']
        no_children = request.form['children']
        no_infants = request.form['infant']
        my_list = my_db.get_scheduled_train_details(date,trav_from,trav_to)
        names = []
        if len(my_list)==0:
            error = 'No train found'
            return render_template('booking-form.html',error=error)
        elif len(my_list)>=1:
            names.append(my_list[0][8])
            scheduled_id = my_list[0][1]
            if my_db.check_seat_availibility(scheduled_id):
                if my_db.book_scheduled_train(scheduled_id,session['username'],no_adults,no_children) != False:
                    message = no_adults+' ac tickets and '+no_children+' non-AC tickets booked.'
                    return render_template('booking-form.html',message=message)
                else:
                    error = 'Train full.'
                    return render_template('booking-form.html',error=error)
    return render_template('booking-form.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/emp_logout')
def emp_logout():
    session.pop('username', None)
    return redirect(url_for('emp_login'))

@app.route('/manage',methods=['GET', 'POST'])
def manage():
    if request.method == 'POST':
        id = request.form['schedule']
        print(id)
        num = my_db.check_seat_availibility(id)
        if type(num) == type(True):
            message = "Not found"
            return render_template('manage.html',error=message)
        message = 'Booked seats - Non-AC:'+str(num[0])+'  AC:'+str(num[1])
        return render_template('manage.html',info=message)
    return render_template('manage.html')

@app.route('/contus')
def about():
    return render_template('contus.html')

@app.route('/emp_reg',methods=['POST','GET'])
def reg():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        fname = request.form['fname']
        sname = request.form['sname']
        phone = request.form['phone']
        sex = request.form['gender']
        if sex == 0:
            gender = 'M'
        elif sex == 1:
            gender = 'F'
        else:
            gender = 'O'
        password = request.form['password']
        out = my_db.set_employee_data(username,password,fname,sname,email,phone,gender)
        print(out)
        if out != 1:
            return render_template('register.html',error='Invalid details')
        print('Succesfully registered'+username)
        return redirect(url_for('emp_login'))
    return render_template('emp_reg.html')

@app.route('/schedule',methods=['POST','GET'])
def schedule():
    if request.method == 'POST':
        trainID = request.form['trainID']
        start = request.form['start']
        end = request.form['end']
        schedule_id = my_db.schedule_train(trainID,start,end)
        if type(schedule_id) == type(1):
            message = 'Scheduled ID:'+str(schedule_id)
            return render_template('schedule.html',message=message)
        else:
            message = 'Invalid input'
            return render_template('schedule.html',error=message)
    return render_template('schedule.html')

@app.route('/remove',methods=['POST','GET'])
def remove():
    if request.method == 'POST':
        id = request.form['schedule']
        num = my_db.check_seat_availibility(id)
        message = 'Booked seats - Non-AC:'+str(num[0])+'  AC:'+str(num[1])
        return render_template('remove.html',info=message)
    return render_template('remove.html')

@app.route('/sched')
def sched():
    my_string = str(soup5)
    soup6 = BeautifulSoup(my_string)
    head = soup6.find("container2")
    print(head)
    l = my_db.get_scheduled_train_details()
    print(l)
    if len(l)==0:
        message = "No Schedules yet."
        print(message)
        return render_template_string(str(soup6),username=session['username'],info=message)
    else:
        for value in l:
            new_p = soup6.new_tag("p",**{'class':'back'})
            new_p1 = soup6.new_tag("p",**{'class':'booking'})
            new_p1.string = "Scheduled ID:"+str(value[1])+" Train ID:"+str(value[0])+" Free: "+str(value[4])+'|'+str(value[6])
            new_p2 = soup6.new_tag("p",**{'class':'booking'})
            new_p2.string = "Start:"+str(value[9])
            new_p3 = soup6.new_tag("p",**{'class':'booking'})
            new_p3.string = "End:"+str(value[10])
            new_p.append(new_p1)
            new_p.append(new_p2)
            new_p.append(new_p3)
            head.append(new_p)
        return render_template_string(str(soup6),username=session['username'])

if __name__ == '__main__':
    app.run(host="0.0.0.0",debug=True)
