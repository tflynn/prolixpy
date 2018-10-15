import standard_logger
from prolix.config import Config


class ApiImpl:
    """ApiImpl implements the public-facing API methods for the Prolix package"""

    def __init__(self, **kwargs):
        self.logger = kwargs['logger'] if 'logger' in kwargs else standard_logger.get_logger('prolix_api')
        self.conf_data = Config.conf().get_data()
        self.redis_host = kwargs['redis_host'] if 'redis_host' in kwargs else self.conf_data['redis_host']
        self.redis_port = kwargs['redis_port'] if 'redis_port' in kwargs else self.conf_data['redis_port']
        self.redis_password = kwargs['redis_password'] if 'redis_password' in kwargs \
            else self.conf_data['redis_password']

    def obscure(self, text=None, expiration_secs = None):
        """
        Obscure text

        :param str text: Text to obscured
        :param int expiration_secs: How long text should be valid for - default 300 secs (5 mins)
        :return: {key, expiration_secs, obscured text, error}
        :rtype: dict
        """
        return {'error':'Not implemented'}

    def clarify(self, key=None, text=None):
        """
        Clarify text previously obscured
        :param str key: Key returned from obscure process
        :param str text: Text returned from  obscure process
        :return: {clarified text, error}
        :rtype: dict
        """
        return {'error':'Not implemented'}
