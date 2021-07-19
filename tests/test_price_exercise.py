import time
import pytest
from brownie import PriceExercise, network
from scripts.helpful_scripts import LOCAL_BLOCKCHAIN_ENVIRONMENTS, get_account, get_contract


@pytest.fixture
def deploy_price_exercise(get_job_id, chainlink_fee):
    # Arrange / Act
    price_exercise = PriceExercise.deploy(
        get_contract("oracle").address,
        get_job_id,
        chainlink_fee,
        get_contract("link_token").address,
        get_contract("btc_usd_price_feed").address,
        {"from": get_account()},
    )
    # Assert
    assert price_exercise is not None
    return price_exercise


def test_send_api_request_local(
    deploy_price_exercise,
    chainlink_fee,
    get_data,
):
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only for local testing")
    price_exercise = deploy_price_exercise
    get_contract("link_token").transfer(
        price_exercise.address, chainlink_fee * 2, {"from": get_account()}
    )
    # Act
    transaction_receipt = price_exercise.requestPriceData(
        {"from": get_account()})
    requestId = transaction_receipt.events["ChainlinkRequested"]["id"]
    # Assert
    get_contract("oracle").fulfillOracleRequest(
        requestId, get_data, {"from": get_account()})
    assert isinstance(price_exercise.priceFeedGreater(), bool)


def test_send_api_request_testnet(deploy_price_exercise, chainlink_fee):
    # Arrange
    if network.show_active() not in ["kovan", "rinkeby", "mainnet"]:
        pytest.skip("Only for local testing")
    price_exercise = deploy_price_exercise
    get_contract("link_token").transfer(
        price_exercise.address, chainlink_fee * 2, {"from": get_account()}
    )
    # Act
    transaction = price_exercise.requestPriceData({"from": get_account()})
    # Assert
    assert transaction is not None
    transaction.wait(2)
    time.sleep(35)
    assert isinstance(price_exercise.priceFeedGreater(), bool)


def test_can_get_latest_price(get_job_id, chainlink_fee):
    # Arrange / Act
    price_exercise = PriceExercise.deploy(
        get_contract("oracle").address,
        get_job_id,
        chainlink_fee,
        get_contract("link_token").address,
        get_contract("btc_usd_price_feed"),
        {"from": get_account()},
    )
    # Assert
    value = price_exercise.getLatestPrice()
    assert isinstance(value, int)
    assert value > 0
