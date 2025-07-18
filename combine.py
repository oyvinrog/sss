#!/usr/bin/env python3

from shamir_mnemonic import combine_mnemonics
from mnemonic import Mnemonic
import sys


def combine_shares_to_bip39(shares_file=None, shares_list=None):
    """
    Combine Shamir secret shares back into a BIP39 seed phrase.
    
    Args:
        shares_file (str, optional): File containing shares (one per line)
        shares_list (list, optional): List of share strings
    
    Returns:
        str: The recovered BIP39 seed phrase
    """
    if shares_file:
        try:
            print(f"Reading {shares_file}")
            with open(shares_file, 'r') as f:
                lines = f.readlines()
            shares = [line.strip() for line in lines if line.strip()]
        except Exception as e:
            raise IOError(f"Error reading file: {e}")
    elif shares_list:
        shares = [share.strip() for share in shares_list if share.strip()]
    else:
        raise ValueError("Either shares_file or shares_list must be provided")
    
    if len(shares) < 3:
        raise ValueError("At least 3 shares are required.")
    
    try:
        secret = combine_mnemonics(shares)
        
        # Display the recovered seed's hexadecimal representation
        hex_entropy = secret.hex()
        print(f"🔑 Recovered Seed Hex: {hex_entropy}")
        print(f"📏 Entropy Length: {len(secret)} bytes ({len(secret) * 8} bits)")
        print()
        
        mnemo = Mnemonic("english")
        phrase = mnemo.to_mnemonic(secret)
        return phrase
    except Exception as e:
        raise ValueError(f"Failed to recover: {e}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 combine.py <file-with-3-or-more-shares>")
        sys.exit(1)
    
    shares_file = sys.argv[1]
    
    try:
        phrase = combine_shares_to_bip39(shares_file=shares_file)
        print("✅ Recovered BIP39 Phrase:\n")
        print(phrase)
    except Exception as e:
        print(f"❌ {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 