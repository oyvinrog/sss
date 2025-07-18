#!/usr/bin/env python3

from mnemonic import Mnemonic
import shamir_mnemonic


def expand_bip39_words(abbreviated_phrase):
    """
    Expand 4-character BIP39 word prefixes to full words.
    
    Args:
        abbreviated_phrase (str): Space-separated string of 4-character word prefixes
    
    Returns:
        str: Full BIP39 seed phrase with complete words
    """
    mnemo = Mnemonic("english")
    word_list = mnemo.wordlist
    
    # Create mapping from 4-character prefix to full word
    prefix_to_word = {}
    for word in word_list:
        prefix = word[:4]
        prefix_to_word[prefix] = word
    
    words = abbreviated_phrase.strip().split()
    expanded_words = []
    
    for word in words:
        # If word is already full length or longer than 4 chars, keep as is
        if len(word) > 4:
            expanded_words.append(word)
        # If exactly 4 chars or less, try to expand
        else:
            prefix = word[:4].lower()  # Ensure lowercase for matching
            if prefix in prefix_to_word:
                expanded_words.append(prefix_to_word[prefix])
                print(f"🔤 Expanded '{word}' → '{prefix_to_word[prefix]}'")
            else:
                # If not found in prefixes, maybe it's already a full word
                if word.lower() in word_list:
                    expanded_words.append(word.lower())
                else:
                    raise ValueError(f"'{word}' is not a valid BIP39 word prefix or full word")
    
    expanded_phrase = " ".join(expanded_words)
    return expanded_phrase


def expand_share_words_if_needed(share_phrase):
    """
    Smart expansion for Shamir shares. Only expands words that are not 
    already in the Shamir wordlist but can be expanded from prefixes.
    
    Args:
        share_phrase (str): Space-separated Shamir share phrase
    
    Returns:
        str: Share phrase with abbreviated words expanded if needed
    """
    # Get both wordlists
    shamir_wordlist = shamir_mnemonic.wordlist.WORDLIST
    shamir_wordlist_set = set(shamir_wordlist)
    mnemo = Mnemonic("english")
    bip39_wordlist = mnemo.wordlist
    
    # Create mapping from 4-character prefix to full BIP39 word
    bip39_prefix_to_word = {}
    for word in bip39_wordlist:
        prefix = word[:4]
        bip39_prefix_to_word[prefix] = word
    
    words = share_phrase.strip().split()
    processed_words = []
    
    for word in words:
        word_lower = word.lower()
        
        # If word is already in Shamir wordlist, keep it as-is
        if word_lower in shamir_wordlist_set:
            processed_words.append(word_lower)
        # If word is not in Shamir wordlist, try to expand it
        elif len(word) <= 4:
            prefix = word_lower[:len(word)]  # Use actual word length as prefix
            
            # First try: find Shamir words that start with this prefix
            shamir_matches = [w for w in shamir_wordlist if w.startswith(prefix)]
            
            if len(shamir_matches) == 1:
                # Exactly one Shamir word match - expand to it
                expanded_word = shamir_matches[0]
                processed_words.append(expanded_word)
                print(f"🔤 Expanded '{word}' → '{expanded_word}' (Shamir)")
            elif len(shamir_matches) == 0:
                # No Shamir matches, try BIP39 expansion
                if len(word) == 4 and prefix in bip39_prefix_to_word:
                    expanded_word = bip39_prefix_to_word[prefix]
                    # Check if the expanded BIP39 word is in Shamir wordlist
                    if expanded_word in shamir_wordlist_set:
                        processed_words.append(expanded_word)
                        print(f"🔤 Expanded '{word}' → '{expanded_word}' (BIP39→Shamir)")
                    else:
                        # Expanded word not in Shamir wordlist, keep original
                        processed_words.append(word_lower)
                else:
                    # Can't expand, keep original
                    processed_words.append(word_lower)
            else:
                # Multiple Shamir matches - ambiguous, keep original
                processed_words.append(word_lower)
        else:
            # Word is longer than 4 chars but not in Shamir wordlist, keep as-is
            processed_words.append(word_lower)
    
    return " ".join(processed_words) 