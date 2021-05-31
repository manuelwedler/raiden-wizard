from dataclasses import dataclass, field, replace
from decimal import Decimal, getcontext
from enum import Enum
from typing import Dict, Generic, NewType, Optional, TypeVar

from eth_typing import Address
from eth_utils import to_canonical_address

from raiden_contracts.constants import CONTRACTS_VERSION

Eth_T = TypeVar("Eth_T", int, Decimal, float, str, "Wei")
Token_T = TypeVar("Token_T")
TokenTicker = NewType("TokenTicker", str)


class TokenError(Exception):
    pass


class Wei(int):
    pass


@dataclass
class Currency:
    ticker: str
    wei_ticker: str
    decimals: int = 18

    def format_value(self, wei_amount: Decimal):
        if wei_amount == 0:
            ticker = self.ticker
            value = wei_amount
        elif wei_amount >= 10 ** 15:
            ticker = self.ticker
            value = wei_amount / 10 ** self.decimals
        elif 10 ** 12 <= wei_amount < 10 ** 15:
            ticker = "T" + self.wei_ticker
            value = wei_amount / 10 ** 12
        elif 10 ** 9 <= wei_amount < 10 ** 12:
            ticker = "G" + self.wei_ticker
            value = wei_amount / 10 ** 9
        elif 10 ** 6 <= wei_amount < 10 ** 9:
            ticker = "M" + self.wei_ticker
            value = wei_amount / 10 ** 6
        else:
            ticker = self.wei_ticker
            value = wei_amount

        integral = int(value)
        frac = value % 1
        frac_string = f"{frac:.3g}"[1:] if frac else ""

        return f"{integral}{frac_string} {ticker}"


@dataclass
class Erc20Token(Currency):
    address: Address = Address(b"")
    supply: int = 10 ** 21

    def __post_init__(self):
        if self.address == Address(b""):
            raise TokenError("Erc20Token should not get initialized without an address")

    @staticmethod
    def find_by_ticker(ticker, network_name):
        major, minor, _ = CONTRACTS_VERSION.split(".", 2)
        version_string = f"{major}.{minor}"
        token_list_version = {
            "0.25": TokensV25,
            "0.33": TokensV33,
            "0.36": TokensV36,
            "0.37": TokensV37,
        }.get(version_string, Tokens)
        try:
            token_data = token_list_version[ticker].value
            address = token_data.addresses[network_name]
        except KeyError as exc:
            raise TokenError(f"{ticker} is not deployed on {network_name}") from exc

        return Erc20Token(
            ticker=token_data.ticker,
            wei_ticker=token_data.wei_ticker,
            address=to_canonical_address(address)
        )


class CurrencyAmount(Generic[Eth_T]):
    def __init__(self, value: Eth_T, currency: Currency):
        context = getcontext()
        context.prec = currency.decimals
        self.value = Decimal(str(value), context=context)
        if type(value) is Wei:
            self.value /= 10 ** currency.decimals

        self.currency = currency

    @property
    def ticker(self) -> TokenTicker:
        ticker = self.currency.ticker
        return TokenTicker(ticker)

    @property
    def formatted(self):
        return self.currency.format_value(Decimal(self.as_wei))

    @property
    def as_wei(self) -> Wei:
        return Wei(self.value * (10 ** self.currency.decimals))

    def __repr__(self):
        return f"{self.value} {self.ticker}"

    def __add__(self, other):
        if not self.currency == other.currency:
            raise ValueError(f"Cannot add {self.formatted} and {other.formatted}")

        return CurrencyAmount(Wei(self.as_wei + other.as_wei), self.currency)

    def __sub__(self, other):
        if not self.currency == other.currency:
            raise ValueError(f"Cannot sub {self.formatted} and {other.formatted}")

        return CurrencyAmount(Wei(self.as_wei - other.as_wei), self.currency)

    def __eq__(self, other):
        return self.currency == other.currency and self.as_wei == other.as_wei

    def __lt__(self, other):
        if not self.currency == other.currency:
            raise ValueError(f"Cannot compare {self.currency} with {other.currency}")
        return self.as_wei < other.as_wei

    def __le__(self, other):
        if not self.currency == other.currency:
            raise ValueError(f"Cannot compare {self.currency} with {other.currency}")

        return self.as_wei <= other.as_wei

    def __gt__(self, other):
        if not self.currency == other.currency:
            raise ValueError(f"Cannot compare {self.currency} with {other.currency}")
        return self.as_wei > other.as_wei

    def __ge__(self, other):
        if not self.currency == other.currency:
            raise ValueError(f"Cannot compare {self.currency} with {other.currency}")

        return self.as_wei >= other.as_wei


class TokenAmount(CurrencyAmount):
    def __init__(self, value: Eth_T, currency: Erc20Token):
        super().__init__(value, currency)
        self.address = currency.address


ETH = Currency(ticker="ETH", wei_ticker="WEI")


class EthereumAmount(CurrencyAmount):
    def __init__(self, value: Eth_T):
        super().__init__(value, ETH)


@dataclass(frozen=True)
class TokenData:
    ticker: str
    wei_ticker: str
    addresses: Dict[str, str]


_RDN = TokenData(
    ticker="RDN",
    wei_ticker="REI",
    addresses={
        "mainnet": "0x255aa6df07540cb5d3d297f0d0d4d84cb52bc8e6",
        "goerli": "0x709118121A1ccA0f32FC2C0c59752E8FEE3c2834",
        "ropsten": "0x5422Ef695ED0B1213e2B953CFA877029637D9D26",
        "rinkeby": "0x51892e7e4085df269de688b273209f3969f547e0",
        "kovan": "0x3a03155696708f517c53ffc4f696dfbfa7743795",
    },
)

_DAI = TokenData(
    ticker="DAI",
    wei_ticker="DEI",
    addresses={
        "mainnet": "0x6b175474e89094c44da98b954eedeac495271d0f",
        "kovan": "0x4f96fe3b7a6cf9725f59d353f723c1bdb64ca6aa",
        "rinkeby": "0xc3dbf84Abb494ce5199D5d4D815b10EC29529ff8"
    },
)

_WizardToken = TokenData(
    ticker="WIZ",
    wei_ticker="WEI",
    addresses={"goerli": "0x95b2d84de40a0121061b105e6b54016a49621b44"},
)


class Tokens(Enum):
    RDN = _RDN
    DAI = _DAI
    WIZ = _WizardToken


class TokensV25(Enum):
    RDN = replace(
        _RDN,
        addresses={
            "mainnet": "0x255aa6df07540cb5d3d297f0d0d4d84cb52bc8e6",
            "goerli": "0x3a989d97388a39a0b5796306c615d10b7416be77",
        },
    )


class TokensV33(Enum):
    RDN = replace(
        _RDN,
        addresses={
            "mainnet": "0x255aa6df07540cb5d3d297f0d0d4d84cb52bc8e6",
            "goerli": "0x709118121A1ccA0f32FC2C0c59752E8FEE3c2834",
        },
    )
    DAI = _DAI
    WIZ = _WizardToken


class TokensV36(Enum):
    RDN = replace(
        _RDN,
        addresses={"goerli": "0x4074fD4d460d0c31cbEdC3f59B2D98626D063952"},
    )
    DAI = _DAI
    WIZ = _WizardToken


class TokensV37(Enum):
    RDN = replace(
        _RDN,
        addresses={"mainnet": "0x255aa6df07540cb5d3d297f0d0d4d84cb52bc8e6",
                   "rinkeby": "0x2488c9445b405e0fbbd60e89813f8b8652973737", },
    )
    SVT = TokenData(
        ticker="SVT",
        wei_ticker="SEI",
        addresses={"goerli": "0x5Fc523e13fBAc2140F056AD7A96De2cC0C4Cc63A"},
    )
    DAI = _DAI
    WIZ = _WizardToken


@dataclass
class RequiredAmounts:
    eth: EthereumAmount
    eth_after_swap: EthereumAmount
    service_token: TokenAmount
    transfer_token: TokenAmount

    @staticmethod
    def from_settings(settings):
        return RequiredAmounts(
            eth=EthereumAmount(Wei(settings.ethereum_amount_required)),
            eth_after_swap=EthereumAmount(Wei(settings.ethereum_amount_required_after_swap)),
            service_token=TokenAmount(
                Wei(settings.service_token.amount_required),
                Erc20Token.find_by_ticker(settings.service_token.ticker, settings.network),
            ),
            transfer_token=TokenAmount(
                Wei(settings.transfer_token.amount_required),
                Erc20Token.find_by_ticker(settings.transfer_token.ticker, settings.network),
            ),
        )


@dataclass
class SwapAmounts:
    service_token: TokenAmount
    transfer_token: TokenAmount

    @staticmethod
    def from_settings(settings):
        return SwapAmounts(
            service_token=TokenAmount(
                Wei(settings.service_token.swap_amount),
                Erc20Token.find_by_ticker(settings.service_token.ticker, settings.network),
            ),
            transfer_token=TokenAmount(
                Wei(settings.transfer_token.swap_amount),
                Erc20Token.find_by_ticker(settings.transfer_token.ticker, settings.network),
            ),
        )
