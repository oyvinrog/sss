#!/usr/bin/env python3

import random
import itertools
import sys
from shamir_mnemonic import generate_mnemonics
from mnemonic import Mnemonic
from combine import combine_shares_to_bip39


def split_bip39_to_shares_quiet(seed_phrase):
    """Split a BIP39 seed phrase into Shamir secret shares (quiet version for testing)"""
    mnemo = Mnemonic("english")
    
    try:
        secret = mnemo.to_entropy(seed_phrase)
    except Exception as e:
        raise ValueError(f"Invalid BIP39 seed phrase: {e}")
    
    # Generate 5 shares with threshold of 3 (3 of 5 scheme)
    shares = generate_mnemonics(group_threshold=1, groups=[(3, 5)], master_secret=secret)
    
    share_strings = []
    for i, share in enumerate(shares[0], 1):
        share_string = "".join(share)
        share_strings.append(share_string)
    
    return share_strings


class BIP39TestVerification:
    def __init__(self):
        self.mnemo = Mnemonic("english")
        self.passed_tests = 0
        self.failed_tests = 0
        self.test_results = []

    def generate_test_phrase(self, strength=256):
        """Generate a random BIP39 test phrase"""
        return self.mnemo.generate(strength=strength)

    def log_test(self, test_name, success, details=""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if details:
            print(f"    {details}")
        
        self.test_results.append({
            'name': test_name,
            'success': success,
            'details': details
        })
        
        if success:
            self.passed_tests += 1
        else:
            self.failed_tests += 1

    def test_basic_split_and_combine(self, test_phrase):
        """Test basic splitting and combining functionality"""
        try:
            # Split the phrase (using quiet version)
            shares = split_bip39_to_shares_quiet(test_phrase)
            
            # Verify we get 5 shares
            if len(shares) != 5:
                self.log_test("Basic Split", False, f"Expected 5 shares, got {len(shares)}")
                return False
            
            # Combine first 3 shares (threshold requirement)
            recovered_phrase = combine_shares_to_bip39(shares_list=shares[:3])
            
            # Verify recovery matches original
            if recovered_phrase == test_phrase:
                self.log_test("Basic Split & Combine", True, "First 3 shares successfully recovered original phrase")
                return True
            else:
                self.log_test("Basic Split & Combine", False, "Recovered phrase doesn't match original")
                return False
                
        except Exception as e:
            self.log_test("Basic Split & Combine", False, f"Exception: {e}")
            return False

    def test_three_random_shares(self, test_phrase, num_iterations=10):
        """Test combining with 3 random shares multiple times"""
        try:
            shares = split_bip39_to_shares_quiet(test_phrase)
            successful_combinations = 0
            
            for i in range(num_iterations):
                # Randomly select 3 shares from the 5
                random_shares = random.sample(shares, 3)
                
                try:
                    recovered_phrase = combine_shares_to_bip39(shares_list=random_shares)
                    
                    if recovered_phrase == test_phrase:
                        successful_combinations += 1
                    else:
                        self.log_test(f"Random 3 Shares (iteration {i+1})", False, 
                                    "Recovered phrase doesn't match original")
                        return False
                        
                except Exception as e:
                    self.log_test(f"Random 3 Shares (iteration {i+1})", False, f"Exception: {e}")
                    return False
            
            self.log_test("Random 3 Shares Test", True, 
                         f"All {num_iterations} random combinations successful")
            return True
            
        except Exception as e:
            self.log_test("Random 3 Shares Test", False, f"Exception: {e}")
            return False

    def test_all_possible_combinations(self, test_phrase):
        """Test all possible 3-share combinations from 5 shares"""
        try:
            shares = split_bip39_to_shares_quiet(test_phrase)
            
            # Generate all possible combinations of 3 shares from 5
            all_combinations = list(itertools.combinations(shares, 3))
            successful_combinations = 0
            
            print(f"    Testing all {len(all_combinations)} possible 3-share combinations...")
            
            for i, combination in enumerate(all_combinations):
                try:
                    recovered_phrase = combine_shares_to_bip39(shares_list=list(combination))
                    
                    if recovered_phrase == test_phrase:
                        successful_combinations += 1
                    else:
                        self.log_test("All 3-Share Combinations", False, 
                                    f"Combination {i+1} failed: recovered phrase doesn't match")
                        return False
                        
                except Exception as e:
                    self.log_test("All 3-Share Combinations", False, 
                                f"Combination {i+1} failed with exception: {e}")
                    return False
            
            self.log_test("All 3-Share Combinations", True, 
                         f"All {len(all_combinations)} combinations successful")
            return True
            
        except Exception as e:
            self.log_test("All 3-Share Combinations", False, f"Exception: {e}")
            return False

    def test_insufficient_shares(self, test_phrase):
        """Test that 2 shares or fewer cannot recover the phrase"""
        try:
            shares = split_bip39_to_shares_quiet(test_phrase)
            
            # Test with 1 share
            try:
                recovered = combine_shares_to_bip39(shares_list=shares[:1])
                self.log_test("Insufficient Shares (1 share)", False, 
                            "Should have failed but didn't")
                return False
            except:
                pass  # Expected to fail
            
            # Test with 2 shares
            try:
                recovered = combine_shares_to_bip39(shares_list=shares[:2])
                self.log_test("Insufficient Shares (2 shares)", False, 
                            "Should have failed but didn't")
                return False
            except:
                pass  # Expected to fail
            
            self.log_test("Insufficient Shares Test", True, 
                         "Correctly failed with 1 and 2 shares")
            return True
            
        except Exception as e:
            self.log_test("Insufficient Shares Test", False, f"Unexpected exception: {e}")
            return False

    def test_invalid_phrase(self):
        """Test behavior with invalid BIP39 phrases"""
        invalid_phrases = [
            "invalid word word word word word word word word word word word word word word word word word word word word word word word word",
            "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon",
            "word1 word2 word3 word4 word5 word6 word7 word8 word9 word10 word11 word12 word13 word14 word15 word16 word17 word18 word19 word20 word21 word22 word23 word24"
        ]
        
        for i, invalid_phrase in enumerate(invalid_phrases):
            try:
                shares = split_bip39_to_shares_quiet(invalid_phrase)
                self.log_test(f"Invalid Phrase Test {i+1}", False, 
                            "Should have failed with invalid phrase but didn't")
                return False
            except:
                pass  # Expected to fail
        
        self.log_test("Invalid Phrase Test", True, 
                     "Correctly rejected invalid BIP39 phrases")
        return True

    def run_comprehensive_test(self, num_test_phrases=5):
        """Run comprehensive verification tests"""
        print("🔬 Starting BIP39 Shamir Secret Sharing Verification Tests")
        print("=" * 60)
        
        # Test invalid phrases first
        self.test_invalid_phrase()
        print()
        
        # Test with multiple generated phrases
        for i in range(num_test_phrases):
            print(f"📝 Test Phrase {i+1}/{num_test_phrases}")
            print("-" * 40)
            
            # Generate test phrase
            test_phrase = self.generate_test_phrase()
            print(f"Generated phrase: {test_phrase[:50]}...")
            
            # Run all tests on this phrase
            self.test_basic_split_and_combine(test_phrase)
            self.test_three_random_shares(test_phrase)
            self.test_all_possible_combinations(test_phrase)
            self.test_insufficient_shares(test_phrase)
            
            print()
        
        # Print summary
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"✅ Passed: {self.passed_tests}")
        print(f"❌ Failed: {self.failed_tests}")
        print(f"📈 Success Rate: {self.passed_tests/(self.passed_tests + self.failed_tests)*100:.1f}%")
        
        if self.failed_tests == 0:
            print("\n🎉 ALL TESTS PASSED! Your BIP39 Shamir Secret Sharing implementation is working correctly.")
        else:
            print(f"\n⚠️  {self.failed_tests} test(s) failed. Check the implementation.")
        
        return self.failed_tests == 0


def main():
    """Main function to run verification tests"""
    if len(sys.argv) > 1:
        try:
            num_tests = int(sys.argv[1])
        except ValueError:
            print("Usage: python3 test_bip39_verification.py [number_of_test_phrases]")
            sys.exit(1)
    else:
        num_tests = 5
    
    verifier = BIP39TestVerification()
    success = verifier.run_comprehensive_test(num_tests)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main() 