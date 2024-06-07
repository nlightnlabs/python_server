import pandas as pd
from sklearn.cluster import KMeans

def kMeans(data):
    df = pd.DataFrame(data)

    # Initialize the K-means clustering algorithm
    kmeans = KMeans(n_clusters=2, random_state=0)  # You can adjust the number of clusters (n_clusters)

    # Fit the model to the data and predict cluster labels
    df['Cluster'] = kmeans.fit_predict(df[['Feature1', 'Feature2']])

    # Get cluster centers
    cluster_centers = kmeans.cluster_centers_

    # Calculate inertia (within-cluster sum of squares)
    inertia = kmeans.inertia_

    # Create an object with clustering results and descriptions
    output_object = {
        'Cluster Labels': {
            'Value': df['Cluster'].tolist(),
            'Description': 'Cluster labels assigned to each data point.'
        },
        'Cluster Centers': {
            'Value': cluster_centers.tolist(),
            'Description': 'Coordinates of cluster centers in feature space.'
        },
        'Inertia': {
            'Value': inertia,
            'Description': 'Sum of squared distances of samples to their closest cluster center.'
        }
    }

    # Display the output object
    print(output_object)

# Sample data
data = {'Feature1': [1, 2, 3, 10, 11, 12],
        'Feature2': [5, 6, 7, 15, 16, 17]}

kMeans(data)