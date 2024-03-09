import wtforms
from flask import Flask, render_template, session, redirect, url_for, flash, request, g
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms.validators import Length, EqualTo


class NameForm(FlaskForm):
    id = IntegerField('学号')
    name = StringField('姓名')
    birthday = StringField('出生日期')
    age = IntegerField('年龄')
    placeofbird = StringField('籍贯')
    sex = StringField('性别')
    college = StringField('学院')
    major = StringField('专业')
    submit = SubmitField('提交')


class LessonForm(FlaskForm):
    id = StringField('课程号')
    name = StringField('课程名称')
    teacher = StringField('开课教师')
    major = StringField('开课专业')
    grade = IntegerField('学分')
    submit = SubmitField('提交')


class EditForm_stu(NameForm):
    submit = SubmitField('编辑')


class EditForm_lesson(LessonForm):
    submit = SubmitField('编辑')


class EnrollCourseForm(FlaskForm):
    course_id = IntegerField('课程号',)
    submit = SubmitField('选课')


class FindStudent(FlaskForm):
    student_id = IntegerField('学号')
    submit = SubmitField('查找')


class FindCourse(FlaskForm):
    course_id = IntegerField('课程号')
    submit = SubmitField('查找')


class RegisterForm(wtforms.Form):
    id = wtforms.StringField(validators=[Length(min=8, max=8, message='管理员号格式错误')])
    psw = wtforms.StringField(validators=[Length(min=6, max=10, message='密码格式错误')])
    psw_confirm = wtforms.StringField(validators=[EqualTo('psw', message='两次密码不一致')])

    def validate_id(self, field):
        id = field.data
        user = Manager.query.filter_by(id=id).first()
        if user:
            raise wtforms.ValidationError(message='该管理员号已被注册！')


class RegisterManagerForm(wtforms.Form):
    id = wtforms.StringField(validators=[Length(min=8, max=8, message='学号格式错误')])
    psw = wtforms.StringField(validators=[Length(min=6, max=10, message='密码格式错误')])
    psw_confirm = wtforms.StringField(validators=[EqualTo('psw', message='两次密码不一致')])

    def validate_id(self, field):
        id = field.data
        user = LoginInfo.query.filter_by(id=id).first()
        if user:
            raise wtforms.ValidationError(message='该学号已被注册！')


class LoginFormChecked(wtforms.Form):
    id = wtforms.StringField(validators=[Length(min=8, max=8, message='学号格式错误')])
    psw = wtforms.StringField(validators=[Length(min=6, max=10, message='密码格式错误')])


app = Flask(__name__)
bootstrap = Bootstrap(app)
app.config['SECRET_KEY'] = 'test_secretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:djh040916@localhost:3306/students'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db = SQLAlchemy(app)


class StudentInfo(db.Model):
    __tablename__ = 'students-info'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    birthday = db.Column(db.Date)
    age = db.Column(db.Integer)
    placeofbird = db.Column(db.Text)
    sex = db.Column(db.Text)
    college = db.Column(db.Text)
    major = db.Column(db.Text)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lesson-info.id'))
    lessons = db.relationship('LessonInfo', secondary='studentlesson', backref=db.backref('students', lazy='dynamic'))


class LessonInfo(db.Model):
    __tablename__ = 'lesson-info'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    teacher = db.Column(db.Text)
    major = db.Column(db.Text)
    grade = db.Column(db.Integer)


class LoginInfo(db.Model):
    __tablename__ = 'login-info'
    id = db.Column(db.String(8), primary_key=True)
    psw = db.Column(db.Text)


class StudentLesson(db.Model):
    __tablename__ = 'studentlesson'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students-info.id'))
    lesson_id = db.Column(db.Integer, db.ForeignKey('lesson-info.id'))
    lesson = db.relationship('LessonInfo', backref=db.backref('enrollments', lazy='dynamic'))


class Manager(db.Model):
    __tablename__ = 'manager'
    id = db.Column(db.Integer, primary_key=True)
    psw = db.Column(db.String(500), nullable=False)
    user = db.Column(db.String(10), nullable=False)


with app.app_context():
    db.create_all()


@app.route('/index', methods=['GET', 'POST'])
def index():  # put application's code here
    studs = StudentInfo.query.all()
    lessons = LessonInfo.query.all()
    return render_template('index.html', studs=studs, lessons=lessons)


@app.route('/new_stud', methods=['GET', 'POST'])
def new_stud():
    form = NameForm()
    if form.validate_on_submit():
        id = form.id.data
        name = form.name.data
        sex = form.sex.data
        age = form.age.data
        birthday = form.birthday.data
        placeofbird = form.placeofbird.data
        college = form.college.data
        major = form.major.data
        student_id = StudentInfo.query.get(id)
        if student_id:
            flash('该学生已添加')
            return redirect(url_for('studentinfo'))
        else:
            newstud = StudentInfo(id=id, name=name, sex=sex, age=age, birthday=birthday, placeofbird=placeofbird, college=college, major=major)
            db.session.add(newstud)
            db.session.commit()
            flash("新增了一位学生！")
            return redirect(url_for('studentinfo'))
    return render_template('new_student.html', form=form)


@app.route('/new_lesson', methods=['GET', 'POST'])
def new_lesson():
    form = LessonForm()
    if form.validate_on_submit():
        id = form.id.data
        name = form.name.data
        teacher = form.teacher.data
        major = form.major.data
        grade = form.grade.data
        newlesson = LessonInfo(id=id, name=name, teacher=teacher, major=major, grade=grade)
        db.session.add(newlesson)
        db.session.commit()
        flash("新增了一门课程！")
        return redirect(url_for('index'))
    return render_template('new_lesson.html', form=form)


@app.route('/delete_lesson/<int:lesson_id>', methods=['GET', 'POST'])
def delete_lesson(lesson_id):
    lesson = LessonInfo.query.get(lesson_id)
    sls = StudentLesson.query.filter_by(lesson_id=lesson_id).all()
    for sl in sls:
        db.session.delete(sl)
    db.session.delete(lesson)
    db.session.commit()
    flash("删除了一条课程信息")
    return redirect(url_for('index'))


@app.route('/delete_stud/<int:stu_id>', methods=['GET', 'POST'])
def delete_stud(stu_id):
    stud = StudentInfo.query.get(stu_id)
    db.session.delete(stud)
    db.session.commit()
    flash("删除了一条学生信息")
    return redirect(url_for('studentinfo'))


@app.route('/edit_stud/<int:stu_id>', methods=['GET', 'POST'])
def edit_stud(stu_id):
    form = EditForm_stu()
    stud = StudentInfo.query.get(stu_id)
    if form.validate_on_submit():
        stud.id = form.id.data
        stud.name = form.name.data
        stud.sex = form.sex.data
        stud.age = form.age.data
        stud.birthday = form.birthday.data
        stud.placeofbird = form.placeofbird.data
        stud.college = form.college.data
        stud.major = form.major.data
        db.session.commit()
        flash("修改了一条信息")
        return redirect(url_for('studentinfo'))
    form.id.data = stud.id
    form.name.data = stud.name
    form.sex.data = stud.sex
    form.age.data = stud.age
    form.birthday.data = stud.birthday
    form.placeofbird.data = stud.placeofbird
    form.college.data = stud.college
    form.major.data = stud.major
    return render_template('edit_student.html', form=form)


@app.route('/edit_lesson/<int:lesson_id>', methods=['GET', 'POST'])
def edit_lesson(lesson_id):
    form = EditForm_lesson()
    lesson = LessonInfo.query.get(lesson_id)
    if form.validate_on_submit():
        lesson.id = form.id.data
        lesson.name = form.name.data
        lesson.teacher = form.teacher.data
        lesson.major = form.major.data
        lesson.grade = form.grade.data
        db.session.commit()
        flash("修改了一条信息")
        return redirect(url_for('index'))
    form.id.data = lesson.id
    form.name.data = lesson.name
    form.teacher.data = lesson.teacher
    form.major.data = lesson.major
    form.grade.data = lesson.grade
    return render_template('edit_lesson.html', form=form)


@app.route('/find_lesson', methods=['GET', 'POST'])
def find_lesson():
    form = FindCourse()
    course_id = form.course_id.data
    course = LessonInfo.query.get(course_id)
    if course:
        flash('查找成功', 'success')
    else:
        flash('没有该课程', 'error')
    return render_template('find_lesson.html', form=form, lesson=course)


@app.route('/find_student', methods=['GET', 'POST'])
def find_student():
    form = FindStudent()
    student_id = form.student_id.data
    student = StudentInfo.query.get(student_id)
    if student:
        flash('查找成功', 'success')
    else:
        flash('没有该学生', 'error')
    return render_template('find_student.html', form=form, student=student)


@app.route('/')
def denglu():
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return redirect('/')
    else:
        form = RegisterForm(request.form)
        if form.validate():
            id = form.id.data
            psw = form.psw.data
            registers = LoginInfo(id=id, psw=generate_password_hash(psw))
            if registers:
                flash("该学号已经注册过")
                return redirect(url_for('zhuce'))
            else:
                db.session.add(registers)
                db.session.commit()
                flash('注册成功')
                return redirect('/')
        else:
            print(form.errors)
            flash(form.errors)
            return redirect(url_for('zhuce'))


@app.route('/register_manager', methods=['GET', 'POST'])
def register_manager():
    if request.method == 'GET':
        return redirect(url_for('zhuce_manager'))
    else:
        form = RegisterManagerForm(request.form)
        if form.validate():
            id = form.id.data
            psw = form.psw.data
            registers = Manager(id=id, psw=generate_password_hash(psw))
            if registers:
                flash("该管理员已经注册过了！")
                return redirect(url_for('zhuce_manager'))
            else:
                db.session.add(registers)
                db.session.commit()
                flash('注册成功')
                return redirect('/')
        else:
            print(form.errors)
            flash(form.errors)
            return redirect(url_for('zhuce_manager'))


@app.route('/zhuce', methods=['GET', 'POST'])
def zhuce():
    return render_template('register.html')


@app.route('/zhuce_manager', methods=['GET', 'POST'])
def zhuce_manager():
    return render_template('register_manager.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return redirect('/')
    else:
        form = LoginFormChecked(request.form)
        if form.validate():
            id = form.id.data
            psw = form.psw.data
            user = LoginInfo.query.filter_by(id=id).first()
            user1 = StudentInfo.query.filter_by(id=id).first()
            if not user1:
                flash('学生尚未录入系统')
                return redirect('/')
            else:
                if not user:
                    flash('用户不存在')
                    return redirect(url_for('login'))
                if check_password_hash(user.psw, psw):
                    session['psw'] = psw
                    session['user_id'] = user.id
                    flash('登录成功')
                    return redirect(url_for('enroll_course', user_id=user.id))
                else:
                    flash('密码错误')
                    return redirect(url_for('login'))
        else:
            print(form.errors)
            return redirect(url_for('login'))


@app.before_request
def my_before_request():
    user_id = session.get('user_id')
    if user_id:
        user = LoginInfo.query.get(user_id)
        setattr(g, 'user', user)
    else:
        setattr(g, 'user', None)


@app.context_processor
def my_context_processor():
    return {"user": g.user}


@app.route('/enroll_course', methods=['GET', 'POST'])
def enroll_course():
    student_id = session.get('user_id')
    form = EnrollCourseForm()
    if form.validate_on_submit():
        course_id = form.course_id.data
        course = LessonInfo.query.get(course_id)
        if course:
            enrolled_course = StudentLesson.query.filter_by(student_id=student_id, lesson_id=course_id).first()
            if enrolled_course:
                flash('您已经选择了这门课程', 'error')
            else:
                student = StudentInfo.query.get(student_id)
                student_major = student.major
                if course.major == student_major:
                    student_lesson = StudentLesson(student_id=student_id, lesson_id=course_id)
                    db.session.add(student_lesson)
                    db.session.commit()
                    flash('选课成功', 'success')
                else:
                    flash('该课程不属于您的专业', 'error')
        else:
            flash('未找到该课程', 'error')
    selected_courses = StudentLesson.query.filter_by(student_id=student_id).all()
    total_credits = sum(course.lesson.grade for course in selected_courses)
    available_courses = LessonInfo.query.filter_by(major=StudentInfo.query.get(student_id).major).all()
    return render_template('enroll_course.html', form=form, selected_courses=selected_courses, total_credits=total_credits, available_courses=available_courses)


@app.route('/delete_enrollment/<int:id>', methods=['GET', 'POST'])
def delete_enrollment(id):
    enrollment_to_delete = StudentLesson.query.get(id)
    if enrollment_to_delete:
        db.session.delete(enrollment_to_delete)
        db.session.commit()
        flash("退课成功")
    else:
        flash("未找到要退课的选课记录")
    return redirect(url_for('enroll_course'))


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'GET':
        return redirect('/manager_html')
    else:
        form = LoginFormChecked(request.form)
        if form.validate():
            id = form.id.data
            psw = form.psw.data
            manager = Manager.query.filter_by(id=id).first()
            if not manager:
                flash('用户不存在')
                return redirect('/manager_html')
            if check_password_hash(manager.psw, psw):
                session['psw'] = psw
                return render_template('admin.html', current_user=manager)
            else:
                flash('密码错误')
                return redirect('/manager_html')
        else:
            print(form.errors)
            return redirect('/manager_html')


@app.route('/admin/<int:manager_id>', methods=['GET', 'POST'])
def admin2(manager_id):
    manager = Manager.query.get(manager_id)
    return render_template('admin.html', current_user=manager)


@app.route('/manager_html')
def manager_html():
    return render_template('manager_login.html')


@app.route('/admin/studentinfo')
def studentinfo():
    studs = StudentInfo.query.all()
    return render_template('studentinfo.html', studs=studs)


if __name__ == '__main__':
    app.run(debug=True)
