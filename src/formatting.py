"""Funções de formatação de números no padrão brasileiro (ponto de milhar, vírgula decimal)."""


def format_int_pt_br(value: int) -> str:
    """Formata um inteiro com ponto como separador de milhar. Ex.: 12345 -> '12.345'."""
    return f"{value:,}".replace(",", ".")


def format_currency_pt_br(value: float, symbol: str = "€") -> str:
    """Formata um valor monetário no padrão pt-BR. Ex.: 1234.5 -> '€ 1.234,50'."""
    formatted = f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{symbol} {formatted}"
