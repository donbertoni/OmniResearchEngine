from omni.domain.formatting import fmt_num, fmt_pct


def test_fmt_num_zero_and_none_show_placeholder():
    assert fmt_num(0.0) == "--"
    assert fmt_num(None) == "--"


def test_fmt_num_uses_pt_br_thousands_and_decimal_separators():
    assert fmt_num(1234.5) == "1.234,50"


def test_fmt_pct_adds_sign_and_pt_br_decimal_separator():
    assert fmt_pct(1.5) == "+1,50%"
    assert fmt_pct(-2.25) == "-2,25%"
    assert fmt_pct(None) == "0,00%"
