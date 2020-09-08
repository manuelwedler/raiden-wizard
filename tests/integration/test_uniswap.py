import os
import time

import pytest
from tests.constants import TESTING_KEYSTORE_FOLDER
from tests.fixtures import create_account, test_password
from tests.utils import empty_account

from raiden_installer.constants import WEB3_TIMEOUT
from raiden_installer.ethereum_rpc import Infura, make_web3_provider
from raiden_installer.network import Network
from raiden_installer.token_exchange import ExchangeError, Uniswap
from raiden_installer.tokens import Erc20Token, EthereumAmount, TokenAmount
from raiden_installer.transactions import approve, get_token_balance, mint_tokens
from raiden_installer.uniswap.web3 import contracts as uniswap_contracts
from raiden_installer.utils import estimate_gas, send_raw_transaction, wait_for_transaction

INFURA_PROJECT_ID = os.getenv("TEST_RAIDEN_INSTALLER_INFURA_PROJECT_ID")
WAIT_TIME = 15  # Makes sure that transactions are discovered due to how Infura works

WIZ_EXCHANGE_ADDRESS = "0x86E21A295782649f1d7bC3fB360b4AeDd17b6E37"

NETWORK = Network.get_by_name("goerli")
WIZ_TOKEN = Erc20Token.find_by_ticker("WIZ", NETWORK.name)
GAS_LIMIT = 120_000


def fund_account(account, w3):
    NETWORK.fund(account)
    account.wait_for_ethereum_funds(w3, EthereumAmount(0.01))
    time.sleep(WAIT_TIME)


def generateDeadline(w3):
    current_timestamp = w3.eth.getBlock('latest')['timestamp']
    return current_timestamp + WEB3_TIMEOUT


def addLiquidity(w3, account, exchange_proxy):
    max_tokens = get_token_balance(w3, account, WIZ_TOKEN)

    approve(w3, account, WIZ_EXCHANGE_ADDRESS, max_tokens.as_wei, WIZ_TOKEN)

    min_liquidity = 1
    deadline = generateDeadline(w3)
    transaction_params = {
        "from": account.address,
        "value": EthereumAmount(0.001).as_wei,
        "gas_price": w3.eth.generateGasPrice(),
        "gas": GAS_LIMIT,
    }

    tx_receipt = send_raw_transaction(
        w3,
        account,
        exchange_proxy.functions.addLiquidity,
        min_liquidity,
        max_tokens.as_wei,
        deadline,
        **transaction_params,
    )
    wait_for_transaction(w3, tx_receipt)
    time.sleep(WAIT_TIME)


def removeLiquidity(w3, account, exchange_proxy):
    time.sleep(WAIT_TIME)
    amount = exchange_proxy.functions.balanceOf(account.address).call()
    min_eth = 1
    min_tokens = 1
    deadline = generateDeadline(w3)
    transaction_params = {
        "from": account.address,
        "gas_price": w3.eth.generateGasPrice(),
        "gas": GAS_LIMIT,
    }

    tx_receipt = send_raw_transaction(
        w3,
        account,
        exchange_proxy.functions.removeLiquidity,
        amount,
        min_eth,
        min_tokens,
        deadline,
        **transaction_params,
    )
    wait_for_transaction(w3, tx_receipt)
    time.sleep(WAIT_TIME)


@pytest.fixture
def patch_exchange_address(monkeypatch):
    monkeypatch.setitem(Uniswap.EXCHANGE_ADDRESSES, "WIZ", {NETWORK.name: WIZ_EXCHANGE_ADDRESS})


@pytest.fixture
def infura():
    assert INFURA_PROJECT_ID
    return Infura.make(NETWORK, INFURA_PROJECT_ID)


@pytest.fixture
def provide_liquidity(infura, create_account):
    account = create_account()
    w3 = make_web3_provider(infura.url, account)

    fund_account(account, w3)
    tx_receipt = mint_tokens(w3, account, WIZ_TOKEN)
    wait_for_transaction(w3, tx_receipt)
    time.sleep(WAIT_TIME)

    exchange_proxy = w3.eth.contract(
        abi=uniswap_contracts.UNISWAP_EXCHANGE_ABI,
        address=WIZ_EXCHANGE_ADDRESS,
    )
    addLiquidity(w3, account, exchange_proxy)
    yield
    removeLiquidity(w3, account, exchange_proxy)
    empty_account(w3, account)


@pytest.fixture
def test_account(create_account):
    return create_account()


@pytest.fixture
def funded_account(test_account, uniswap):
    fund_account(test_account, uniswap.w3)
    yield test_account
    empty_account(uniswap.w3, test_account)


@pytest.fixture
def uniswap(test_account, infura):
    w3 = make_web3_provider(infura.url, test_account)
    return Uniswap(w3)


def test_buy_tokens(funded_account, provide_liquidity, patch_exchange_address, uniswap):
    w3 = uniswap.w3
    wiz_balance_before = get_token_balance(w3, funded_account, WIZ_TOKEN)
    buy_amount = TokenAmount(1, WIZ_TOKEN)
    tx_receipt = uniswap.buy_tokens(funded_account, buy_amount)
    wait_for_transaction(w3, tx_receipt)
    time.sleep(WAIT_TIME)
    wiz_balance_after = get_token_balance(w3, funded_account, WIZ_TOKEN)
    assert wiz_balance_after == wiz_balance_before + buy_amount


def test_cannot_buy_on_unsupported_network(funded_account, provide_liquidity, uniswap):
    with pytest.raises(ExchangeError):
        uniswap.buy_tokens(funded_account, TokenAmount(1, WIZ_TOKEN))


def test_cannot_buy_zero_tokens(funded_account, provide_liquidity, patch_exchange_address, uniswap):
    with pytest.raises(ExchangeError):
        uniswap.buy_tokens(funded_account, TokenAmount(0, WIZ_TOKEN))


def test_cannot_buy_without_eth(test_account, provide_liquidity, patch_exchange_address, uniswap):
    with pytest.raises(ValueError):
        uniswap.buy_tokens(test_account, TokenAmount(1, WIZ_TOKEN))
