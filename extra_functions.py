from wtforms.validators import ValidationError

def password_val(form, field):
    errors = []
    password = field.data
    if not any(x.isupper() for x in password):
        errors.append("Must contain atleast one UPPERCASE.")
    if not any(x.islower() for x in password):
        errors.append("Must contain atleast one lowercase.")
    if not any(x.isdigit() for x in password):
        errors.append("Must contain atleast one digit.")
    if not len(password) >= 6:
        errors.append("The password should have minimum length of 6.")

    if errors:
        message = " ".join(errors)
        raise ValidationError(message)
