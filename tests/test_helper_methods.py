# from helper_methods import *


# class TestListManagmement(object):
#     def test_get_all_lists(self):
#         # returns list for existant user
#         assert type(get_all_lists('kevin.ma')) == list

#         # should return null - non existant user
#         assert get_all_lists('fakename324') is None


# class TestAuthentication(object):
#     def test_is_authenticated(self):
#         # test authentication for valid tg->zv connection
#         assert is_authenticated('kevin.ma', '289934826') == True

#         # test authentication for invalid tg->zv connection
#         assert is_authenticated('kevin.ma', '123456789') == False

class TestFoo(object):
    def test(self):
        assert 2 > 1