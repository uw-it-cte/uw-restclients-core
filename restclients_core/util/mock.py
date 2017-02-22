import re
import os
import json
from urllib import unquote
from restclients_core.models import MockHTTP


def load_resource_from_path(resource_dir, service_name,
                            implementation_name,
                            url, headers):

    RESOURCE_ROOT = os.path.join(resource_dir,
                                 service_name,
                                 implementation_name)

    if url == "///":
        # Just a placeholder to put everything else in an else.
        # If there are things that need dynamic work, they'd go here
        pass
    else:
        orig_file_path = RESOURCE_ROOT + url
        unquoted = unquote(orig_file_path)
        paths = [
            convert_to_platform_safe(orig_file_path),
            "%s/index.html" % (convert_to_platform_safe(orig_file_path)),
            orig_file_path,
            "%s/index.html" % orig_file_path,
            convert_to_platform_safe(unquoted),
            "%s/index.html" % (convert_to_platform_safe(unquoted)),
            unquoted,
            "%s/index.html" % unquoted,
            ]

        file_path = None
        handle = None
        for path in paths:
            try:
                file_path = path
                handle = open(path)
                break
            except IOError as ex:
                pass

        if handle is None:
            return None

        response = MockHTTP()
        response.status = 200
        response.data = handle.read()
        response.headers = {"X-Data-Source": service_name + " file mock data",
                            }

        try:
            headers = open(handle.name + '.http-headers')
            file_values = json.loads(headers.read())

            if "headers" in file_values:
                response.headers = dict(response.headers.items() +
                                        file_values['headers'].items())

                if 'status' in file_values:
                    response.status = file_values['status']

            else:
                response.headers = dict(response.headers.items() +
                                        file_values.items())

        except IOError:
            pass

        return response


def convert_to_platform_safe(dir_file_name):
    """
    :param dir_file_name: a string to be processed
    :return: a string with all the reserved characters replaced
    """
    return re.sub('[\?|<>=:*,;+&"@$]', '_', dir_file_name)
