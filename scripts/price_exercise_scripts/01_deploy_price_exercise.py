from scripts.deploy_mocks import deploy_mocks
from scripts.helpful_scripts import (
    get_account,
    get_verify_status,
    LOCAL_BLOCKCHAIN_ENVIRONMENTS,
)
from brownie import MockV3Aggregator, PriceExercise, LinkToken, MockOracle, config, network


def deploy_price_exercise():
    jobId = config["networks"][network.show_active()]["jobId"]
    fee = config["networks"][network.show_active()]["fee"]
    account = get_account()
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        if len(MockOracle) <= 0:
            deploy_mocks()
        oracle = MockOracle[-1].address
        link_token = LinkToken[-1].address
        btc_usd_price_feed = MockV3Aggregator[-1].address
    else:
        btc_usd_price_feed = config["networks"][network.show_active(
        )]["btc_usd_price_feed"]
        oracle = config["networks"][network.show_active()]["oracle"]
        link_token = config["networks"][network.show_active()]["link_token"]
        price_exercise = PriceExercise.deploy(
            oracle,
            jobId,
            fee,
            link_token,
            btc_usd_price_feed,
            {"from": account},
            publish_source=get_verify_status(),
        )
        print(f"Price Exercise deployed to {price_exercise.address}")


def main():
    deploy_price_exercise()
