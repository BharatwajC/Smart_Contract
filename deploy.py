import json

from web3 import Web3

# In the video, we forget to `install_solc`
# from solcx import compile_standard
from solcx import compile_standard, install_solc
import os

from dotenv import load_dotenv

load_dotenv("./.env")


with open("./SimpleStorage.sol", "r") as file:
    simple_storage_file = (
        file.read()
    )  # print(simple_storage_storage)   gonna give us this entire code

# We add these two lines that we forgot from the video!
# print("Installing...")
# install_solc("0.6.0")

# Solidity source code
# we installed pysolcx for compiling

compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"SimpleStorage.sol": {"content": simple_storage_file}},
        "settings": {
            "outputSelection": {
                "*": {
                    "*": [
                        "abi",
                        "metadata",
                        "evm.bytecode",
                        "evm.bytecode.sourceMap",
                    ]  # Our ABI is json ABI (copied from remix)
                }
            }
        },
    },
    solc_version="0.6.0",
)

with open("compiled_code.json", "w") as file:
    json.dump(compiled_sol, file)

# first get bytecode
bytecode = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["evm"][
    "bytecode"
]["object"]

# Next get abi
abi = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["abi"]

# Now we need an environment to deploy it so
## w3 = Web3(Web3.HTTPProvider(os.getenv("RINKEBY_RPC_URL")))
# # chain_id = 4
# #
# For connecting to rinkeby test net
w3 = Web3(
    Web3.HTTPProvider("https://rinkeby.infura.io/v3/86527d20c9f4480ba5e26e58f74365d9")
)  # ganache rpc server    Infura rinkeby address endpoint
chain_id = 4  # Network ID from Ganache   1337 alone is working i tried network id but its showing trace back error
# chain id for rinkeby is 4  (chainlist.org)
my_address = "0x1bFD26f5198db4581D10c6f51933979264af2684"
private_key = os.getenv("PRIVATE_KEY")
# print(private_key)  always add 0x at front because python is gonna look for hexadecimal version of private key


# Create the contract in Python
SimpleStorage = w3.eth.contract(
    abi=abi, bytecode=bytecode
)  # print(SimpleStorage)   output is <class 'web3._utils.datatypes.Contract'>


# 1.) Build the Contract Deploy Transaction          2.) Sign the transaction            3.) Send the Transaction

# Get the latest transaction

nonce = w3.eth.getTransactionCount(
    my_address
)  # Nonce in this context just tracks the number of transactions made        print(nonce)  o/p 0 as of now


# Submit the transaction that deploys the contract
transaction = SimpleStorage.constructor().buildTransaction(
    {
        "chainId": chain_id,
        "gasPrice": w3.eth.gas_price,
        "from": my_address,
        "nonce": nonce,
    }
)  # SimpleStorage constructor

# print(transaction)  we have this transaction but we need to sign it!

# # Sign the transaction  with our private key

signed_txn = w3.eth.account.sign_transaction(transaction, private_key=private_key)
# print(signed_txn)

# Now its really bad to store of private key in this formar (github) so store these in environment variable
print("Deploying Contract!")
# Send it!
tx_hash = w3.eth.send_raw_transaction(
    signed_txn.rawTransaction
)  # This will our transaction to local blockchain   checkout ganache
# # Wait for the transaction to be mined, and get the transaction receipt
print("Waiting for transaction to finish...")
tx_receipt = w3.eth.wait_for_transaction_receipt(
    tx_hash
)  # waiting for the transaction to finish
print("Deployed!!")
# print(f"Done! Contract deployed to {tx_receipt.contractAddress}")

# While working on chain we often need
# contract address and contract abi


# Working with deployed Contracts

simple_storage = w3.eth.contract(address=tx_receipt.contractAddress, abi=abi)

# Call -> Simulate making the call amd getting return value
# Transact -> Actually making a state change

print(
    simple_storage.functions.retrieve().call()
)  # Calling the retrieve function in simple_storage contract

# Even you can access store() and make to return uint256 and try it works with call but it doesnt change the state
# its just simulation
print("updating contract...")
store_transaction = simple_storage.functions.store(15).buildTransaction(
    {
        "chainId": chain_id,
        "gasPrice": w3.eth.gas_price,
        "from": my_address,
        "nonce": nonce + 1,
    }
)

signed_store_txn = w3.eth.account.sign_transaction(
    store_transaction, private_key=private_key
)

send_store_tx = w3.eth.send_raw_transaction(signed_store_txn.rawTransaction)

tx_receipt = w3.eth.wait_for_transaction_receipt(send_store_tx)

print("updated!!")
print(
    simple_storage.functions.retrieve().call()
)  # During this call the favorite number is changed so it=he output will be 15
# print(f"Initial Stored Value {simple_storage.functions.retrieve().call()}")
# greeting_transaction = simple_storage.functions.store(15).buildTransaction(
#     {
#         "chainId": chain_id,
#         "gasPrice": w3.eth.gas_price,
#         "from": my_address,
#         "nonce": nonce + 1,
#     }
# )
# signed_greeting_txn = w3.eth.account.sign_transaction(
#     greeting_transaction, private_key=private_key
# )
# tx_greeting_hash = w3.eth.send_raw_transaction(signed_greeting_txn.rawTransaction)
# print("Updating stored Value...")
# tx_receipt = w3.eth.wait_for_transaction_receipt(tx_greeting_hash)

# print(simple_storage.functions.retrieve().call())
