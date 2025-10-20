import re
from teams.connector import generate_join_code

def test_join_code_format_and_length():
    code = generate_join_code()
    assert len(code) == 8
    assert re.fullmatch(r"[A-Z0-9]{8}", code)

def test_join_code_uniqueness_sample():
    codes = {generate_join_code() for _ in range(3000)}
    assert len(codes) == 3000  # very low collision odds at 36^8
