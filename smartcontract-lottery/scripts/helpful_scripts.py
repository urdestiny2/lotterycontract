from brownie import (
    network,
    accounts,
    config,
    MockV3Aggregator,
    Contract,
    VRFCoordinatorMock,
    LinkToken,
)
from brownie.network import account
from toolz.functoolz import _restore_curry

LOCAL_BLOCKCHAIN_ENVIRONMENTS = ["development", "ganache-local"]
FORKED_LOCAL_ENVIRONMENTS = ["mainnet_fork", "mainnet-fork-dev"]


def get_account(index=None, id=None):

    if index:
        return accounts[index]
    if id:
        return accounts.load(id)
    if (
        network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS
        or network.show_active() in FORKED_LOCAL_ENVIRONMENTS
    ):
        # if we are using one of the available development chains.
        return accounts[0]

    return accounts.add(
        config["wallets"]["from_key"]
    )  # else we pull an adress that we have hardcoded in some file


contract_to_mock = {
    "eth_usd_price_feed": MockV3Aggregator,
    "vrf_coordinator": VRFCoordinatorMock,
    "link_token": LinkToken,
}


def get_contract(contract_name):
    """
    This function grabs the contract address from the from the brownie config if defined, else it
    deploys the mock version of the contract and returns its address.
    """
    contract_type = contract_to_mock[contract_name]
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        if (
            len(contract_type) <= 0
        ):  # checking how many MockV3Aggregator have been deployed and if none are presently deployed then deploy one
            deploy_mocks()
        contract = contract_type[
            -1
        ]  # mock was deployed using the deploy_mocks() and now wee need to grab it.

    else:
        contract_address = config["networks"][network.show_active()][contract_name]
        # now we need address and abi to work with this grabbed contract
        contract = Contract.from_abi(
            contract_type._name, contract_address, contract_type.abi
        )

    return contract


DECIMALS = 8
INITIAL_VALUE = 200000000000


def deploy_mocks(decimals=DECIMALS, initial_value=INITIAL_VALUE):
    account = get_account()
    MockV3Aggregator.deploy(decimals, initial_value, {"from": account})
    link_token = LinkToken.deploy({"from": account})
    VRFCoordinatorMock.deploy(link_token.address, {"from": account})
    print("deployed!")


def fund_with_link(
    contract_address, account=None, link_token=None, amount=100000000000000000
):
    account = account if account else get_account()
    link_token = link_token if link_token else get_contract("link_token")
    tx = link_token.transfer(contract_address, amount, {"from": account})
    tx.wait(1)
    print("funded contract!")
    return tx
