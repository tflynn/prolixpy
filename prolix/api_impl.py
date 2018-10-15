import standard_logger
from prolix.config import Config
from prolix import steno


class ApiImpl:
    """ApiImpl implements the public-facing API methods for the Prolix package"""

    def __init__(self, **kwargs):
        self.logger = kwargs['logger'] if 'logger' in kwargs else standard_logger.get_logger('prolix_api')
        self.conf_data = Config.conf().get_data()
        self.redis_host = kwargs['redis_host'] if 'redis_host' in kwargs else self.conf_data['redis_host']
        self.redis_port = kwargs['redis_port'] if 'redis_port' in kwargs else self.conf_data['redis_port']
        self.redis_password = kwargs['redis_password'] if 'redis_password' in kwargs \
            else self.conf_data['redis_password']
        self.default_store_expiration_secs = kwargs['default_store_expiration_secs'] \
            if 'default_store_expiration_secs' in kwargs \
            else self.conf_data['default_store_expiration_secs']
        self.steno = steno.Steno(logger=self.logger)

    def add_error(self, error_text, status={}):
        """
        Add error text to a dict

        :param str error_text: Error text
        :param dict status: Dict containing status information
        :return: No return. Status dict is updated in place
        """
        all_errors = status['errors'] if 'errors' in status else []
        all_errors.append("ApiImpl.obscure no text specified")
        status["errors"] = all_errors
        return

    def obscure(self, text=None, expiration_secs=None):
        """
        Obscure text

        :param str text: Text to obscured
        :param int expiration_secs: How long text should be valid for - default 300 secs (5 mins)
        :return: {key, expiration_secs, obscured text, errors}
        :rtype: dict
        """
        status = {}
        if not text:
            self.add_error("ApiImpl.obscure no text specified", status=status)
            return status

        if not expiration_secs:
            expiration_secs = self.self.default_store_expiration_secs

        results = self.steno.obscure(text=text, expiration_secs=expiration_secs)
        if 'errors' in results:
            self.add_error(results['error'], status=status)
            del results['error']

        status.update(results)
        return status

    def clarify(self, key=None, text=None):
        """
        Clarify text previously obscured

        :param str key: Key returned from obscure process
        :param str text: Text returned from  obscure process
        :return: {clarified text, error}
        :rtype: dict
        """
        status = {}
        if not key:
            self.add_error("ApiImpl.clarify no key specified", status=status)
        if not text:
            self.add_error("ApiImpl.clarify no obscured text specified", status=status)
        if status:
            return status

        results = self.steno.clarify(key=key, text=text)
        if 'errors' in results:
            self.add_error(results['error'], status=status)
            del results['error']

        status.update(results)
        return status
