# Analysis of Adversary Capabilities

This project performs automated analysis of adversary capabilities across multiple security protocols. By extending the **Tamarin Prover** with an additional decision rule, we leverage the accessibility of protocol primitives to automatically determine whether a given protocol enables any special adversarial capabilities.

The repository includes protocol specifications, corresponding analysis results, and generated visualization figures for further inspection and verification.

---

## Repository Structure

.  
├── protocol/ # Protocols analyzed in this project (.spthy files)  
├── proof/ # Analysis results for each protocol, verifiable with Tamarin   
└── fig/ # Generated visualization maps (.png files)  

---

## How to Reproduce the Results

This analysis is based on **Tamarin Prover version 1.6.0**.

For installation and environment setup, please refer to Chapter 2 of the official manual:  
https://tamarin-prover.github.io/manual/book/002_installation.html

After installing Tamarin, you can reproduce all analysis results using the following commands.

### Automatically Prove All Protocols
```bash
tamarin-prover --prove *.spthy
```

Due to the complexity of the protocol modeling in this project, it is not recommended to use automated proofs. It is suggested to enter the graphical interface to prove each theorem one by one. The command to enter the graphical interface is as follows

### Enter the graphic page to prove
```bash
tamarin-prover interactive *.spthy
```
