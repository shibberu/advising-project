'''
This code does some simple processing and renames the files in ./processed and put them in a sub-directory. 
This code should be called before calling build_chunk
'''
if __name__ == "__main__":
    import os 
    import pandas as pd
    p = './processed/'
    for f in os.listdir(p):
        f_path = p + f
        # if (f.endswith('_cleaned.csv')):

        #     os.remove(f)
        if (not f.endswith('cleaned.csv')):
            continue
        tmp2 = pd.read_csv(f_path, low_memory=False)
        major_name = tmp2.columns[2].replace(' ', "_")
        tmp2 = tmp2.iloc[:, 1:]
        for i in range(0, tmp2.shape[0]):
            for j in range(0, tmp2.shape[1]):
                print(tmp2.iloc[i, j])
        #print(f, tmp2.columns[2])
        #tmp2 = tmp.dropna(how="all", axis=0).dropna(how="all", axis=1)
        if ('secondmajor' in f.lower()):
            #tmp2.to_csv("./processed/4/" + major_name + "_second_major.csv")
            pass
        else:
            #tmp2.to_csv("./processed/4/" + major_name + ".csv")
            pass

