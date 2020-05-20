from wtforms.validators import ValidationError
from datetime import datetime
from dateutil.relativedelta import relativedelta

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

# time difference
def time_diff(old):
    current = str(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    x_current = datetime.strptime(current, '%Y-%m-%d %H:%M:%S')
    old = str(old.strftime('%Y-%m-%d %H:%M:%S'))
    x_old = datetime.strptime(old, '%Y-%m-%d %H:%M:%S')
    diff = relativedelta(x_current, x_old)
    if diff.years > 4:
        x = "Long time ago"
    elif (diff.years >= 1) and (diff.years <= 4):
        if diff.months == 0:
            if diff.days <= 1:
                x = str(diff.years)+"y ago"
            else:
                x = str(diff.years) + "y " + str(diff.days) + "d ago"
        else:
            if diff.days <= 1:
                x = str(diff.years)+"y "+str(diff.months)+"m ago"
            else:
                x = str(diff.years) + "y " + str(diff.months)+"m "+ str(diff.days) + "d ago"
    else:
        if diff.months > 0:
            if diff.days <= 1:
                x = str(diff.months)+"m ago"
            else:
                x = str(diff.months) + "m " + str(diff.days) + "d ago"
        else:
            if diff.days > 2:
                x = str(diff.days)+"day ago"
            else:
                if diff.hours > 0:
                    if diff.minutes > 0:
                        x = str(diff.hours) + "h " + str(diff.minutes) +"m ago"
                    else:
                        x = str(diff.hours)+"h ago"
                else:
                     if diff.minutes > 0:
                         x = str(diff.minutes) +"m ago"
                     else:
                         x = "Few seconds ago"

    return x

# time string
def time_small(old):
    current = str(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    x_current = datetime.strptime(current, '%Y-%m-%d %H:%M:%S')
    old = str(old.strftime('%Y-%m-%d %H:%M:%S'))
    x_old = datetime.strptime(old, '%Y-%m-%d %H:%M:%S')
    diff = relativedelta(x_current, x_old)
    if diff.days == 0:
        y = "Today, "
        x = y+str(x_old.day)+"/"+str(x_old.month)+"/"+str(x_old.year)
    elif diff.days == 1:
        y = "Yesterday, "
        x = y+str(x_old.day)+"/"+str(x_old.month)+"/"+str(x_old.year)
    else:
        x = str(x_old.day)+"/"+str(x_old.month)+"/"+str(x_old.year)

    return x
