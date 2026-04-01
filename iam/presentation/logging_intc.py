import grpc
import time
import structlog

log = structlog.get_logger()


class LoggingInterceptor(grpc.aio.ServerInterceptor):
    async def intercept_service(self, continuation, handler_call_details):
        metadata = dict(handler_call_details.invocation_metadata)
        request_id = metadata.get("x-request-id", "internal-gen")

        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(
            request_id=request_id,
            method=handler_call_details.method
        )

        start_time = time.perf_counter()

        try:
            log.info("grpc_request_start")

            response = await continuation(handler_call_details)

            duration = time.perf_counter() - start_time
            log.info(
                "grpc_request_success",
                duration_ms=round(duration * 1000, 2)
            )
            return response

        except Exception as e:
            duration = time.perf_counter() - start_time
            log.error(
                "grpc_request_failed",
                error=str(e),
                duration_ms=round(duration * 1000, 2),
                exc_info=True
            )
            raise e