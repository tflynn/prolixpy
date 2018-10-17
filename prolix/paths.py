# import pkg_resources
# from os import path
#
# def get_package_path():
#     possible_path = pkg_resources.resource_filename('prolix', '/')
#     possible_path = path.normpath(possible_path)
#     return possible_path if path.exists(possible_path) else None
#
#
# def get_data_path(file_name=None):
#     if file_name:
#         possible_path = pkg_resources.resource_filename('prolix', "data/{0}".format(file_name))
#     else:
#         possible_path = pkg_resources.resource_filename('prolix', 'data/')
#     possible_path = path.normpath(possible_path)
#     return possible_path if path.exists(possible_path) else None
#
