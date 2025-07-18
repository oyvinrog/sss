#!/usr/bin/env python3

from shamir_mnemonic import generate_mnemonics
from mnemonic import Mnemonic
from bip39_utils import expand_bip39_words
import sys


def split_bip39_to_shares(seed_phrase, output_file=None):
    """
    Split a BIP39 seed phrase into Shamir secret shares.
    Automatically expands 4-character word prefixes to full words.
    
    Args:
        seed_phrase (str): The 24-word BIP39 seed phrase (can be abbreviated)
        output_file (str, optional): File to write shares to
    
    Returns:
        list: List of Shamir secret shares
    """
    # First, expand any abbreviated words
    expanded_phrase = expand_bip39_words(seed_phrase)
    print(f"📝 Expanded phrase: {expanded_phrase}")
    print()
    
    mnemo = Mnemonic("english")
    
    try:
        secret = mnemo.to_entropy(expanded_phrase)
    except Exception as e:
        raise ValueError(f"Invalid BIP39 seed phrase: {e}")
    
    # Display the original seed's hexadecimal representation
    hex_entropy = secret.hex()
    print(f"🔑 Original Seed Hex: {hex_entropy}")
    print(f"📏 Entropy Length: {len(secret)} bytes ({len(secret) * 8} bits)")
    print()
    
    # Generate 5 shares with threshold of 3 (3 of 5 scheme)
    shares = generate_mnemonics(group_threshold=1, groups=[(3, 5)], master_secret=secret)
    
    share_strings = []
    for i, share in enumerate(shares[0], 1):
        share_string = "".join(share)
        share_strings.append(share_string)
        print(f"Share {i}: {share_string}")
    
    if output_file:
        with open(output_file, "w") as fw:
            for share_string in share_strings:
                fw.write(share_string + "\n")
        print(f"✅ Shares written to {output_file}")
    
    return share_strings


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 split.py \"<24-word-seed-phrase>\" [output-file]")
        print("Note: Words can be abbreviated to their first 4 characters")
        print("Example: python3 split.py \"aban abou abse acci...\" shares.txt")
        sys.exit(1)
    
    seed_phrase = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    try:
        split_bip39_to_shares(seed_phrase, output_file)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 