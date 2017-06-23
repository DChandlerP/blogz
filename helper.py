import re
def does_pw_match(password, verify):
    if password and verify:
        return password == verify
    else:
        return False

def is_un_or_pw_valid(username):
    if username:
        return re.match(r'^[\S]{3,20}$', username) is not None
    else:
        return False

#Apparently you can't initialize the DB in the shell w/o this.
if __name__ == '__main__':
    app.run()