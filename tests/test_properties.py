VALID_ZEVERE_USER = 'kevin.ma'
INVALID_ZEVERE_USER = 'fakename324'

VALID_TG_ID = '289934826'
INVALID_TG_ID = '123456789'

VALID_ZV_CONNECTION = VALID_ZEVERE_USER, VALID_TG_ID
INVALID_ZV_CONNECTION = INVALID_ZEVERE_USER, INVALID_TG_ID

LIST_TITLE = "Centennial College School Work"
LIST_TITLE2 = "Test List with No Description"
LIST_DESCRIPTION = "This task list is for managing all the school work I have to do from class."

VALID_LIST_ID = LIST_TITLE.strip().lower().replace(' ', '_')
VALID_LIST_ID2 = LIST_TITLE2.strip().lower().replace(' ', '_')
INVALID_LIST_ID = 'xxx. chalbye choo foo?'

VALID_LIST_AND_OWNER = VALID_ZEVERE_USER, VALID_LIST_ID
INVALID_OWNER_VALID_LIST = INVALID_ZEVERE_USER, VALID_LIST_ID
INVALID_OWNER_AND_LIST = INVALID_ZEVERE_USER, INVALID_LIST_ID

TASK_TITLE = 'Rumi Essay'
TASK_TITLE2 = 'Test Task with No Description'
TASK_DESCRIPTION = 'Write 100 page research essay on the philosophical teachings of Rumi'

VALID_TASK_ID = TASK_TITLE.strip().lower().replace(' ', '_')
VALID_TASK_ID2 = TASK_TITLE2.strip().lower().replace(' ', '_')
INVALID_TASK_ID = 'monsTer W3nk4r?? W0t 1s th|s?'
