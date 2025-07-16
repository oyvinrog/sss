## 3 of 5 unlocking scheme for Bitcoin


<img src="explanation.png" width="400" height="400">

Use `bip39split` to split your Bitcoin private key into SSS shares

Use `bip39combine` to combine back again

Use `generate_testphrase` if you want to generate a Bitcoin test seedphrase

Example usage: 

```bash

 ./bip39split "prison supreme survey fetch drift wood book rose abstract input hammer this engage oil surprise behind poverty breeze profit ice regret whip monster hurt" KEYS

```
If you want to reconstruct the original key, use 3 keys chosen from file 'KEYS'. The following command should regenerate the exact key above:

```bash
./bip39combine KEYS
```