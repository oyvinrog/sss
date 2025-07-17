## 3 of 5 locking scheme for Bitcoin

Split your private key into 5 separate keyphrases using Shamir secret sharing (SSS). Any 3 keys will unlock the treasure.

<img src="explanation.png" width="400" height="400">

Use `bip39split` to split your Bitcoin private key into SSS shares

Use `bip39combine` to combine back again

Use `generate_testphrase` if you want to generate a Bitcoin test seedphrase. This is useful if you want to verify that this utility works. 

Example usage: 

```bash

 ./bip39split "prison supreme survey fetch drift wood book rose abstract input hammer this engage oil surprise behind poverty breeze profit ice regret whip monster hurt" KEYS

```
If you want to reconstruct the original key, use 3 keys chosen from file 'KEYS'. The following command should regenerate the exact key above:

```bash
./bip39combine KEYS
```

## TODO

- Make the scripts work for Windows:

    - Rewrite code to use Python completely

- Make UI version