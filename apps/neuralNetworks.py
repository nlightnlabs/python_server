import pandas as pd
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix


def neuralNetwork(data):
    df = pd.DataFrame(data)

    # Split the data into training and testing sets
    X = df[['Feature1', 'Feature2']]
    y = df['Target']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Initialize the Neural Network model
    model = Sequential([
        Dense(units=64, activation='relu', input_shape=(2,)),  # Input layer with 2 features
        Dense(units=32, activation='relu'),  # Hidden layer with 32 neurons
        Dense(units=1, activation='sigmoid')  # Output layer with 1 neuron for binary classification
    ])

    # Compile the model
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

    # Fit the model to the training data
    model.fit(X_train, y_train, epochs=50, verbose=0)  # You can adjust the number of epochs

    # Make predictions on the test data
    y_pred_proba = model.predict(X_test)
    y_pred = (y_pred_proba > 0.5).astype(int)  # Convert probabilities to binary predictions

    # Evaluate the model
    accuracy = accuracy_score(y_test, y_pred)
    classification_rep = classification_report(y_test, y_pred, output_dict=True)
    conf_matrix = confusion_matrix(y_test, y_pred)

    # Break down the classification report into key-value pair objects with descriptions
    precision_0 = classification_rep['0']
    recall_0 = classification_rep['1']
    f1_score_0 = classification_rep['1']
    support_0 = classification_rep['1']

    precision_1 = classification_rep['1']
    recall_1 = classification_rep['1']
    f1_score_1 = classification_rep['1']
    support_1 = classification_rep['1']

    classification_rep_breakdown = {
        'Class 0': {
            'Precision': {'Value': precision_0, 'Description': 'Precision measures the proportion of true positive predictions among all positive predictions.'},
            'Recall': {'Value': recall_0, 'Description': 'Recall measures the proportion of true positive predictions among all actual positive instances.'},
            'F1-Score': {'Value': f1_score_0, 'Description': 'F1-score is the harmonic mean of precision and recall, providing a balanced measure.'},
            'Support': {'Value': support_0, 'Description': 'Support is the number of actual occurrences of the class in the test set.'}
        },
        'Class 1': {
            'Precision': {'Value': precision_1, 'Description': 'Precision measures the proportion of true positive predictions among all positive predictions.'},
            'Recall': {'Value': recall_1, 'Description': 'Recall measures the proportion of true positive predictions among all actual positive instances.'},
            'F1-Score': {'Value': f1_score_1, 'Description': 'F1-score is the harmonic mean of precision and recall, providing a balanced measure.'},
            'Support': {'Value': support_1, 'Description': 'Support is the number of actual occurrences of the class in the test set.'}
        }
    }

    # Create an object with output parameters and descriptions
    output_object = {
        'Accuracy': {
            'Value': accuracy,
            'Description': 'Accuracy is the ratio of correctly predicted observations to the total observations.'
        },
        'Classification Report': {
            'Value': classification_rep_breakdown,
            'Description': 'Detailed breakdown of precision, recall, F1-score, and support for each class.'
        },
        'Confusion Matrix': {
            'Value': conf_matrix,
            'Description': 'Confusion matrix shows the count of true positive, true negative, false positive, and false negative predictions.'
        }
    }

    # Display the output object
    print(output_object)

    return output_object

# Sample data
data = {'Feature1': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        'Feature2': [5, 4, 3, 2, 1, 5, 4, 3, 2, 1],
        'Target': [0, 0, 0, 0, 0, 1, 1, 1, 1, 1]}


neuralNetwork(data)