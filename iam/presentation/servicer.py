from app.models import MinimalUser, ResetDataRequest, ConfirmResetData, AuthTokens
from presentation.generated import iam_pb2 as pb2
from presentation.generated import iam_pb2_grpc as pb2_grpc


class AuthServicer(pb2_grpc.AuthServiceServicer):
    def __init__(
            self,
            register_handler,
            login_handler,
            refresh_handler,
            authenticate_handler,
            request_reset_handler,
            confirm_reset_handler
    ):
        self.register_handler = register_handler
        self.login_handler = login_handler
        self.refresh_handler = refresh_handler
        self.authenticate_handler = authenticate_handler
        self.request_reset_handler = request_reset_handler
        self.confirm_reset_handler = confirm_reset_handler

    async def Register(self, request, context):
        cmd = MinimalUser(email=request.email, password=request.password)
        user_id = await self.register_handler.execute(cmd)
        return pb2.RegisterResponse(user_id=str(user_id), message="User created")

    async def Login(self, request, context):
        cmd = MinimalUser(email=request.email, password=request.password)
        tokens: AuthTokens = await self.login_handler.execute(cmd)

        return pb2.LoginResponse(
            access_token=tokens.access,
            refresh_token=tokens.refresh
        )

    async def RefreshToken(self, request, context):
        tokens: AuthTokens = await self.refresh_handler.execute(request.refresh_token)

        return pb2.LoginResponse(
            access_token=tokens.access,
            refresh_token=tokens.refresh
        )

    async def Authenticate(self, request, context):
        user_info = await self.authenticate_handler.execute(request.access_token)

        return pb2.AuthResponse(
            user_id=str(user_info.id),
            email=str(user_info.email),
            is_active=user_info.is_active
        )

    async def RequestReset(self, request, context):
        cmd = ResetDataRequest(email=request.email)
        await self.request_reset_handler.execute(cmd)
        return pb2.ResetResponse(message="If email exists, check your inbox")

    async def ConfirmReset(self, request, context):
        cmd = ConfirmResetData(
            token=request.token,
            new_password=request.new_password
        )
        new_pair = await self.confirm_reset_handler.execute(cmd)
        return pb2.LoginResponse(
            access_token=new_pair.access,
            refresh_token=new_pair.refresh
        )
