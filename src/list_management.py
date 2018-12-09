import requests
from properties import BORZOO_ROOT_URL


def get_list_by_id(list_id):
    # TODO implement this func when the feature has been implemented in the BORZOO graphql api
    pass


def create_list(zv_user, list_title, list_description):
    """Creates a list for this Zevere user.

    Keyword arguments:
    zv_user - the user id of the Zevere user
    list_title - the title of the list to be deleted
    list_description - Optional; the description of the list to be deleted

    Returns:
        True, list id   - upon successful creation
        False, None     - upon failure
    """

    from helper_methods import convert_list_title_to_id
    list_id = convert_list_title_to_id(list_title)

    print(
        '\nLIST DETAILS\nlist_title={}\nlist_id={}\nlist_description={}\nowner={}\n'.format(
            list_title, list_id, list_description, zv_user)
    )

    # TODO change to use get list here instead of get_all_lists once the func is implemented in BORZOO

    # check if list exists for the user already
    owned_lists = get_all_lists(zv_user)
    for list in owned_lists:
        if list['id'] == list_id:
            return False, None

    # if reached here, means list does not already exist for this zv_user
    # send POST request to borzoo graphql web api to create list with the above list details
    if list_description is not None:
        response = requests.post('{}/zv/graphql'.format(BORZOO_ROOT_URL),
                                 json={
            "query": "mutation {createList(owner: \"" + zv_user + "\", list: {id: \""+list_id+"\", title: \""+list_title+"\", description: \""+list_description+"\"}){id}}"
        },
            headers={'Content-Type': 'application/json'})
    else:
        response = requests.post('{}/zv/graphql'.format(BORZOO_ROOT_URL),
                                 json={
            "query": "mutation {createList(owner: \"" + zv_user + "\", list: {id: \""+list_id+"\", title: \""+list_title+"\"}){id}}"
        },
            headers={'Content-Type': 'application/json'})

    if response.status_code == 200:
        response = response.json()
        print('\ncreate_list\nresponse: {}\n'.format(response))
        return True, response['data']['createList']['id']
    else:
        # borzoo is offline
        return False, None

    return False, None


def delete_list(zv_user, list_id):
    """Deletes a list belonging to a Zevere user.

    Keyword arguments:
    zv_user - the user id of the Zevere user
    list_id - the id of the list to be deleted

    Returns:
        True, list id   - upon successful delete
        False, None     - if list does not exist for this Zevere user
    """
    # send POST request to borzoo graphql web api to delete list belonging to the current connected zv user
    response = requests.post('{}/zv/graphql'.format(BORZOO_ROOT_URL),
                             json={
        "query": "mutation{ deleteList(owner:\"" + zv_user + "\", list:\""+list_id+"\")}"
    },
        headers={'Content-Type': 'application/json'})

    if response.status_code == 200:
        response = response.json()
        print('\ndelete_list\nresponse: {}\n'.format(response))
        if response['data']['deleteList'] == True:
            return True, list_id
        else:
            # Task list not found
            return False, None
    else:
        # borzoo is offline
        return False, None


def get_all_lists(zv_user):
    """Returns a list of all the lists owned by zv_user.

    Keyword arguments:
    zv_user -- the user id of the Zevere user
    """
    # send POST request to borzoo graphql web api to query lists belonging to connected zv user
    response = requests.post('{}/zv/graphql'.format(BORZOO_ROOT_URL),
                             json={
        "query": "query{ user(userId:\"" + zv_user + "\") { lists { id collaborators createdAt description owner tags tasks { id } title updatedAt } } }"
    },
        headers={'Content-Type': 'application/json'})

    if response.status_code == 200:
        response = response.json()
        print('\nget_all_lists\nresponse: {}\n'.format(response))
        if response['data']['user'] == None:
            owned_lists = None
        else:
            owned_lists = response['data']['user']['lists']
    else:
        owned_lists = None

    return owned_lists
