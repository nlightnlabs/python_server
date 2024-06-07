import pandas as pd
import numpy as np
import statsmodels.api as sm

def linearRegression(data):
 
    df = pd.DataFrame(data)

    # Add constant term for intercept
    df['const'] = 1

    # Define independent variables (X) and dependent variable (Y)
    X = df[['const', 'X1', 'X2']]
    Y = df['Y']

    # Fit the model
    model = sm.OLS(Y, X).fit()

    # Print the model summary
    print(model.summary())

    return(model.summary)


 # Sample data
data = {'X1': [1, 2, 3, 4, 5],
        'X2': [5, 4, 3, 2, 1],
        'Y': [10, 20, 30, 40, 50]}
    
linearRegression(data)
