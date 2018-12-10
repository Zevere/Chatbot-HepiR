import requests
from properties import BORZOO_ROOT_URL


def get_task_by_id(task_id):
    # TODO implement this func when the feature has been implemented in the BORZOO graphql api
    pass


def get_all_tasks(zv_user, list_id):
    """Returns a list of all the tasks within the list owned by zv_user.

    Keyword arguments:
    zv_user - the user id of the Zevere user
    zv_user - the list id of the List we want to retrieve tasks from
    """
    # send POST request to borzoo graphql web api to query lists belonging to connected zv user
    response = requests.post('{}/zv/graphql'.format(BORZOO_ROOT_URL),
                             json={
        "query": "query{ user(userId:\"" + zv_user + "\") { list(listId:\"" + list_id + "\") { tasks { id title description } } } }"
    },
        headers={'Content-Type': 'application/json'})

    if response.status_code == 200:
        response = response.json()
        print('\get_all_tasks\nresponse: {}\n'.format(response))
        if response['data']['user']['list'] == None:
            existing_tasks = None
        else:
            existing_tasks = response['data']['user']['list']['tasks']
    else:
        existing_tasks = None

    return existing_tasks
