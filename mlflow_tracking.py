

from sklearn.metrics import f1_score
from sklearn.metrics import roc_auc_score
from sklearn.metrics import confusion_matrix
import pandas as pd
from sklearn.feature_selection import chi2
from sklearn import preprocessing
from sklearn.model_selection import train_test_split
import mlflow
from sklearn.linear_model import LogisticRegression
import mlflow.sklearn
from mlflow.tracking import MlflowClient
import io
from google.colab import files

pip install mlflow

def data_upload():
  uploaded = files.upload()
  data = pd.read_csv(io.BytesIO(uploaded['heart.csv']))
  return data
def preprocess(data):
    

    # label_encoding target column
    label_encoder = preprocessing.LabelEncoder()

    data['HeartDisease'] = label_encoder.fit_transform(data['HeartDisease'])
    y = data['HeartDisease']
    data.pop('HeartDisease')

    # One-hot encoding
    encoded_data = pd.get_dummies(data)

    return encoded_data, y

def traintestsplit(encoded_data,y):
    X= encoded_data

    

    # split into train test sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.33)
    return X_train, X_test, y_train, y_test

def eval_metrics(actual, pred):

    f1 = f1_score(actual, pred, average='micro')
    roc = roc_auc_score(actual, pred)
    cm = confusion_matrix(actual, pred)
    return f1, roc, cm
def parameter():
    c = input('''Enter regularization parameter"
              Hint: try lower values like 1,2,3 for better results''')
    if (c=='' or c!=int):
        c=1.0

    p = input('''Enter penalty parameter
    Hint: l1, l2, elasticnet, none''')
    if p =='':
        p='l2'

    s = input('''Enter solver
    Hint: newton-cg, lbfgs, liblinear, sag, saga''')
    if s=='':
        s='lbfgs'
    return c, p, s

if __name__ == "__main__":

    data = data_upload()
    encoded_data, y = preprocess(data)
    X_train, X_test, y_train, y_test = traintestsplit(encoded_data, y)

    #model training using MLflow
    c, penalty, solver =parameter()
    

    
    arti_repo = "./mlflow-run"
    experiment_name = 'End-to-End-implementation'
    client = MlflowClient()

    try:
        # Create experiment
        experiment_id = client.create_experiment(experiment_name, artifact_location=arti_repo)
    except:
        # Get the experiment id if it already exists
        experiment_id = client.get_experiment_by_name(experiment_name).experiment_id

    with mlflow.start_run(run_name='LR2', experiment_id=experiment_id) as run:
        run_id = run.info.run_uuid
        MlflowClient().set_tag(run_id,
                               "mlflow.note.content",
                               "An end-to-end implementation of ML model using synthea-allergies data")

        # Define customer tag
        tags = {"Application": "ML flow implementation",
                "release.version": "2.2.0"}

        # Set Tag
        mlflow.set_tags(tags)
        mlflow.sklearn.autolog()
        #train model

        log_reg = LogisticRegression(penalty=penalty, solver=solver, C=c)
        log_reg.fit(X_train, y_train)

        #perform prediction on test data
        y_pred = log_reg.predict(X_test)
        (f1, roc, cm) = eval_metrics(y_test, y_pred)
        t_p, t_n, f_p, f_n = cm.ravel()

        #log metrics and parameters
        mlflow.log_metric("t_p", t_p)
        mlflow.log_metric("t_n", t_n)
        mlflow.log_metric("f_p", f_p)
        mlflow.log_metric("f_n", f_n)
        mlflow.log_param("solver", solver)
        mlflow.log_param("penalty", penalty)
        mlflow.log_param("c", c)
        mlflow.log_metric("f1", f1)
        mlflow.log_metric("roc", roc)
        mlflow.sklearn.log_model(log_reg, "model")
