"""
区块链验证模块
使用区块链技术确保审核结果的不可篡改性和透明度
"""

import hashlib
import json
import time
from typing import Dict, List, Any, Optional
from web3 import Web3
from eth_account import Account
import requests


class BlockchainVerifier:
    """区块链验证器"""
    
    def __init__(self, network='ethereum', contract_address=None):
        """
        初始化区块链验证器
        
        Args:
            network: 区块链网络 (ethereum, polygon, bsc)
            contract_address: 智能合约地址
        """
        self.network = network
        self.contract_address = contract_address
        
        # 连接区块链
        self._connect_blockchain()
        
        # 审核记录链
        self.audit_chain = []
    
    def _connect_blockchain(self):
        """连接区块链网络"""
        if self.network == 'ethereum':
            self.w3 = Web3(Web3.HTTPProvider('https://mainnet.infura.io/v3/YOUR-PROJECT-ID'))
        elif self.network == 'polygon':
            self.w3 = Web3(Web3.HTTPProvider('https://polygon-rpc.com'))
        elif self.network == 'bsc':
            self.w3 = Web3(Web3.HTTPProvider('https://bsc-dataseed.binance.org'))
        
        # 加载智能合约
        if self.contract_address:
            self.contract = self.w3.eth.contract(
                address=self.contract_address,
                abi=self._load_contract_abi()
            )
    
    def _load_contract_abi(self) -> List[Dict]:
        """加载智能合约ABI"""
        # 审计合约的ABI
        return [
            {
                "inputs": [
                    {"name": "plugin_hash", "type": "string"},
                    {"name": "audit_result_hash", "type": "string"},
                    {"name": "score", "type": "uint256"},
                    {"name": "auditor", "type": "address"}
                ],
                "name": "submitAuditResult",
                "outputs": [{"name": "audit_id", "type": "uint256"}],
                "type": "function"
            },
            {
                "inputs": [{"name": "audit_id", "type": "uint256"}],
                "name": "getAuditResult",
                "outputs": [
                    {"name": "plugin_hash", "type": "string"},
                    {"name": "audit_result_hash", "type": "string"},
                    {"name": "score", "type": "uint256"},
                    {"name": "auditor", "type": "address"},
                    {"name": "timestamp", "type": "uint256"}
                ],
                "type": "function"
            }
        ]
    
    def submit_audit_result(self, plugin_path: str, audit_result: Dict, private_key: str) -> str:
        """
        提交审核结果到区块链
        
        Returns:
            transaction_hash: 交易哈希
        """
        # 计算插件哈希
        plugin_hash = self._calculate_file_hash(plugin_path)
        
        # 计算审核结果哈希
        audit_result_hash = self._calculate_audit_hash(audit_result)
        
        # 准备交易
        account = Account.from_key(private_key)
        nonce = self.w3.eth.get_transaction_count(account.address)
        
        # 调用智能合约
        if self.contract:
            tx = self.contract.functions.submitAuditResult(
                plugin_hash,
                audit_result_hash,
                int(audit_result.get('overall_score', 0) * 100),  # 分数转换为整数
                account.address
            ).build_transaction({
                'from': account.address,
                'nonce': nonce,
                'gas': 200000,
                'gasPrice': self.w3.eth.gas_price
            })
        else:
            # 如果没有智能合约，创建交易
            data = {
                'plugin_hash': plugin_hash,
                'audit_result_hash': audit_result_hash,
                'score': audit_result.get('overall_score', 0),
                'auditor': account.address,
                'timestamp': time.time(),
                'audit_result': audit_result  # 完整结果（可能太大）
            }
            
            tx = {
                'from': account.address,
                'to': account.address,  # 发送给自己
                'value': 0,
                'gas': 100000,
                'gasPrice': self.w3.eth.gas_price,
                'nonce': nonce,
                'data': self.w3.to_hex(text=json.dumps(data))
            }
        
        # 签名并发送交易
        signed_tx = account.sign_transaction(tx)
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        
        # 添加到本地链
        self.audit_chain.append({
            'transaction_hash': tx_hash.hex(),
            'plugin_hash': plugin_hash,
            'timestamp': time.time(),
            'audit_result_hash': audit_result_hash
        })
        
        return tx_hash.hex()
    
    def verify_audit_result(self, audit_id: int) -> Dict[str, Any]:
        """
        验证审核结果是否在区块链上
    
        Args:
            audit_id: 审核ID
            
        Returns:
            验证结果
        """
        result = {
            'verified': False,
            'audit_data': None,
            'blockchain_data': None,
            'integrity_check': False
        }
        
        try:
            if self.contract:
                # 从区块链获取审核数据
                blockchain_data = self.contract.functions.getAuditResult(audit_id).call()
                
                result['blockchain_data'] = {
                    'plugin_hash': blockchain_data[0],
                    'audit_result_hash': blockchain_data[1],
                    'score': blockchain_data[2],
                    'auditor': blockchain_data[3],
                    'timestamp': blockchain_data[4]
                }
                
                # 查找本地审核记录
                local_audit = self._find_local_audit(audit_id)
                
                if local_audit:
                    # 验证哈希
                    local_hash = self._calculate_audit_hash(local_audit)
                    result['integrity_check'] = local_hash == result['blockchain_data']['audit_result_hash']
                    
                    result['audit_data'] = local_audit
                    result['verified'] = result['integrity_check']
                
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def create_audit_nft(self, plugin_name: str, audit_result: Dict) -> str:
        """
        创建审核NFT（非同质化代币）
        
        Returns:
            nft_token_id: NFT令牌ID
        """
        # 生成NFT元数据
        nft_metadata = {
            'name': f"Plugin Audit: {plugin_name}",
            'description': f"OpenClaw插件审核证书 - 分数: {audit_result['overall_score']}/100",
            'image': self._generate_audit_certificate_image(audit_result),
            'attributes': [
                {'trait_type': 'Score', 'value': audit_result['overall_score']},
                {'trait_type': 'Risk Level', 'value': audit_result.get('risk_level', 'unknown')},
                {'trait_type': 'Audit Date', 'value': audit_result['timestamp']},
                {'trait_type': 'Audit Level', 'value': audit_result.get('audit_level', 'standard')}
            ]
        }
        
        # 上传元数据到IPFS
        ipfs_hash = self._upload_to_ipfs(nft_metadata)
        
        # 铸造NFT
        token_id = self._mint_nft(ipfs_hash)
        
        return token_id
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """计算文件SHA-256哈希"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    def _calculate_audit_hash(self, audit_result: Dict) -> str:
        """计算审核结果哈希"""
        # 移除时间戳等可变字段
        stable_data = {
            'plugin_path': audit_result.get('plugin_path'),
            'overall_score': audit_result.get('overall_score'),
            'passed': audit_result.get('passed'),
            'vulnerabilities': audit_result.get('vulnerabilities', []),
            'recommendations': audit_result.get('recommendations', [])
        }
        
        json_str = json.dumps(stable_data, sort_keys=True)
        return hashlib.sha256(json_str.encode()).hexdigest()
    
    def _find_local_audit(self, audit_id: int) -> Optional[Dict]:
        """查找本地审核记录"""
        # 从数据库或文件系统加载
        # 简化实现
        return None
    
    def _generate_audit_certificate_image(self, audit_result: Dict) -> str:
        """生成审核证书图片"""
        # 使用PIL或其他库生成证书图片
        # 返回IPFS哈希或URL
        return "ipfs://QmCertificateHash"
    
    def _upload_to_ipfs(self, data: Dict) -> str:
        """上传数据到IPFS"""
        # 使用IPFS客户端上传
        # 简化实现
        return "QmIPFSHash"
    
    def _mint_nft(self, metadata_uri: str) -> str:
        """铸造NFT"""
        # 调用NFT智能合约
        # 返回token_id
        return "token_id_123456"