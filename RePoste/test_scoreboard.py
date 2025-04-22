from scoreboard_manager import (
    decode_bcd,
    parse_lamp_bits,
    parse_matches_and_priorities,
    parse_penalty_bits,
)


def test_decode_bcd():
    # Single-digit BCD
    assert decode_bcd(0x00) == 0
    assert decode_bcd(0x06) == 6
    # Two-digit BCD
    assert decode_bcd(0x12) == 12
    assert decode_bcd(0x56) == 56
    # Edge cases
    assert decode_bcd(0x99) == 99  # Technically valid BCD nibble range
    assert decode_bcd(0x0F) == 15  # 0x0F => 0x0 * 10 + 0xF = 15
    # Check that it doesn't do anything unexpected for non-BCD nibbles:
    # 0xAB => A=10 in the high nibble => 100,
    # #B=11 => + 11 = 111 (It’s “valid” math, not typical scoreboard data)
    assert decode_bcd(0xAB) == 111


def test_parse_lamp_bits():
    # b6 = 0x14 => 00010100 in binary
    # D2=1 => left_red = True, D4=1 => right_yellow = True
    b6 = 0x14
    result = parse_lamp_bits(b6)
    assert result["left_white"] is False
    assert result["right_white"] is False
    assert result["left_red"] is True
    assert result["right_green"] is False
    assert result["right_yellow"] is True
    assert result["left_yellow"] is False

    # Another example: 0x3F => 00111111 => all lower six bits set
    b6 = 0x3F
    result = parse_lamp_bits(b6)
    # D0=1 => left_white
    assert result["left_white"] is True
    # D1=1 => right_white
    assert result["right_white"] is True
    # D2=1 => left_red
    assert result["left_red"] is True
    # D3=1 => right_green
    assert result["right_green"] is True
    # D4=1 => right_yellow
    assert result["right_yellow"] is True
    # D5=1 => left_yellow
    assert result["left_yellow"] is True


def test_parse_matches_and_priorities():
    # (Example from doc: 0x0A => binary 1010 => D1=1 => 2 matches,
    # D3=1 => left priority)
    b7 = 0x0A  # 0b1010
    result = parse_matches_and_priorities(b7)
    assert result["num_matches"] == 2
    assert result["right_priority"] is False
    assert result["left_priority"] is True

    # (Example 2: 0x07 => 0b0111 => D1=0, D0=3 => 3 matches,
    # D2=1 => right priority, D3=0 => left priority off)

    # Actually note that D0..D1 can only form 0..3 in decimal,
    # so bits are 2 bits total. If D0=1, D1=1 => that’s 3

    # 0b0111 => D0=1, D1=1 => 3 matches, D2=1 => right priority,
    # D3=0 => left priority
    b7 = 0x07
    result = parse_matches_and_priorities(b7)
    assert result["num_matches"] == 3
    assert result["right_priority"] is True
    assert result["left_priority"] is False

    # Another example: 0x00 => 0b0000 => 0 matches, no priorities
    b7 = 0x00
    result = parse_matches_and_priorities(b7)
    assert result["num_matches"] == 0
    assert result["right_priority"] is False
    assert result["left_priority"] is False


def test_parse_penalty_bits():
    # Example from doc: 0x38 => 00111000 => D3=1 => left yellow penalty
    b9 = 0x38
    result = parse_penalty_bits(b9)
    assert result["penalty_right_red"] is False
    assert result["penalty_left_red"] is False
    assert result["penalty_right_yellow"] is False
    assert result["penalty_left_yellow"] is True

    # Another scenario: 0x0F => 00001111 => bits D0..D3
    # are all 1 => all four penalty lights ON
    b9 = 0x0F
    result = parse_penalty_bits(b9)
    assert result["penalty_right_red"] is True
    assert result["penalty_left_red"] is True
    assert result["penalty_right_yellow"] is True
    assert result["penalty_left_yellow"] is True

    # Another scenario: 0x05 => 00000101 => bits D0=1 =>
    # Right Red ON, D2=1 => Right Yellow ON
    b9 = 0x05
    result = parse_penalty_bits(b9)
    assert result["penalty_right_red"] is True
    assert result["penalty_left_red"] is False
    assert result["penalty_right_yellow"] is True
    assert result["penalty_left_yellow"] is False
