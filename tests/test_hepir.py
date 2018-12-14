from test_properties import *
from authentication import connect, disconnect, get_authenticated_zvuser, is_authenticated
from list_management import create_list, get_all_lists, delete_list, get_list_by_id
from task_management import get_all_tasks, create_task, delete_task


class TestAuthentication(object):
    def test_login(self):
        # TEST ENV SETUP
        # make sure the valid account is logged out first before trying to login with the account
        print('*'*50)
        print('TEST ENVIRONMENT SETUP')
        print(disconnect(*VALID_ZV_CONNECTION)[1])
        print('*'*50)

        # trying to login with valid credentials
        assert connect(*VALID_ZV_CONNECTION) == (
            True, 'You have successfully logged into the Zevere account {} with your telegram account of {}'.format(VALID_ZV_CONNECTION[0], VALID_ZV_CONNECTION[1]))

        # trying to login with invalid credentials
        assert connect(*INVALID_ZV_CONNECTION) == (
            False, 'You have provided invalid login credentials.')

    def test_is_authenticated(self):
        # TEST ENV SETUP
        # make sure the valid account is logged in first before trying to logout with the account
        connect(*VALID_ZV_CONNECTION)

        # test authentication for valid tg->zv connection
        # should return True and the zv_user the tg user is auth'd as
        assert is_authenticated(VALID_TG_ID) == True

        # test authentication for invalid tg->zv connection
        # should return False and None since tg user not auth'd
        assert is_authenticated(INVALID_TG_ID) == False

    def test_get_authenticated_zvuser(self):
        # TEST ENV SETUP
        # make sure the valid account is logged in first
        print('*'*50)
        print('TEST ENVIRONMENT SETUP')
        print(connect(*VALID_ZV_CONNECTION)[1])
        print('*'*50)

        # self explanatory
        assert get_authenticated_zvuser(VALID_TG_ID) == VALID_ZEVERE_USER

        # self explanatory
        assert get_authenticated_zvuser(INVALID_TG_ID) is None

    def test_logout(self):
        # TEST ENV SETUP
        # make sure the valid account is logged in first before trying to logout with the account
        print('*'*50)
        print('TEST ENVIRONMENT SETUP')
        print(connect(*VALID_ZV_CONNECTION)[1])
        print('*'*50)

        # trying to logout valid telegram to zevere connection
        assert disconnect(*VALID_ZV_CONNECTION) == (
            True, 'You have successfully been logged out from {}'.format(VALID_ZV_CONNECTION[0]))

        # trying to logout with invalid telegram to zevere connection
        assert disconnect(*INVALID_ZV_CONNECTION) == (
            False, 'You are not logged in to any Zevere account.')


class TestListManagmement(object):
    def test_create_list(self):
        # TEST ENV SETUP
        # make sure the valid account is logged in first
        print('*'*50)
        print('TEST ENVIRONMENT SETUP')
        print(connect(*VALID_ZV_CONNECTION)[1])
        print('*'*50)

        # create new list for the zevere user
        # should return the id of the list which is the list title
        # toLower and spaces replaced with underscore characters
        assert create_list(VALID_ZEVERE_USER, LIST_TITLE,
                           LIST_DESCRIPTION) == (True, LIST_TITLE.strip().lower().replace(' ', '_'))

        # creating a list that already exists for the zevere user
        # should return None since the list is not created again
        assert create_list(VALID_ZEVERE_USER,
                           LIST_TITLE, LIST_DESCRIPTION) == (False, None)

    def test_get_all_lists(self):
        # TEST ENV SETUP
        # make sure the valid account is logged in first
        print('*'*50)
        print('TEST ENVIRONMENT SETUP')
        print(connect(*VALID_ZV_CONNECTION)[1])
        print('*'*50)

        # returns list of lists for existant zevere user
        assert type(get_all_lists(VALID_ZEVERE_USER)) == list

        # should return null for non existant zevere users
        assert get_all_lists(INVALID_ZEVERE_USER) is None

    def test_get_list_by_id(self):
        # TEST ENV SETUP
        # make sure the valid account is logged in first
        print('*'*50)
        print('TEST ENVIRONMENT SETUP')
        print(connect(*VALID_ZV_CONNECTION)[1])
        print('*'*50)

        # try to get the list we created in the above test case
        result = get_list_by_id(VALID_ZEVERE_USER, VALID_LIST_ID)
        assert result['id'] == VALID_LIST_ID

        # try to get a non existent list
        assert get_list_by_id(VALID_ZEVERE_USER, INVALID_LIST_ID) is None

    def test_delete_list(self):
        # TEST ENV SETUP
        # make sure the valid account is logged in first
        print('*'*50)
        print('TEST ENVIRONMENT SETUP')
        print(connect(*VALID_ZV_CONNECTION)[1])
        print('*'*50)

        # trying to delete a list not owned by the zv_user passed
        # in as an argument should return False and None as no
        # list was deleted
        assert delete_list(*INVALID_OWNER_VALID_LIST) == (
            False, None)

        # trying to delete a list by an id that does not exist
        # should return False and None as no list was deleted
        assert delete_list(*INVALID_OWNER_AND_LIST) == (
            False, None)

        # trying to delete a list owned by the zv_user passed
        # in as an argument should return True and the id of the list that was deleted
        assert delete_list(*VALID_LIST_AND_OWNER) == (
            True, VALID_LIST_AND_OWNER[1])


class TestTaskManagement(object):
    def test_create_task(self):
        # TEST ENV SETUP
        # make sure the valid account is logged in first before trying to logout with the account
        print('*'*50)
        print('TEST ENVIRONMENT SETUP')
        print(connect(*VALID_ZV_CONNECTION)[1])
        print('The list with id = {} was successfully created'.format(
            create_list(VALID_ZEVERE_USER, LIST_TITLE, LIST_DESCRIPTION)))
        print('*'*50)

        # create new task for the zevere user for an existing list
        # should return the id of the task which is the task title
        # toLower and spaces replaced with underscore characters
        assert create_task(VALID_ZEVERE_USER, VALID_LIST_ID, TASK_TITLE,
                           TASK_DESCRIPTION) == (True, TASK_TITLE.strip().lower().replace(' ', '_'))

        # creating a task that already exists for the zevere user's list
        # should return None since the task is not created again
        assert create_task(VALID_ZEVERE_USER, VALID_LIST_ID,
                           TASK_TITLE, TASK_DESCRIPTION) == (False, None)

        # creating a task for a non-existent list
        # should return None since the task cannot be created
        assert create_task(VALID_ZEVERE_USER, INVALID_LIST_ID,
                           TASK_TITLE, TASK_DESCRIPTION) == (False, None)

        # creating a task for a list not belonging to the connected zevere user
        # should return None since the task will not be created
        assert create_task(VALID_ZEVERE_USER, VALID_LIST_ID2,
                           TASK_TITLE, TASK_DESCRIPTION) == (False, None)

        # creating a list with an invalid zevere user
        # should return None since the list is not created
        assert create_task(INVALID_ZEVERE_USER, VALID_LIST_ID,
                           LIST_TITLE, LIST_DESCRIPTION) == (False, None)

    def test_get_all_tasks(self):
        # returns list of tasks for existant zevere user and his/her owned list
        assert type(get_all_tasks(VALID_ZEVERE_USER, VALID_LIST_ID)) == list

        # should return null for existant zevere user but an unknown list
        assert get_all_tasks(VALID_ZEVERE_USER, INVALID_LIST_ID) is None

        # should return null for non existant zevere users
        assert get_all_tasks(INVALID_ZEVERE_USER, VALID_LIST_ID) is None

    def test_delete_task(self):
        # trying to delete a task not part of the list passed
        # in as an argument should return False and None as no
        # task was deleted
        assert delete_task(*VALID_LIST_AND_OWNER, VALID_TASK_ID2) == (
            False, None)

        # trying to delete a task by an id that does not exist
        # should return False and None as no list was deleted
        assert delete_task(*INVALID_OWNER_AND_LIST, INVALID_TASK_ID) == (
            False, None)

        # trying to delete a task part of the list owned by th zv_user passed
        # in as an argument should return True and the id of the list that was deleted
        assert delete_task(*VALID_LIST_AND_OWNER, VALID_TASK_ID) == (
            True, VALID_TASK_ID)

        print('*'*50)
        print('TEST ENVIRONMENT CLEANUP')
        print('The list with id = {} was successfully deleted'.format(
            delete_list(*VALID_LIST_AND_OWNER)[1]))
        # print(disconnect(*VALID_ZV_CONNECTION)[1])
        print('*'*50)
