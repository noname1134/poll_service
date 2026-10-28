class AnswerAlreadyExistsError(Exception):
    pass

class QuestionNotFoundError(Exception):
    pass


class UserNotFoundError(Exception):
    pass


class UserNotRegisteredError(Exception):
    pass

class UserServiceUnavailableError(Exception):
    pass