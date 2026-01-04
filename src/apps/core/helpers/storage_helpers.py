def handle_storage(instance, filename):
    """
    This helper is to save in the database the files using the identifier uuid for the
    associated instance
    :param instance:
    :param filename:
    :return:
    """
    file_extension = filename.split(".")[-1]
    name_value = instance.uuid.hex
    return f"{instance.__class__.__name__}/{name_value}.{file_extension}"
