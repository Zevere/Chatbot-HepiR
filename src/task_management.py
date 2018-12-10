import requests
from properties import BORZOO_ROOT_URL


def get_all_tasks(zv_user, list_id):
    """Returns a list of all the tasks within the list owned by zv_user.

    Keyword arguments:
    zv_user - the user id of the Zevere user
    zv_user - the list id of the List we want to retrieve tasks from
    """
    # send POST request to borzoo graphql web api to query lists belonging to connected zv user
    response = requests.post('{}/zv/graphql'.format(BORZOO_ROOT_URL),
                             json={
        "query": "query{ user(userId:\"" + zv_user + "\") { list(listId:\"" + list_id + "\") { tasks { id title description createdAt } } } }"
    },
        headers={'Content-Type': 'application/json'})

    if response.status_code == 200:
        response = response.json()
        print('get_all_tasks\nresponse: {}\n'.format(response))
        if response['data']['user'] == None or response['data']['user']['list'] == None:
            existing_tasks = None
        else:
            existing_tasks = response['data']['user']['list']['tasks']
    else:
        existing_tasks = None

    return existing_tasks


def create_task(zv_user, list_id, task_title, task_description):
    """Creates a task for this Zevere user under the list which has list_id.

    Keyword arguments:
    zv_user - the user id of the Zevere user
    list_id - the id of the list where this task will be added to
    task_title - the title of the task to be added
    task_description - Optional; the description of the task to be added

    Returns:
        True, list id   - upon successful creation
        False, None     - upon failure
    """

    from helper_methods import convert_task_title_to_id
    task_id = convert_task_title_to_id(task_title)

    print(
        '\nTASK DETAILS\ntask_title={}\ntask_id={}\ntask_description={}\nowner={}\nlist_id={}\n'.format(
            task_title, task_id, task_description, zv_user, list_id)
    )

    # check if task exists for the list already
    # check that the list does not already contain the task that the user is trying to add
    existing_tasks = get_all_tasks(zv_user, list_id)

    if existing_tasks is not None:
        for task in existing_tasks:
            if task['id'] == task_id:
                print('task with id={} already exists for the connected_user({})\'s list_id={}\nThe task will not be created.'.format(
                    task_id, zv_user, list_id))
                return False, None

    # if reached here, means task does not already exist for this zv_user list_id
    # send POST request to borzoo graphql web api to create task with the above task details
    if task_description is not None:
        response = requests.post('{}/zv/graphql'.format(BORZOO_ROOT_URL),
                                 json={
            "query": "mutation {createTask(ownerId: \"" + zv_user + "\" listId: \"" + list_id + "\" task: {id: \"" + task_id + "\", title: \"" + task_title + "\", description: \"" + task_description + "\"}){id title description createdAt}}"
        },
            headers={'Content-Type': 'application/json'})
    else:
        response = requests.post('{}/zv/graphql'.format(BORZOO_ROOT_URL),
                                 json={
            "query": "mutation {createTask(ownerId: \"" + zv_user + "\" listId: \"" + list_id + "\" task: {id: \"" + task_id + "\", title: \"" + task_title + "\"}){id title description createdAt}}"
        },
            headers={'Content-Type': 'application/json'})

    if response.status_code == 200:
        response = response.json()
        print('\ncreate_task\nresponse: {}\n'.format(response))

        # invalid list id
        if response['data']['createTask'] is None:
            return False, None
        return True, response['data']['createTask']['id']
    else:
        # borzoo is offline
        return False, None

    return False, None
