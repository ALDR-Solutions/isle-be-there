from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import StringField, SubmitField, FileField, DateField, EmailField, PasswordField
from wtforms.validators import DataRequired, Optional, Email, EqualTo


class ProfileForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    phone_number = StringField('Phone Number', validators=[Optional()])
    birth_date = DateField('Date of Birth', validators=[Optional()])
    avatar = FileField('Upload Avatar', validators=[FileAllowed(['jpg', 'png', 'jpeg', 'gif'], 'Images only!')])
    submit = SubmitField('Update Profile')

class UpdateEmailForm(FlaskForm):
    email = EmailField(
        "Email",
        validators=[
            DataRequired("Email is required."),
            Email(),
            EqualTo(fieldname="email_confirm", message="Email Address does not match"),
        ],
    )
    email_confirm = EmailField(
        "Confirm email", validators=[DataRequired("Email is required."), Email()]
    )
    submit = SubmitField("Update Email")

class UpdatePasswordForm(FlaskForm):
    password = PasswordField(
        "Password", validators=[DataRequired("Password is required.")]
    )
    password_confirm = PasswordField(
        "Confirm password",
        validators=[
            DataRequired("Password is required."),
            EqualTo(fieldname="password", message="Password does not match"),
        ],
    )
    submit = SubmitField("Update Password")
