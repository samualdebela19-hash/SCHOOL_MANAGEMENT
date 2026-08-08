from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, IntegerField, DateField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional, NumberRange

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=50)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


class StudentForm(FlaskForm):
    student_id = StringField('Student ID', validators=[DataRequired(), Length(max=20)])
    full_name = StringField('Full Name', validators=[DataRequired(), Length(max=100)])
    grade = StringField('Grade', validators=[Optional(), Length(max=10)])
    section = StringField('Section', validators=[Optional(), Length(max=10)])
    gender = SelectField('Gender', choices=[('', 'Select'), ('Male', 'Male'), ('Female', 'Female')], validators=[Optional()])
    phone = StringField('Phone', validators=[Optional(), Length(max=20)])
    submit = SubmitField('Save Student')


class AttendanceForm(FlaskForm):
    student_id = SelectField('Student', coerce=int, validators=[DataRequired()])
    date = DateField('Date', validators=[DataRequired()])
    status = SelectField('Status', choices=[('Present', 'Present'), ('Absent', 'Absent'), ('Late', 'Late')], validators=[DataRequired()])
    submit = SubmitField('Record Attendance')


class InventoryForm(FlaskForm):
    item_name = StringField('Item Name', validators=[DataRequired(), Length(max=100)])
    quantity = IntegerField('Quantity', validators=[DataRequired(), NumberRange(min=0)])
    description = TextAreaField('Description', validators=[Optional()])
    submit = SubmitField('Save Item')


class LoanForm(FlaskForm):
    student_id = SelectField('Student', coerce=int, validators=[DataRequired()])
    item_id = SelectField('Item', coerce=int, validators=[DataRequired()])
    borrowed_date = DateField('Borrowed Date', validators=[DataRequired()])
    submit = SubmitField('Issue Item')


class ReturnForm(FlaskForm):
    return_date = DateField('Return Date', validators=[DataRequired()])
    submit = SubmitField('Mark as Returned')
