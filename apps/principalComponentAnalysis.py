import pandas as pd
from sklearn.decomposition import PCA

def principalComponentAnalysis(data):

    df = pd.DataFrame(data)

    # Initialize PCA with desired number of components
    pca = PCA(n_components=2)  # You can adjust the number of components (n_components)

    # Fit PCA to the data and transform it
    pca_result = pca.fit_transform(df)

    # Get explained variance ratio
    explained_variance_ratio = pca.explained_variance_ratio_

    # Create an object with PCA results and descriptions
    output_object = {
        'PCA Components': {
            'Value': pca_result.tolist(),
            'Description': 'Transformed data with reduced dimensions using PCA.'
        },
        'Explained Variance Ratio': {
            'Value': explained_variance_ratio.tolist(),
            'Description': 'Percentage of variance explained by each principal component.'
        }
    }

    # Display the output object
    print(output_object)

    return(output_object)

# Sample data
data = {'Feature1': [1, 2, 3, 4, 5],
        'Feature2': [5, 4, 3, 2, 1],
        'Feature3': [10, 9, 8, 7, 6]}

principalComponentAnalysis(data)
