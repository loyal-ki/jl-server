import os
from datetime import datetime
from decimal import Decimal
from typing import Any

from starlette.background import BackgroundTask
from starlette.responses import FileResponse

from app.core.schema.error_schema import Error
from app.helpers.encoder import jsonable_encoder


class BaseResponse(object):
    @staticmethod
    def model_to_dict(obj, *ignore: str):
        """
        Converts a model object to a dictionary representation.

        Args:
            obj: The model object to convert.
            *ignore (str): Optional. Columns to ignore during conversion.

        Returns:
            dict: The dictionary representation of the model object.

        Raises:
            None.
        """
        # Return the object if it has __table__ attribute.
        if getattr(obj, "__table__", None) is None:
            return obj
        data = dict()
        # This method will add the column names to the data dictionary.
        for c in obj.__table__.columns:
            # Skips ignore if the name is in ignore.
            if c.name in ignore:
                continue
            val = getattr(obj, c.name)
            # Set the data for this column.
            if isinstance(val, datetime):
                data[c.name] = val.strftime("%d-%m-%Y %H:%M:%S")
            else:
                data[c.name] = val
        return data

    @staticmethod
    def dict_model_to_dict(obj):
        """
        Convert a dictionary-based model to a dictionary or a list of dictionaries.

        Args:
            obj (dict): The dictionary-based model to be converted.

        Returns:
            dict: The converted dictionary or list of dictionaries.
        """
        # Convert model to dict list or dict.
        for k, v in obj.items():
            # Convert a model to a dict or list of models.
            if isinstance(v, dict):
                BaseResponse.dict_model_to_dict(v)
            elif isinstance(v, list):
                obj[k] = BaseResponse.model_to_list(v)
            else:
                obj[k] = BaseResponse.model_to_dict(v)
        return obj

    @staticmethod
    def json_serialize(obj):
        """
        Serializes a Python object to a JSON-compatible dictionary.

        Args:
            obj (Any): The Python object to be serialized.

        Returns:
            dict: A JSON-compatible dictionary representation of the object.
        """
        ans = dict()
        # Convert a dict to a dictionary.
        for k, o in dict(obj).items():
            # Convert a Python object to a dictionary.
            if isinstance(o, set):
                ans[k] = list(o)
            elif isinstance(o, datetime):
                ans[k] = o.strftime("%d-%m-%Y %H:%M:%S")
            elif isinstance(o, Decimal):
                ans[k] = str(o)
            elif isinstance(o, bytes):
                ans[k] = o.decode(encoding="utf-8")
            else:
                ans[k] = o
        return ans

    @staticmethod
    def parse_sql_result(data: list):
        """
        Parses the SQL result and returns the list of columns in the data.

        Parameters:
            data (list): A list containing the SQL result.

        Returns:
            columns (list): A list of columns in the data.
            serialized_data (list): A list of serialized objects from the data.
        """
        columns = []
        # Returns a list of columns in the data.
        if len(data) > 0:
            columns = list(data[0].keys())
        return columns, [BaseResponse.json_serialize(obj) for obj in data]

    @staticmethod
    def model_to_list(data: list, *ignore: str):
        """
        Convert a list of model objects to a list of dictionaries.

        Args:
            data (list): The list of model objects to be converted.
            *ignore (str): Optional parameters to specify fields to ignore in the conversion.

        Returns:
            list: A list of dictionaries representing the model objects.
        """
        return [BaseResponse.model_to_dict(x, *ignore) for x in data]

    @staticmethod
    def encode_json(data: Any, *exclude: str):
        """
        Encodes the given data as a JSON string using the `jsonable_encoder` function.

        Args:
            data (Any): The data to be encoded as JSON.
            *exclude (str): Optional. Any properties to exclude from the JSON encoding.

        Returns:
            str: The JSON string representing the encoded data.
        """
        return jsonable_encoder(
            data,
            exclude=exclude,  # type: ignore
            custom_encoder={
                datetime: lambda x: x.strftime("%d-%m-%Y %H:%M:%S")
            },
        )

    @staticmethod
    def success(data=None, code=200, msg="Successfully", exclude=()):
        """
        Generate a success response with optional data, status code, message, and excluded keys.

        Args:
            data (Any, optional): The data to be included in the response. Defaults to None.
            code (int, optional): The status code of the response. Defaults to 200.
            msg (str, optional): The message of the response. Defaults to "Successfully".
            exclude (Tuple[str], optional): The keys to be excluded from the response data. Defaults to ().

        Returns:
            str: The JSON-encoded success response.
        """
        return BaseResponse.encode_json(
            dict(code=code, msg=msg, data=data), *exclude
        )

    @staticmethod
    def records(data: list, code=0, msg="Successfully"):
        """
        Static method that takes a list of data,
        an optional code, and an optional message as parameters.
        Returns a dictionary with keys 'code', 'msg', and 'data',
        where 'code' and 'msg' default to 200 and 'Successfully' respectively.
        'data' is obtained by calling the 'model_to_list' method of
        the 'BaseResponse' class on the input data list.
        """
        return dict(code=code, msg=msg, data=BaseResponse.model_to_list(data))

    @staticmethod
    def success_with_size(data=None, code=0, msg="Successfully", total=0):
        """
        Returns a JSON encoded response.

        :param data: The data to be included in the response. Defaults to None.
        :type data: Any, optional
        :param code: The response code. Defaults to 200.
        :type code: int, optional
        :param msg: The response message. Defaults to "Successfully".
        :type msg: str, optional
        :param total: The total number of data items. Defaults to 0.
        :type total: int, optional
        :return: The JSON encoded response.
        """
        # Returns a JSON encoded response.
        if data is None:
            return BaseResponse.encode_json(
                dict(code=code, msg=msg, data=list(), total=0)
            )
        return BaseResponse.encode_json(
            dict(code=code, msg=msg, data=data, total=total)
        )

    @staticmethod
    def failed(error: Error, data=None):
        """
        Creates a dictionary representing a failed response.

        Parameters:
            msg (str): The error message.
            code (int): The error code. Defaults to 110.
            data (Any): Additional data to include in the response. Defaults to None.

        Returns:
            dict: A dictionary containing the error code, error message, and additional data if provided.
        """
        return dict(
            code=error.get_status(), msg=str(error.get_message()), data=data
        )

    @staticmethod
    def forbidden():
        """
        A static method that returns a dictionary with the code and message for a forbidden access.

        Returns:
            dict: A dictionary with the following keys:
                  - code (int): The HTTP status code for forbidden access (403).
                  - msg (str): The error message indicating the lack of permission.
        """
        return dict(code=403, msg="I'm sorry, you do not have permission.")

    @staticmethod
    def file(filepath, filename):
        """
        Generate a FileResponse object.

        Args:
            filepath (str): The path to the file.
            filename (str): The name of the file.

        Returns:
            FileResponse: The FileResponse object representing the file.

        """
        return FileResponse(
            filepath,
            filename=filename,
            background=BackgroundTask(lambda: os.remove(filepath)),
        )
