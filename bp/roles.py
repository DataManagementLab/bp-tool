from bp.models import BP

def is_tl(user):
    return hasattr(user, 'tl')

def is_student(user):
    return hasattr(user, 'student')

def is_orga(user):
    return user.is_superuser

def is_tl_or_student(user):
    return is_tl(user) or is_student(user)

def is_tl_of_group(group, user):
    return user.tl == group.tl

def is_student_of_group(group, user):
    return user.student in group.student_set.all()

def is_neither_tl_nor_student_of_group(group, user):
    if is_tl(user) and is_tl_of_group(group, user):
        return False
    if is_student(user) and is_student_of_group(group, user):
        return False
    return True

def get_bp_of_user(user):
    if is_tl(user):
        return user.tl.bp
    if is_student(user):
        return user.student.bp
    if is_orga(user):
        return BP.get_active()
    return None

def has_role(user):
    return is_orga(user) or is_tl(user) or is_student(user)
