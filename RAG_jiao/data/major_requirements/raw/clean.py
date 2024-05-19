if __name__ == "__main__":
    import os 
    import pandas as pd
    for f in os.listdir():
        print(f)
        if (f.endswith('_cleaned.csv')):
            os.remove(f)

        tmp = pd.read_excel('./' + f)

        #tmp2 = tmp.dropna(how="all", axis=0).dropna(how="all", axis=1)
        
        #tmp2.to_csv(f.split('.')[0] + "_cleaned.csv")


