# Ruflo Anvil Verification System

Enhanced multi-agent vulnerability discovery system that requires mandatory Anvil simulation verification before reporting any vulnerabilities.

## Core Principle
**No vulnerability is reported until it is verified to work via Anvil simulation.**

## Agent Workflow

### 1. Code Analysis Agent
- Analyzes Solidity contracts for potential vulnerabilities
- Identifies suspicious patterns, missing modifiers, reentrancy risks
- Ranks vulnerabilities by severity and exploitability

### 2. Exploit Development Agent  
- Takes potential vulnerabilities from Code Analysis Agent
- Writes complete exploit contracts in Solidity
- Develops proof-of-concept attacks with proper gas optimization

### 3. Anvil Verification Agent
- Sets up Anvil test environment
- Deploys vulnerable contracts and exploit contracts
- Executes the exploits and captures results
- **CRITICAL**: Only passes verified exploits to reporting

### 4. Security Report Agent
- Generates professional vulnerability reports
- Only processes vulnerabilities that passed Anvil verification
- Includes verified exploit code and execution results
- Creates technical documentation with professional styling

## Verification Requirements

Each vulnerability must:
1. ✅ Be exploitable in Anvil simulation
2. ✅ Show measurable impact (funds drained, state corrupted, etc.)
3. ✅ Include working proof-of-concept code
4. ✅ Demonstrate reproducible results

## Directory Structure

```
ruflo-anvil-verification/
├── agents/
│   ├── code-analyzer.md
│   ├── exploit-developer.md
│   ├── anvil-verifier.md
│   └── report-generator.md
├── templates/
│   ├── vulnerability-test.sol
│   └── report-template.html
└── verification-pipeline/
    ├── run-analysis.sh
    └── verify-exploits.sh
```

## Usage

```bash
# Run complete vulnerability analysis with verification
./verification-pipeline/run-analysis.sh <contract-file>

# This will:
# 1. Analyze the contract for vulnerabilities
# 2. Write exploit contracts
# 3. Verify exploits in Anvil
# 4. Generate reports only for verified vulnerabilities
```

## Success Criteria

A vulnerability analysis is successful when:
- All reported vulnerabilities have working exploits
- Anvil verification logs show actual exploitation
- No false positives are reported
- Professional technical documentation is generated