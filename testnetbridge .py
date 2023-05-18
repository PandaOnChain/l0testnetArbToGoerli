
import json
from web3 import Web3

# ChainID: 42161 , L0/Arbitrum's Endpoint ChaindID: 110
RPC = "https://rpc.ankr.com/arbitrum"
web3 = Web3(Web3.HTTPProvider(RPC))


bridge_abi = json.load(open('./bridge_abi.json'))
endpoint_abi = json.load(
    open('./router_arb_abi.json'))  # Arbitrum's Endpoint
SwappableBridgeUniswapV3 = web3.to_checksum_address(
    '0x0A9f824C05A74F577A536A8A0c673183a872Dff4')
Router = web3.to_checksum_address(
    '0x53Bf833A5d6c4ddA888F69c22C88C9f356a41614')  # Stargate's router
bridge = web3.eth.contract(address=SwappableBridgeUniswapV3, abi=bridge_abi)
L0 = web3.eth.contract(address=Router, abi=endpoint_abi)


def bridge():
    key = "#########"
    account = web3.eth.account.from_key(key).address
    nonce = web3.eth.get_transaction_count(account)
    gas_price = web3.eth.gas_price
    fees = L0.functions.quoteLayerZeroFee(
        111, 1, account, "0x", [0, 0, account]).call()
    L0_fees = fees[0]
    tx = bridge.functions.swapAndBridge(
        amountIn=web3.to_wei(0.001, 'ether'),  # ETH
        amountOutMin=web3.to_wei(10, 'ether'),  # gETH
        dstChainId=154,
        to=account,
        refundAddress=account,
        zroPaymentAddress='0x0000000000000000000000000000000000000000',
        adapterParams="0x"
    ).build_transaction({
        'from': account,
        'nonce': web3.eth.get_transaction_count(account),
        'value': int(web3.from_wei(0.001, 'ether') + L0_fees + gas_price),
        'gas': 5000000,
        'gasPrice': web3.eth.gas_price})
    signed_tx = web3.eth.account.sign_transaction(tx, key)
    tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
    print(f'Transaction hash: https://arbiscan.io/tx/{tx_hash.hex()}')
    print('Waiting for receipt...')
    tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
    print('Transfer complete!')


if __name__ == '__main__':
    bridge()
