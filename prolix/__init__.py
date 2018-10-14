from prolix import api_impl


def api(**kwargs):
    return api_impl.ApiImpl(**kwargs)


