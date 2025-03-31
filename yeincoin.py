import datetime
import hashlib
import json
from flask import Flask, jsonify
import requests
from uuid import uuid4
from urllib.parse import urlparse

class Blockchain:

    def __init__(self):
        self.chain = []
        self.transactions = []
        self.append_block(proof = 1, previous_hash = '0')

    def create_block(self):
        # 이전블록의 작업증명 불러오기
        previous_block = blockchain.get_previous_block()
        previous_proof = previous_block['proof']

        # proof 찾기
        proof = blockchain.proof_of_work(previous_proof)

        # hash값 찾기
        previous_hash = blockchain.hash(previous_block)

        # 블록을 블록체인에 추가
        block = blockchain.append_block(proof, previous_hash)

        return block

    def append_block(self, proof, previous_hash):
        block = { 'index': len(self.chain) + 1,
                  'timestamp': str(datetime.datetime.now()),
                  'proof': proof,
                  'previous_hash': previous_hash,
                  'transactions': self.transactions}
        self.transactions = []
        self.chain.append(block)
        return block

    def get_previous_block(self):
        return self.chain[-1]

    def proof_of_work(self, previous_proof):
        new_proof = 1
        check_proof = False

        while check_proof is False:
            hash_operation = hashlib.sha256(str(new_proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] == '0000':
                check_proof = True
            else:
                new_proof += 1

        return new_proof

    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()

    def is_chain_valid(self, chain):
        block_index = 1

        while block_index < len(chain):
            previous_block = chain[block_index-1]
            block = chain[block_index]

            # 해시 확인
            # 현재 블록에 저장된 이전 해시 != 이전 블록에서 구한 해시
            if block['previous_hash'] != self.hash(previous_block):
                return False

            # PoW 확인
            previous_proof = previous_block['proof']
            proof = block['proof']
            hash_operation = hashlib.sha256(str(proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] != '0000':
                return False

            # 인덱스 업데이트
            block_index += 1

        return True

    def add_transaction(self, sender, receiver, amount):
        self.transactions.append({'sender': sender,
                                  'receiver': receiver,
                                  'amount': amount})
        return self.get_previous_block()['index'] + 1

app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

blockchain = Blockchain()

@app.route('/mine_block', methods = ['GET'])
def mine_block():
    block = blockchain.create_block()
    response = {'message': 'Congratulations, you just mined a block!'}

    for k, v in block.items():
        response[k] = v

    return jsonify(response), 200


@app.route('/get_chain', methods = ['GET'])
def get_chain():
    response = {'chain': blockchain.chain,
                'length': len(blockchain.chain)}
    return jsonify(response), 200

@app.route('/is_valid', methods = ['GET'])
def is_valid():
    return jsonify(blockchain.is_chain_valid(blockchain.chain)), 200


app.run(host = '127.0.0.1', port=8080)