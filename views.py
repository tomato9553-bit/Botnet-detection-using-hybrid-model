from django.shortcuts import render
from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import login ,logout,authenticate
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC

# Create your views here.
def home(request):
    return render(request,'home.html')


def register(request):
    if request.method == 'POST':
        First_Name = request.POST['name']
        Email = request.POST['email']
        username = request.POST['username']
        password = request.POST['password']
        confirmation_password = request.POST['cnfm_password']
        if password == confirmation_password:
            if User.objects.filter(username=username).exists():
                messages.error(request, 'Username already exists, please choose a different one.')
                return redirect('register')
            else:
                if User.objects.filter(email=Email).exists():
                    messages.error(request, 'Email already exists, please choose a different one.')
                    return redirect('register')
                else:
                    user = User.objects.create_user(
                        username=username,
                        password=password,
                        email=Email,
                        first_name=First_Name,
                    )
                    user.save()
                    return redirect('login')
        else:
            messages.error(request, 'Passwords do not match.')
        return render(request, 'register.html')
    return render(request, 'register.html')

def login_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        if User.objects.filter(username=username).exists():
            user=User.objects.get(username=username)
            if user.check_password(password):
                user = authenticate(username=username,password=password)
                if user is not None:
                    login(request,user)
                    messages.success(request,'login successfull')
                    return redirect('/')
                else:
                   messages.error(request,'please check the Password Properly')
                   return redirect('login')
            else:
                messages.error(request,"please check the Password Properly")  
                return redirect('login') 
        else:
            messages.error(request,"username doesn't exist")
            return redirect('login')
    return render(request,'login.html')
# Load and preprocess the dataset
def logout_view(request):
    logout(request)
    return redirect('login')

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression

from sklearn.preprocessing import StandardScaler

import warnings
warnings.filterwarnings('ignore')
import joblib
import os
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score
from sklearn.metrics import f1_score
from sklearn.metrics import accuracy_score,confusion_matrix,classification_report
from catboost import CatBoostClassifier
import pandas as pd
import joblib

def prediction(request):
    import pandas as pd
    import joblib
    from django.shortcuts import render

    # Load the trained model and encoders
    clf = joblib.load('model/HybridModel.pkl')
    encoders = joblib.load('model/label_encoders.pkl')
    categorical_cols = ['proto', 'saddr', 'sport', 'daddr', 'dport']

    # Manually defined class labels (must match model training)
    labels = ['DDoS', 'DoS', 'Reconnaissance', 'Normal']

    # Define feature labels for form display
    feature_labels = {
        "pkSeqID": "pk_Seq_ID",
        "proto": "Protocol",
        "saddr": "Source IP",
        "sport": "Source Port",
        "daddr": "Destination IP",
        "dport": "Destination Port",
        "seq": "Sequence Number",
        "stddev": "Standard Deviation",
        "N_IN_Conn_P_SrcIP": "Inbound Connections per Source IP",
        "min": "Minimum Value",
        "state_number": "State Number",
        "mean": "Mean",
        "N_IN_Conn_P_DstIP": "Inbound Connections per Destination IP",
        "drate": "Data Rate",
        "srate": "Service Rate",
        "max": "Maximum Value"
    }

    if request.method == "POST":
        input_data = {}

        for feature in feature_labels:
            value = request.POST.get(feature)
            if value is None or value.strip() == "":
                input_data[feature] = 0  # fallback default
            else:
                try:
                    input_data[feature] = float(value)
                except ValueError:
                    input_data[feature] = value.strip()

        df = pd.DataFrame([input_data])

        # Apply label encoders properly
        for col in categorical_cols:
            if col in df.columns:
                le = encoders[col]
                df[col] = df[col].apply(lambda x: le.transform([x])[0] if x in le.classes_ else le.transform([le.classes_[0]])[0])  # default to first known class

        # Debug: Check actual feature values
        print("Final Input to Model:", df.to_dict(orient="records"))

        # Predict
        prediction_index = clf.predict(df)[0]
        outcome = labels[prediction_index] if prediction_index < len(labels) else "Unknown"

        return render(request, 'outcome.html', {'outcome': outcome})

    return render(request, 'prediction.html', {"feature_labels": feature_labels})




from django.core.files.storage import default_storage
le=LabelEncoder()
dataloaded=False
global X_train,X_test,y_train,y_test
global df
def Upload_data(request):
    load=True
    global df,dataloaded
    global X_train,X_test,y_train,y_test
    if request.method == 'POST' and request.FILES.get('file'):
        uploaded_file = request.FILES['file']
        file_path = default_storage.save(uploaded_file.name, uploaded_file)
        df=pd.read_csv(default_storage.path(file_path))
        df.drop(["attack", "subcategory"], axis=1, inplace=True)

        le=LabelEncoder()
        categorical_cols = ['proto', 'saddr', 'sport','daddr','dport','category']
        encoders = {}

        for col in categorical_cols:
            le = LabelEncoder()
            df[col] = le.fit_transform(df[col])
            encoders[col] = le
        

        sns.set(style="darkgrid")  # Set the style of the plot
        plt.figure(figsize=(8, 6))  # Set the figure size
        ax = sns.countplot(x='category', data=df)
        plt.title("Count Plot")  # Add a title to the plot
        plt.xlabel("Categories")  # Add label to x-axis
        plt.ylabel("Count")  # Add label to y-axis
        # Annotate each bar with its count value
        for p in ax.patches:
            ax.annotate(f'{p.get_height()}', (p.get_x() + p.get_width() / 2., p.get_height()),
                        ha='center', va='center', fontsize=10, color='black', xytext=(0, 5),
                        textcoords='offset points')
        plt.xticks(rotation=90)
        plt.show()


        
        x = df.drop("category", axis=1)   # Replace "target" with your actual target column
        y = df["category"]
        target_encoder = LabelEncoder()
        y = target_encoder.fit_transform(y)
        joblib.dump(encoders, 'model/label_encoders.pkl')
        joblib.dump(target_encoder, 'model/target_encoder.pkl')
        X_train,X_test,y_train,y_test= train_test_split(x,y,test_size=0.20,random_state=42)
        default_storage.delete(file_path)
        outdata=df.head(100)
        dataloaded=True
        return render(request,'train.html',{'temp':outdata.to_html()})
    return render(request,'train.html',{'upload':load})
labels = ['DDoS', 'DoS', 'Reconnaissance', 'Normal']
#defining global variables to store accuracy and other metrics
precision = []
recall = []
fscore = []
accuracy = []
def calculateMetrics(algorithm, testY,predict):
    testY = testY.astype('int')
    predict = predict.astype('int')
    p = precision_score(testY, predict,average='macro') * 100
    r = recall_score(testY, predict,average='macro') * 100
    f = f1_score(testY, predict,average='macro') * 100
    a = accuracy_score(testY,predict)*100 
    accuracy.append(a)
    precision.append(p)
    recall.append(r)
    fscore.append(f)
    print(algorithm+' Accuracy    : '+str(a))
    print(algorithm+' Precision   : '+str(p))
    print(algorithm+' Recall      : '+str(r))
    print(algorithm+' FSCORE      : '+str(f))
    report=classification_report(predict, testY,target_names=labels)
    print('\n',algorithm+" classification report\n",report)
    conf_matrix = confusion_matrix(testY, predict) 
    plt.figure(figsize =(5, 5)) 
    ax = sns.heatmap(conf_matrix, xticklabels = labels, yticklabels = labels, annot = True, cmap="Blues" ,fmt ="g");
    ax.set_ylim([0,len(labels)])
    plt.title(algorithm+" Confusion matrix") 
    plt.ylabel('True class') 
    plt.xlabel('Predicted class') 
    plt.show()

import os
import joblib
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
    
def HybridModel(request):
    if dataloaded == False:
        return redirect('upload')

    model_path = 'model/HybridModel.pkl'
    os.makedirs('model', exist_ok=True)

    if os.path.exists(model_path):
        # Load the trained hybrid model from the file
        hybrid_model = joblib.load(model_path)
        print("Hybrid model loaded successfully.")
        predict = hybrid_model.predict(X_test)
        calculateMetrics("HybridModel", predict, y_test)
    else:
        # Create individual models
        rf = RandomForestClassifier()
        svm = SVC(probability=True)
        lr = LogisticRegression()

        # Create a hybrid model using VotingClassifier
        hybrid_model = VotingClassifier(estimators=[
            ('rf', rf),
            ('svm', svm),
            ('lr', lr)
        ], voting='soft')  # Use 'soft' voting to use predicted probabilities

        # Train the hybrid model
        hybrid_model.fit(X_train, y_train)

        # Save the trained hybrid model to a file
        joblib.dump(hybrid_model, model_path)
        print("Hybrid model saved successfully.")

        # Predict and evaluate
        predict = hybrid_model.predict(X_test)
        calculateMetrics("HybridModel", predict, y_test)

    return render(request, 'train.html',
                  {'algorithm': 'Hybrid Model (Voting Classifier)',
                   'accuracy': accuracy[-1],
                   'precision': precision[-1],
                   'recall': recall[-1],
                   'fscore': fscore[-1]})


def RNNModel(request):
    if dataloaded == False:
        return redirect('upload')

    import numpy as np
    from tensorflow.keras.models import Sequential, load_model
    from tensorflow.keras.layers import SimpleRNN, Dense
    from tensorflow.keras.callbacks import EarlyStopping
    import os

    model_path = 'model/RNNModel.h5'
    os.makedirs('model', exist_ok=True)

    # Reshape input: RNN expects 3D input [samples, timesteps, features]
    X_train_rnn = np.reshape(X_train, (X_train.shape[0], 1, X_train.shape[1]))
    X_test_rnn = np.reshape(X_test, (X_test.shape[0], 1, X_test.shape[1]))

    if os.path.exists(model_path):
        # Load the trained RNN model
        rnn_model = load_model(model_path)
        print("RNN model loaded successfully.")
    else:
        # Build the RNN model
        rnn_model = Sequential()
        rnn_model.add(SimpleRNN(64, activation='relu', input_shape=(1, X_train.shape[1])))
        rnn_model.add(Dense(1, activation='sigmoid'))  # Use softmax if multi-class

        rnn_model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

        # Train the model
        early_stop = EarlyStopping(monitor='val_loss', patience=3, restore_best_weights=True)
        rnn_model.fit(X_train_rnn, y_train, epochs=20, batch_size=32,
                      validation_split=0.2, callbacks=[early_stop], verbose=1)

        # Save the trained model
        rnn_model.save(model_path)
        print("RNN model saved successfully.")

    # Predict and evaluate
    y_pred_probs = rnn_model.predict(X_test_rnn)
    y_pred = (y_pred_probs > 0.5).astype(int)

    calculateMetrics("RNNModel", y_test, y_pred  )

    return render(request, 'train.html',
                  {'algorithm': 'Recurrent Neural Network (RNN)',
                   'accuracy': accuracy[-1],
                   'precision': precision[-1],
                   'recall': recall[-1],
                   'fscore': fscore[-1]})


