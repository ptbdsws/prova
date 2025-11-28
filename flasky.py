from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired
from flask import Flask, render_template, session, redirect, url_for, flash
from flask_moment import Moment
from flask_bootstrap import Bootstrap
from flask_migrate import Migrate
from datetime import datetime
import os
from flask_sqlalchemy import SQLAlchemy

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'chave secreta'
app.config['SQLALCHEMY_DATABASE_URI'] =\
    'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
bootstrap = Bootstrap(app)
moment = Moment(app)
migrate = Migrate(app, db)

class Course(db.Model):
    __tablename__ = 'courses'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, index=True)
    description = db.Column(db.String(250))

    def __repr__(self):
        return '<Course %r>' % self.name

class CourseForm(FlaskForm):
    name = StringField('Qual é o nome do curso?', validators=[DataRequired()])
    description = TextAreaField('Descrição (250 caracteres)', validators=[DataRequired()]) 
    submit = SubmitField('Cadastrar')

@app.shell_context_processor
def make_shell_context():
    return dict(db=db, Course=Course)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', current_time=datetime.utcnow()), 404

@app.route('/', methods=['GET', 'POST'])
def main():
    return render_template('main_menu.html', current_time=datetime.utcnow())

@app.route('/cursos', methods=['GET', 'POST'])
def aluno():
    form = CourseForm()
    if form.validate_on_submit():
        course = Course.query.filter_by(name=form.name.data).first()
        
        if course is None:
            course = Course(name=form.name.data, description=form.description.data)
            db.session.add(course)
            db.session.commit()
            session['known'] = False
        else:
            session['known'] = True
            
        session['name'] = form.name.data
        return redirect(url_for('aluno'))

    courses_list = Course.query.order_by(Course.name).all()
    
    return render_template('index.html', 
                           form=form, 
                           name=session.get('name'), 
                           known=session.get('known', False), 
                           courses=courses_list)

if __name__ == "__main__":

    app.run(debug=True)
