import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix



def supportVectorMachines(data):
        df = pd.DataFrame(data)

        # Split the data into training and testing sets
        X = df[['Feature1', 'Feature2']]
        y = df['Target']
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # Initialize the SVM classifier
        svm_classifier = SVC(kernel='linear')  # You can change the kernel type (linear, rbf, poly, etc.)

        # Fit the model to the training data
        svm_classifier.fit(X_train, y_train)

        # Make predictions on the test data
        y_pred = svm_classifier.predict(X_test)

        # Evaluate the model
        accuracy = accuracy_score(y_test, y_pred)
        classification_rep = classification_report(y_test, y_pred)
        conf_matrix = confusion_matrix(y_test, y_pred)

        result = {
                "accuracy":accuracy,
                "classification_report":classification_rep,
                "confusion_matrix":conf_matrix
        }

        print(result)

        return result

# Sample data
data = {'Feature1': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        'Feature2': [5, 4, 3, 2, 1, 5, 4, 3, 2, 1],
        'Target': [0, 0, 0, 0, 0, 1, 1, 1, 1, 1]}

supportVectorMachines(data)