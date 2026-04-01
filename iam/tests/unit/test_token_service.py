from domain.v_objects import TokenType


def test_token_type_mismatch_fails(token_service, user_entity):
    reset_token = token_service.create_token(user_entity, TokenType.PASSWORD_RESET, 77)

    decoded = token_service.decode_token(reset_token)

    assert decoded.token_type == TokenType.PASSWORD_RESET
    assert decoded.token_type != TokenType.ACCESS
