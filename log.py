class log(object):
    def __init__(self, variable=None, message=0):
        self._variable = variable
        self._message = message

        if self._message != 0:
            print(message + " : " + str(variable))

        elif self._variable:
            print(str(variable))

class logSection(object):
    def __init__(self, title):
        print("===================================")
        print(title)
        print("-----------------------------------")