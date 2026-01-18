# Team NeoQuant - Submission Package

## Files for Unstop Submission

### 1. Team_NeoQuant_Strategy.py
Main Python strategy file - takes CSV input and outputs all metrics

### 2. Python Project.pdf  
Research report explaining methodology

### 3. requirements.txt
Dependencies

### 4. Dataset Files (for testing, not for submission)
- DAT_MT_XAUUSD_M1_2024.csv
- DAT_MT_XAGUSD_M1_2024.csv

---

## Create Submission ZIP

```bash
cd "/Users/kartikchoudhary/Desktop/Team NeoQuant"
zip Team_NeoQuant.zip Team_NeoQuant_Strategy.py "Python Project.pdf" requirements.txt
```

Then upload `Team_NeoQuant.zip` to Unstop!

---

## Test Before Submitting

```bash
python Team_NeoQuant_Strategy.py --xau_csv DAT_MT_XAUUSD_M1_2024.csv --xag_csv DAT_MT_XAGUSD_M1_2024.csv
```
