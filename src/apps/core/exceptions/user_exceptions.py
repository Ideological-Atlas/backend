class UserAlreadyVerifiedException(Exception):
    def __init__(self, user=None):
        self.user = user
        if self.user is not None:
            self.message = f"User {user} already verified"
        else:
            self.message = "User not verified"
        super().__init__(self.message)
