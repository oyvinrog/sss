## 3 of 5 locking scheme for Bitcoin

Split your private key into 5 separate keyphrases using Shamir secret sharing (SSS). Any 3 keys will unlock the treasure.

<img src="explanation.png" width="400" height="400">

Use `split.py` to split your Bitcoin private key into SSS shares

Use `combine.py` to combine back again

Use `generate_testphrase` if you want to generate a Bitcoin test seedphrase. This is useful if you want to verify that this utility works.

## Installation

1. Create a virtual environment (recommended):
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Splitting a BIP39 seed phrase

```bash
python3 split.py "prison supreme survey fetch drift wood book rose abstract input hammer this engage oil surprise behind poverty breeze profit ice regret whip monster hurt" shares.txt
```

This creates 5 shares in the file `shares.txt`. Any 3 of these shares can recover the original seed phrase.

### Combining shares back to original

If you want to reconstruct the original key, use **exactly 3 shares** from the file. You can manually select any 3 shares:

```bash
# Create a file with any 3 shares (for example, first 3 shares)
head -n 3 shares.txt > selected_shares.txt
python3 combine.py selected_shares.txt
```

**Note**: The combine script requires exactly 3 shares. If you pass a file with more than 3 shares, it will fail. This is by design for security and clarity.

Alternative: You can manually copy any 3 shares into a new file and combine those.

### Testing and Verification

Run comprehensive tests to verify the system works correctly:

```bash
# Quick test with 2 random phrases
./run_verification_tests 2

# Or run directly with Python
python3 test_bip39_verification.py 5
```

The test suite will:
- Generate random BIP39 phrases
- Split them into 5 shares  
- Verify any 3 random shares can recover the original
- Test all possible 3-share combinations
- Ensure fewer than 3 shares cannot recover the phrase

## Files

- `split.py` - Split BIP39 phrase into Shamir shares
- `combine.py` - Combine Shamir shares back to BIP39 phrase  
- `test_bip39_verification.py` - Comprehensive test suite
- `run_verification_tests` - Convenient test runner
- `generate_testphrase` - Generate random test BIP39 phrases
- `requirements.txt` - Python dependencies

## Security Notes

- This implements a 3-of-5 threshold scheme
- Any 3 shares can recover the original seed phrase
- 2 or fewer shares provide no information about the original
- Store shares in separate, secure locations
- Test the recovery process before relying on it