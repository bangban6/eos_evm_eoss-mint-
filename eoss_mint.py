from web3 import Web3, exceptions
from web3.middleware import geth_poa_middleware
import threading
import time

# 配置信息
chain_id = 0x4571  # EOS EVM 链的链 ID
rpc_server = "https://api.evm.eosnetwork.com/"
gas_price = Web3.to_wei(150, 'gwei')  # 150 Gwei 的 Gas 价格
gas_limit = 32940  # Gas 限制

# 连接到 RPC 服务器
w3 = Web3(Web3.HTTPProvider(rpc_server))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)

# 私钥列表
private_key_list = [
    '输入你的私钥1',
    '输入你的私钥2',
    '输入你的私钥3',
    '输入你的私钥4',

]


# 获取当前 nonce 的函数
def get_current_nonce(account):
    try:
        nonce = w3.eth.get_transaction_count(account.address)
        print(f"{account.address} 当前nonce : {nonce}")
        return nonce
    except Exception as e:
        print(f"获取 nonce 出错: {e}")


# 发送交易的函数
def send_transaction(account, nonce):
    tx_data = {
        'nonce': nonce,
        'gasPrice': gas_price,
        'gas': gas_limit,
        'to': account.address,
        'value': 0,
        'data': '0x646174613a2c7b2270223a22656f72633230222c226f70223a226d696e74222c227469636b223a22656f7373222c22616d74223a223130303030227d',
        'chainId': chain_id
    }
    signed_txn = account.sign_transaction(tx_data)
    current_address = account.address;
    while True:
        try:
            tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            #  {tx_hash.hex()}
            print(f"{current_address} 正在铸造（铭文 {nonce}）")

            for _ in range(5):
                try:
                    receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
                    # print(f"交易确认（nonce {nonce}）: {receipt}")
                    print(f"{current_address} 铸造成功,铭文数量 => {nonce} ")
                    return
                except exceptions.TimeExhausted:
                    ...
                    print(f"等待交易收据超时，正在重试...（nonce {nonce}）")
            print(f"{current_address}重试铸造（铭文 {nonce}）")

        except Exception as e:
            print(f"{current_address}铸造出错（铭文ID {nonce}）: {e}")
            time.sleep(10)


# 执行交易的主函数
def execute_transactions_with_key(private_key):
    account = w3.eth.account.from_key(private_key)
    start_nonce = get_current_nonce(account)
    end_nonce = 1000  # 根据需要调整
    if start_nonce >= end_nonce:
        print(f"账户{account.address} 铭文铸造完成,总量 => {start_nonce}")
        return
    for nonce in range(start_nonce, end_nonce + 1):
        send_transaction(account, nonce)


# 为每个私钥创建并启动一个线程
threads = []
for key in private_key_list:
    t = threading.Thread(target=execute_transactions_with_key, args=(key,))
    threads.append(t)
    t.start()

# 等待所有线程完成
for t in threads:
    t.join()

print("所有交易执行完毕")
