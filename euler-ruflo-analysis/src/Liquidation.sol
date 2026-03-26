// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "./mocks/MockERC20.sol";

/**
 * @title Liquidation
 * @notice Simplified implementation of Euler's liquidation logic for testing
 * @dev Contains the same vulnerabilities as the original Euler Finance contract
 */
contract Liquidation {
    MockERC20 public immutable collateralToken;
    MockERC20 public immutable debtToken;
    
    uint256 public constant UNDERLYING_RESERVES_FEE = 20000000000000000; // 2%
    uint256 public constant LIQUIDATION_THRESHOLD = 900000000000000000; // 90%
    
    struct LiquidationOpportunity {
        uint256 healthScore;
        uint256 discount;
        uint256 conversionRate;
    }
    
    struct LiquidationLocals {
        address violator;
        address liquidator;
        uint256 underlyingPrice;
        uint256 collateralPrice;
    }
    
    mapping(address => uint256) public accountCollateral;
    mapping(address => uint256) public accountDebt;
    mapping(address => bool) public isSubAccount;
    mapping(address => address) public subAccountParent;
    
    event LiquidationExecuted(
        address indexed violator,
        address indexed liquidator,
        uint256 debtAmount,
        uint256 collateralAmount,
        uint256 discount
    );
    
    constructor(address _collateralToken, address _debtToken) {
        collateralToken = MockERC20(_collateralToken);
        debtToken = MockERC20(_debtToken);
    }
    
    /**
     * @notice Compute liquidation opportunity - CONTAINS VULNERABILITIES
     * @dev This function contains the same vulnerabilities as the original Euler Finance
     */
    function computeLiqOpp(LiquidationLocals memory liqLocs) 
        public 
        view 
        returns (LiquidationOpportunity memory liqOpp) 
    {
        // VULNERABILITY 1: Self-liquidation check bypass
        require(!isSubAccountOf(liqLocs.violator, liqLocs.liquidator), "e/liq/self-liquidation");
        
        // VULNERABILITY 2: Health score manipulation via donation attack
        (uint256 collateralValue, uint256 liabilityValue) = getAccountLiquidity(liqLocs.violator);
        
        if (liabilityValue == 0) {
            liqOpp.healthScore = type(uint256).max;
            return liqOpp; // no violation
        }
        
        liqOpp.healthScore = collateralValue * 1e18 / liabilityValue;
        
        // VULNERABILITY 3: Discount calculation manipulation
        uint256 baseDiscount = UNDERLYING_RESERVES_FEE + (1e18 - liqOpp.healthScore);
        uint256 discountBooster = computeDiscountBooster(liqLocs.liquidator, liabilityValue);
        uint256 discount = baseDiscount * discountBooster / 1e18;
        
        liqOpp.discount = discount;
        
        // VULNERABILITY 4: Conversion rate manipulation
        liqOpp.conversionRate = liqLocs.underlyingPrice * 1e18 / liqLocs.collateralPrice * 1e18 / (1e18 - discount);
    }
    
    /**
     * @notice Execute liquidation - CONTAINS DEBT TRANSFER VULNERABILITY
     */
    function executeLiquidation(
        address violator,
        address liquidator,
        uint256 repay
    ) external {
        LiquidationLocals memory liqLocs = LiquidationLocals({
            violator: violator,
            liquidator: liquidator,
            underlyingPrice: 1e18, // Simplified: assume 1:1 price
            collateralPrice: 1e18
        });
        
        LiquidationOpportunity memory liqOpp = computeLiqOpp(liqLocs);
        
        require(liqOpp.healthScore < 1e18, "Account not liquidatable");
        
        uint256 violatorCollateral = accountCollateral[violator];
        uint256 violatorDebt = accountDebt[violator];
        
        require(repay <= violatorDebt, "Repay amount too large");
        
        // Calculate collateral to transfer based on discount
        uint256 collateralToTransfer = (repay * liqOpp.conversionRate) / 1e18;
        require(collateralToTransfer <= violatorCollateral, "Insufficient collateral");
        
        // VULNERABILITY 5: Debt transfer logic flaw
        // Liquidator takes on violator's debt
        transferBorrow(violator, liquidator, repay);
        
        // Extra debt is minted for reserves - THIS IS THE CRITICAL VULNERABILITY
        uint256 repayExtra = (repay * UNDERLYING_RESERVES_FEE) / 1e18;
        increaseBorrow(liquidator, repayExtra);
        
        // Transfer collateral to liquidator
        accountCollateral[violator] -= collateralToTransfer;
        accountCollateral[liquidator] += collateralToTransfer;
        
        // VULNERABILITY 6: Reserve manipulation
        increaseReserves(repayExtra);
        
        emit LiquidationExecuted(violator, liquidator, repay, collateralToTransfer, liqOpp.discount);
    }
    
    /**
     * @notice Check if one account is a sub-account of another
     * @dev VULNERABILITY: Only checks direct relationships
     */
    function isSubAccountOf(address account, address possibleParent) public view returns (bool) {
        // This check is insufficient - doesn't detect indirect relationships
        return subAccountParent[account] == possibleParent;
    }
    
    /**
     * @notice Get account liquidity - VULNERABLE TO DONATION ATTACKS
     */
    function getAccountLiquidity(address account) public view returns (uint256 collateralValue, uint256 liabilityValue) {
        // VULNERABILITY: Directly uses token balances without protection against donations
        collateralValue = collateralToken.balanceOf(account);
        liabilityValue = debtToken.balanceOf(account);
    }
    
    /**
     * @notice Compute discount booster
     */
    function computeDiscountBooster(address liquidator, uint256 liabilityValue) internal view returns (uint256) {
        // Simplified implementation - in real Euler this would be based on average liquidity
        // For testing, we'll return a fixed booster
        return 1e18; // 1.0x booster
    }
    
    /**
     * @notice Transfer debt between accounts
     */
    function transferBorrow(address from, address to, uint256 amount) internal {
        require(accountDebt[from] >= amount, "Insufficient debt");
        
        accountDebt[from] -= amount;
        accountDebt[to] += amount;
        
        // Transfer actual debt tokens
        debtToken.transferFrom(from, to, amount);
    }
    
    /**
     * @notice Increase debt for an account
     */
    function increaseBorrow(address account, uint256 amount) internal {
        accountDebt[account] += amount;
        
        // Mint new debt tokens - THIS IS THE VULNERABILITY
        debtToken.mint(account, amount);
    }
    
    /**
     * @notice Increase protocol reserves
     */
    function increaseReserves(uint256 amount) internal {
        // This would update reserve accounting
        // For simplicity, we'll just track the increase
        // In the real exploit, this causes accounting imbalances
    }
    
    /**
     * @notice Deposit collateral for an account
     */
    function depositCollateral(address account, uint256 amount) external {
        collateralToken.transferFrom(msg.sender, address(this), amount);
        accountCollateral[account] += amount;
    }
    
    /**
     * @notice Create debt for an account (for testing)
     */
    function createDebt(address account, uint256 amount) external {
        accountDebt[account] += amount;
        debtToken.mint(account, amount);
    }
    
    /**
     * @notice Set sub-account relationship (for testing)
     */
    function setSubAccount(address child, address parent) external {
        isSubAccount[child] = true;
        subAccountParent[child] = parent;
    }
    
    /**
     * @notice Get account information
     */
    function getAccountInfo(address account) external view returns (
        uint256 collateral,
        uint256 debt,
        uint256 healthScore,
        bool liquidatable
    ) {
        collateral = accountCollateral[account];
        debt = accountDebt[account];
        
        if (debt == 0) {
            healthScore = type(uint256).max;
            liquidatable = false;
        } else {
            healthScore = (collateral * 1e18) / debt;
            liquidatable = healthScore < 1e18;
        }
    }
}