RL-based Braking System=> new dynamics (PRA gave failure) (Trained for 3000 iteration)(New dynamics, old reward policy)
======================================
This has uqique drift between learned policy. It reflects , that AVF based adversary works. In this case policy shift abruptly from very bad policy to very good policy. Then also AVF will have positive result. 

Steps for finding adversary : 
1. PR Adversary (Priority replay Adversary Finder) 
2. Vanilla MC Search(Random Adversary search) 
3. AVF based adversary(AVF based adversary)  

> This experiment shows: 
  -> PR adversary is first step to go for finding adversary and can find faults. 
  -> Vanilla MC is dumbest idea to find adversary. 
  -> AVF  based search is fastest and better way to find adversary. 
 

Assumption made by AVF => Agents fails in similar manner as earlier agents failed. 
