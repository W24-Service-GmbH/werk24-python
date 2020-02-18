import base64
import hashlib
import hmac
from typing import List, Tuple, Union

import boto3
import httpx

from werk24.models.ask import W24Ask
from werk24.models.ask_measures import W24AskMeasures
from werk24.models.ask_thumbnail import W24AskThumbnail
from werk24.models.ask_thumbnail_canvas import W24AskThumbnailCanvas
from werk24.models.ask_thumbnail_page import W24AskThumbnailPage
from werk24.models.ask_thumbnail_sheet import W24AskThumbnailSheet
from werk24.models.attachment_drawing import W24AttachmentDrawing
from werk24.models.attachment_model import W24AttachmentModel
from werk24.models.drawing_read_request import W24DrawingReadRequest


class W24ClientException(Exception):
    pass


class W24Client:

    def __init__(
            self,
            w24io_server: str,
            cognito_region: str,
            cognito_identity_pool_id: str,
            cognito_client_id: str,
            cognito_client_secret: str):
        self._jwt_token = None
        self._cognito_region = cognito_region
        self._cognito_identity_pool_id = cognito_identity_pool_id
        self._cognito_client_id = cognito_client_id
        self._cognito_client_secret = cognito_client_secret
        self._w24io_server = w24io_server
        self._w24io_connection = None

    def _make_cognito_client(self) -> boto3.session.Session.client:
        """ Make the Cognito Client to communicate with
        AWS Cognito

        Returns:
            boto3.session.Session.client -- Boto3 Client
        """
        return boto3.client(
            "cognito-idp",
            self._cognito_region)

    def _make_cognito_secret_hash(self, username: str) -> str:
        """ Make the keyed-hash message authentication code (HMAC) calculated using
        the secret key of a user pool client and username plus the client  ID in the message.

        Arguments:
            username {str} -- Username

        Returns:
            str -- Cognito Secret Hash
        """

        # make the message
        message = username + self._cognito_client_id

        # make the secret
        dig = hmac.new(
            self._cognito_client_secret.encode("UTF-8"),
            msg=message.encode('UTF-8'),
            digestmod=hashlib.sha256).digest()

        # turn the secret into a str object
        return base64.b64encode(dig).decode()

    def login(self, username: str, password: str):
        """ Login with username and password and obtain (stored internally)
        the JWT token from the AWS Cognito service.

        Arguments:
            username {str} -- Username
            password {str} -- Password
        """

        # make the connection to aws
        cognito_client = self._make_cognito_client()

        # make the authentication data
        auth_data = {
            'USERNAME': username,
            'PASSWORD': password,
            'SECRET_HASH': self._make_cognito_secret_hash(username)}

        # get the jwt token from AWS cognito
        resp = cognito_client.admin_initiate_auth(
            UserPoolId=self._cognito_identity_pool_id,
            AuthFlow='ADMIN_NO_SRP_AUTH',
            AuthParameters=auth_data,
            ClientId=self._cognito_client_id)

        # store the jwt token
        try:
            self._jwt_token = resp['AuthenticationResult']['IdToken']
        except KeyError:
            raise W24IoClientException(
                "Unable to obtain JWT Token from AWS Cognito.")

        # now make the w24io_client connection with the
        # jwt token
        self._make_w24io_connection()

    def _make_w24io_connection(self):
        self._w24io_connection = httpx.AsyncClient()
        self._w24io_connection.headers.update(
            {"Authorization": "Bearer {}".format(self._jwt_token)})

    def _make_w24io_endpoint(self, path: str) -> str:
        return "{}/{}".format(self._w24io_server, path)

    async def ping(self):
        """ Verify the connection
        """
        return await self._w24io_connection.get(
            self._make_w24io_endpoint("ping"))

    async def read_drawing(
            self,
            callback_url: str,
            callback_secret: str,
            drawing: bytes,
            model: bytes = None,
            feature_thumbnail_page: Tuple[int, int, bool] = None,
            feature_thumbnail_sheet: Tuple[int, int, bool] = None,
            feature_thumbnail_canvas: Tuple[int, int, bool] = None,
            feature_measures: bool = False,
            architecture="CPU_V1"):

        # make the features
        features = self._make_w24io_request_features(
            feature_thumbnail_page,
            feature_thumbnail_sheet,
            feature_thumbnail_canvas,
            feature_measures)

        # make the request
        request = W24DrawingReadRequest(
            callback_url=callback_url,
            callback_secret=callback_secret,
            drawing=self._make_w24io_attachment(
                W24AttachmentDrawing,
                drawing),
            model=self._make_w24io_attachment(
                W24AttachmentModel,
                model),
            features=features,
            architecture=architecture)

        # and send the requestion
        return await self._w24io_connection.post(
            self._make_w24io_endpoint("drawing:read"),
            data=request.json())

    @staticmethod
    def _make_w24io_attachment(
            model: Union[W24AttachmentDrawing, W24AttachmentModel], attachment: bytes):

        # return None if there is no attachment
        if attachment is None:
            return None

        # otherwise make the attachment
        return model.from_png(attachment)

    @classmethod
    def _make_w24io_request_features(
            cls,
            feature_thumbnail_page,
            feature_thumbnail_sheet,
            feature_thumbnail_canvas,
            feature_measures) -> List[W24Ask]:

        features = []

        # add the thumbnail page
        if feature_thumbnail_page is not None:
            features.append(cls._make_w24io_request_feature_thumbnail(
                W24AskThumbnailPage,
                feature_thumbnail_page))

        # add the thumbnail sheet
        if feature_thumbnail_sheet is not None:
            features.append(cls._make_w24io_request_feature_thumbnail(
                W24AskThumbnailSheet,
                feature_thumbnail_sheet))

        # add the thumbnail canvas
        if feature_thumbnail_canvas is not None:
            features.append(cls._make_w24io_request_feature_thumbnail(
                W24AskThumbnailCanvas,
                feature_thumbnail_canvas))

        # add the measures
        if feature_measures:
            features.append(W24AskMeasures())

        return features

    @staticmethod
    def _make_w24io_request_feature_thumbnail(
            feature_class: W24AskThumbnail,
            feature_attrs: Tuple[int, int, bool]) -> W24AskThumbnail:
        return feature_class(
            maximal_width=feature_attrs[0],
            maximal_height=feature_attrs[1],
            auto_rotate=feature_attrs[2])
