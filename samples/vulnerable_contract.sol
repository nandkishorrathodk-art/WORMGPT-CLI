// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract VulnerableBank {
    mapping(address => uint256) public balances;
    address public owner;
    
    constructor() {
        owner = msg.sender;
    }
    
    function deposit() public payable {
        balances[msg.sender] += msg.value;
    }
    
    function withdraw() public {
        uint256 amount = balances[msg.sender];
        require(amount > 0, "Insufficient balance");
        
        (bool success, ) = msg.sender.call{value: amount}("");
        require(success, "Transfer failed");
        
        balances[msg.sender] = 0;
    }
    
    function sendEth(address recipient, uint256 amount) public {
        require(balances[msg.sender] >= amount, "Insufficient balance");
        
        (bool success, ) = recipient.call{value: amount}("");
        require(success, "Transfer failed");
        
        balances[msg.sender] -= amount;
    }
    
    function checkBalance(address user) public view returns (uint256) {
        return balances[user];
    }
    
    function transferOwnership(address newOwner) public {
        require(tx.origin == owner, "Not owner");
        owner = newOwner;
    }
    
    function emergencyWithdraw() public {
        require(msg.sender == owner, "Not owner");
        payable(owner).transfer(address(this).balance);
    }
    
    receive() external payable {
        deposit();
    }
}


contract InsecureToken {
    mapping(address => uint256) public balances;
    uint256 public totalSupply;
    address public admin;
    
    constructor(uint256 initialSupply) {
        balances[msg.sender] = initialSupply;
        totalSupply = initialSupply;
        admin = msg.sender;
    }
    
    function transfer(address to, uint256 amount) public returns (bool) {
        require(balances[msg.sender] >= amount, "Insufficient balance");
        
        balances[msg.sender] -= amount;
        balances[to] += amount;
        
        return true;
    }
    
    function mint(address to, uint256 amount) public {
        balances[to] += amount;
        totalSupply += amount;
    }
    
    function burn(uint256 amount) public {
        require(balances[msg.sender] >= amount, "Insufficient balance");
        balances[msg.sender] -= amount;
        totalSupply -= amount;
    }
}


contract UnsafeAuction {
    address public highestBidder;
    uint256 public highestBid;
    mapping(address => uint256) public pendingReturns;
    bool public ended;
    
    function bid() public payable {
        require(!ended, "Auction ended");
        require(msg.value > highestBid, "Bid too low");
        
        if (highestBidder != address(0)) {
            pendingReturns[highestBidder] += highestBid;
        }
        
        highestBidder = msg.sender;
        highestBid = msg.value;
    }
    
    function withdraw() public {
        uint256 amount = pendingReturns[msg.sender];
        require(amount > 0, "No funds to withdraw");
        
        (bool success, ) = msg.sender.call{value: amount}("");
        require(success, "Transfer failed");
        
        pendingReturns[msg.sender] = 0;
    }
    
    function endAuction() public {
        ended = true;
    }
}


contract DelegateCallVulnerable {
    address public owner;
    uint256 public value;
    
    constructor() {
        owner = msg.sender;
    }
    
    function callExternalContract(address target, bytes memory data) public {
        (bool success, ) = target.delegatecall(data);
        require(success, "Delegatecall failed");
    }
    
    function setValue(uint256 newValue) public {
        value = newValue;
    }
}


contract TimestampDependency {
    uint256 public lastUpdateTime;
    mapping(address => bool) public hasClaimedReward;
    
    function claimDailyReward() public {
        require(block.timestamp >= lastUpdateTime + 1 days, "Too early");
        require(!hasClaimedReward[msg.sender], "Already claimed");
        
        hasClaimedReward[msg.sender] = true;
        lastUpdateTime = block.timestamp;
        
        payable(msg.sender).transfer(1 ether);
    }
    
    function resetClaim(address user) public {
        hasClaimedReward[user] = false;
    }
}
