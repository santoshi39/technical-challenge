'''
modules - includes all independent methods 
'''
from .db_connection import get_role_count

# ID GENERATOR - to generate unique user IDs for each user registration


def id_generator(role):
    # get the existing count of users based on role
    count_details = get_role_count(role)
    # if there are existing users increment the count
    if count_details is not None:
        count_details = count_details + 1
    # if there are no existing users start with 1
    else:
        count_details = 1
    # if the role is Admin - creates userID as A0001
    if role == 'Admin' or role == 'admin':
        userId = "A000{}".format(count_details)
    # for all the other users - creates userID as R0001
    else:
        userId = "R000{}".format(count_details)
    return userId
