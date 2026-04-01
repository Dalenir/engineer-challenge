import grpc

from app.interfaces import CacheService


class RateLimitInterceptor(grpc.aio.ServerInterceptor):
    def __init__(self, cache_service: CacheService):
        self.cache = cache_service
        self.limits = {
            "/iam.AuthService/Login": {"limit": 5, "window": 300},
            "/iam.AuthService/RequestReset": {'limit': 1, 'window': 60}
        }

    async def intercept_service(self, continuation, handler_call_details):
        method = handler_call_details.method

        if method in self.limits:
            metadata = dict(handler_call_details.invocation_metadata)
            client_id = metadata.get("x-forwarded-for", "unknown_ip")

            limit_cfg = self.limits[method]
            key = f"rl:{method}:{client_id}"

            count = await self.cache.increment(key, expire=limit_cfg["window"])

            if count > limit_cfg["limit"]:
                return self._abort_handler(
                    grpc.StatusCode.RESOURCE_EXHAUSTED,
                    "Rate limit exceeded"
                )

        return await continuation(handler_call_details)

    @staticmethod
    def _abort_handler(code, details):

        async def abort(request, context):
            await context.abort(code, details)

        return grpc.unary_unary_rpc_method_handler(abort)
