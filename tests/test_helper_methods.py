from helper_methods import *
from test_properties import *


class TestListManagmement(object):
    def test_get_all_lists(self):
        # returns list of lists for existant zevere user
        assert type(get_all_lists(VALID_ZEVERE_USER)) == list

        # should return null for non existant zevere users
        assert get_all_lists(INVALID_ZEVERE_USER) is None

    def test_create_list(self):
        # create new list for the zevere user
        # should return the id of the list which is the list title
        # toLower and spaces replaced with underscore characters
        assert create_list(VALID_ZEVERE_USER, LIST_TITLE,
                           LIST_DESCRIPTION) == (True, LIST_TITLE.strip().lower().replace(' ', '_'))

        # creating a list that already exists for the zevere user
        # should return None since the list is not created again
        assert create_list(VALID_ZEVERE_USER,
                           LIST_TITLE, LIST_DESCRIPTION) == (False, None)

    # def test_get_list_by_id(self):
    #     # try to get the list we created in the above test case
    #     result = get_list_by_id(VALID_LIST_ID)
    #     assert hasattr(result, 'id') & result['id'] == VALID_LIST_ID

    #     # try to get a non existent list
    #     assert get_list_by_id(INVALID_LIST_ID) is None

    # def test_delete_list(self):
    #     # trying to delete a list not owned by the zv_user passed
    #     # in as an argument should return False and None as no
    #     # list was deleted
    #     assert delete_list(*INVALID_OWNER_VALID_LIST) == (
    #         False, None)

    #     # trying to delete a list by an id that does not exist
    #     # should return False and None as no list was deleted
    #     assert delete_list(*INVALID_OWNER_AND_LIST) == (
    #         False, None)

    #     # trying to delete a list owned by the zv_user passed
    #     # in as an argument should return True and the id of the list that was deleted
    #     assert delete_list(*VALID_LIST_AND_OWNER) == (
    #         True, VALID_LIST_AND_OWNER[1])

    # class TestAuthentication(object):
    #     def test_is_authenticated(self):
    #         # test authentication for valid tg->zv connection
    #         # should return True and the zv_user the tg user is auth'd as
    #         assert is_authenticated(
    #             *VALID_ZV_CONNECTION) == (True, VALID_ZV_CONNECTION[0])

    #         # test authentication for invalid tg->zv connection
    #         # should return False and None since tg user not auth'd
    #         assert is_authenticated(*INVALID_ZV_CONNECTION) == (False, None)

    #     def test_logout(self):
    #         # valid telegram to zevere connection
    #         assert logout(*VALID_ZV_CONNECTION) == (
    #             True, 'You have successfully been logged out from {}'.format(VALID_ZV_CONNECTION[0]))

    #         # invalid telegram to zevere connection
    #         assert logout(*INVALID_ZV_CONNECTION) == (
    #             False, 'You are not logged in to any Zevere account.')
