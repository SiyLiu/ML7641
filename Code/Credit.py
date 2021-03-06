# -*- coding: utf-8 -*-
"""
Created on Sat Sep 19 18:47:48 2020

@author: Liu
"""

import pandas as pd
import numpy as np
import seaborn as sbn
import matplotlib.pyplot as plt
from helper import *

from sklearn.model_selection import learning_curve, train_test_split,GridSearchCV
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import roc_auc_score, accuracy_score, f1_score, precision_score, recall_score, confusion_matrix

raw_data = pd.read_csv("../Data/default_of_credit_card_clients.csv",header = 0)

#Check data sanity
raw_data.describe()
raw_data.isnull().sum()

#Check character variables levels

#SEX, EDUCATION, MARRIAGE

raw_data['SEX'].value_counts()
# 1    11888
# 2    18112

raw_data.groupby('EDUCATION')['EDUCATION'].count()
# 0       14
# 1    10585
# 2    14030
# 3     4917
# 4      123
# 5      280
# 6       51

raw_data.groupby('MARRIAGE')['MARRIAGE'].count()

# 0       54
# 1    13659
# 2    15964
# 3      323

# Chcek if the data is balanced
raw_data['default_payment_next_month'].value_counts()

# 0    23364
# 1     6636


# divide into test and training
raw_data.drop('ID',inplace = True,axis = 1)
_y_target = raw_data['default_payment_next_month'].values
columns = raw_data.columns.tolist()
columns.remove('default_payment_next_month')
_x_attributes = raw_data[columns].values

_x_train,_x_test,_y_train, _y_test = train_test_split(_x_attributes, _y_target, test_size =0.30, stratify = _y_target, random_state = 1)

#Check the distribution
len(_y_test) #3000
sum(_y_test) #1991

len(_y_train) #9000
sum(_y_train) #4645

#Decision Tree
init_clf = DecisionTreeClassifier(random_state = 1)
init_clf.fit(_x_train,_y_train)
init_clf.get_depth() #41

def hyperTree(X_train, y_train, X_test, y_test, title):
    
    f1_test = []
    f1_train = []
    
    auc_test = []
    auc_train = []
    max_depth = list(range(1,41))
    for i in max_depth:         
            clf = DecisionTreeClassifier(max_depth=i, random_state=1, min_samples_leaf=1, criterion='gini')
            clf.fit(X_train, y_train)
            y_pred_test = clf.predict(X_test)
            y_pred_train = clf.predict(X_train)
            f1_test.append(f1_score(y_test, y_pred_test))
            f1_train.append(f1_score(y_train, y_pred_train))
            auc_test.append(roc_auc_score(y_test, y_pred_test))
            auc_train.append(roc_auc_score(y_train, y_pred_train))
      
    plt.plot(max_depth, f1_test, 'o-', color='r', label='Test F1 Score')
    plt.plot(max_depth, f1_train, 'o-', color = 'b', label='Train F1 Score')
    plt.ylabel('Model F1 Score')
    plt.xlabel('Max Tree Depth')
    
    plt.title(title)
    plt.legend(loc='best')
    plt.tight_layout()
    plt.show()
    
 #Per hyperparameter tuning, best 
 
     
def TreeGridSearchCV(start_leaf_n, end_leaf_n, X_train, y_train):
    #parameters to search:
    #20 values of min_samples leaf from 0.5% sample to 5% of the training data
    #20 values of max_depth from 1, 10
    param_grid = {'min_samples_leaf':np.linspace(start_leaf_n,end_leaf_n,20).round().astype('int'), 'max_depth':np.arange(1,10),
                  'class_weight':["balanced"] }

    tree = GridSearchCV(estimator = DecisionTreeClassifier(), param_grid=param_grid, cv=10,refit=True)
    tree.fit(X_train, y_train)
    print("Per Hyperparameter tuning, best parameters are:")
    print(tree.best_params_)
    return tree.best_params_['max_depth'], tree.best_params_['min_samples_leaf']


hyperTree(_x_train, _y_train, _x_test, _y_test, "Credit Default Data")  

#Grid Search

#Pre-pruning
start_leaf_n = round(0.005*len(_x_train))
end_leaf_n = round(.05*len(_x_train))

best_depth, best_min_sample_leaf, best_min_sample_split = TreeGridSearchCV(start_leaf_n,
                                                     end_leaf_n,
                                                     _x_train,
                                                     _y_train)
#Per Hyperparameter tuning, best parameters are:
# {'max_depth': 4, 'min_samples_leaf': 204}

start_leaf_n = round(0.001*len(_x_train))
end_leaf_n = round(.01*len(_x_train))

#Add a parameter, min_samples_split (5,10,15), class_weight = balanced
# {'class_weight': 'balanced', 'max_depth': 1, 'min_samples_leaf': 105, 'min_samples_split': 5}


best_depth, best_min_sample_leaf = TreeGridSearchCV(start_leaf_n,
                                                     end_leaf_n,
                                                     _x_train,
                                                     _y_train)

# Per Hyperparameter tuning, best parameters are:
# {'class_weight': 'balanced', 'max_depth': 1, 'min_samples_leaf': 21}

#Post-pruning
post_prune = init_clf.cost_copmlexity_pruning_path(_x_train,_y_train)
ccp_alphas, impurities = post_prune.ccp_alphas, post_prune.imjurities



# {'class_weight': 'balanced', 'max_depth': 1, 'min_samples_leaf': 105, 'min_samples_split': 5}


#candidate parameter combination:
    # max_depth = 4, min_samples_leaf = 204
    # max_depth = 1, min_samples_leaf = 21, class_weight = "balanced"
    # max_depth = 1, min_sapmles_leaf = 105, min_samples_split = 5, class_weight ="balanced"
    

#Plot learning curves with best models

DT_credit =  DecisionTreeClassifier(random_state=1,
                                    max_depth=4, 
                                    min_samples_leaf=204,
                                    criterion='gini', 
                                    class_weight = "balanced")
train_samp_phish, DT_train_score_phish, DT_fit_time_phish,DT_pred_time_phish = plot_learning_curve(DT_credit, _x_train, _y_train,
                                             title="Decision Tree Credit Data")

final_classifier_evaluation(DT_credit, _x_train, _x_test, _y_train, _y_test)

#  Model Evaluation Metrics Using Untouched Test Dataset
# *****************************************************
# Model Training Time (s):   0.14153
# Model Prediction Time (s): 0.00139

# F1 Score:  0.53
# Accuracy:  0.78     AUC:       0.70
# Precision: 0.50     Recall:    0.56
# *****************************************************   
    
#Post prune
clf = DecisionTreeClassifier(random_state = 1)
path = clf.cost_complexity_pruning_path(_x_train, _y_train)

ccp_alphas, impurities = path.ccp_alphas, path.impurities

fig, ax = plt.subplots()
ax.plot(ccp_alphas[:-1], impurities[:-1], marker='o', drawstyle="steps-post")
ax.set_xlabel("effective alpha")
ax.set_ylabel("total impurity of leaves")
ax.set_title("Total Impurity vs effective alpha for training set")

    
clfs = []
for ccp_alpha in ccp_alphas:
    clf = DecisionTreeClassifier(random_state=1, ccp_alpha=ccp_alpha)
    clf.fit(_x_train, _y_train)
    clfs.append(clf)
print("Number of nodes in the last tree is: {} with ccp_alpha: {}".format(
      clfs[-1].tree_.node_count, ccp_alphas[-1]))  

#Number of nodes in the last tree is: 1 with ccp_alpha: 0.05344842427328045

clfs2 = clfs[1300:]
ccp_alphas2 = ccp_alphas[1300:]

node_counts = [clf.tree_.node_count for clf in clfs2]
depth = [clf.tree_.max_depth for clf in clfs2]
fig, ax = plt.subplots(2, 1)
ax[0].plot(ccp_alphas2, node_counts, marker='o', drawstyle="steps-post")
ax[0].set_xlabel("alpha")
ax[0].set_ylabel("number of nodes")
ax[0].set_title("Number of nodes vs alpha")
ax[1].plot(ccp_alphas2, depth, marker='o', drawstyle="steps-post")
ax[1].set_xlabel("alpha")
ax[1].set_ylabel("depth of tree")
ax[1].set_title("Depth vs alpha")
fig.tight_layout()


DT_credit2 =  DecisionTreeClassifier(ccp_alpha=0.0004,
                                    random_state=1, criterion='gini', 
                                    class_weight = "balanced")
train_samp_phish, DT_train_score_phish, DT_fit_time_phish,DT_pred_time_phish = plot_learning_curve(DT_credit2, _x_train, _y_train,
                                             title="Decision Tree Credit Data")

final_classifier_evaluation(DT_credit2, _x_train, _x_test, _y_train, _y_test)
# *****************************************************
# Model Training Time (s):   0.54855
# Model Prediction Time (s): 0.00160

# F1 Score:  0.53
# Accuracy:  0.75     AUC:       0.71
# Precision: 0.45     Recall:    0.63
# *****************************************************

## Artificial Neural Network
from sklearn.neural_network import MLPClassifier
from sklearn import preprocessing

#Normalize the data before building the ANN model
scaler = preprocessing.StandardScaler().fit(_x_train)
scale_x_train = scaler.transform(_x_train)
scale_x_test = scaler.transform(_x_test)


def hyperNN(X_train, y_train, X_test, y_test, title, activation = "logistic"):

    f1_test = []
    f1_train = []
    hlist = np.linspace(1,15,15).astype('int')
    for i in hlist:         
            clf = MLPClassifier(hidden_layer_sizes=(i,), solver='adam', activation=activation, 
                                learning_rate_init=0.05, random_state=1)
            clf.fit(X_train, y_train)
            y_pred_test = clf.predict(X_test)
            y_pred_train = clf.predict(X_train)
            f1_test.append(f1_score(y_test, y_pred_test))
            f1_train.append(f1_score(y_train, y_pred_train))
      
    plt.plot(hlist, f1_test, 'o-', color='r', label='Test F1 Score')
    plt.plot(hlist, f1_train, 'o-', color = 'b', label='Train F1 Score')
    plt.ylabel('Model F1 Score')
    plt.xlabel('No. Hidden Units')
    
    plt.title(title)
    plt.legend(loc='best')
    plt.tight_layout()
    plt.show()
    
hyperNN(scale_x_train,_y_train, scale_x_test, _y_test, "Credit Data Neural Network", activation = "logistic")
# alpha = 0.05, hidden_layer = 1

   
def NNGridSearchCV(X_train, y_train,hidden, alpha):
    #parameters to search:
    #number of hidden units
    #learning_rate

    param_grid = {'hidden_layer_sizes': hidden, 
                  'learning_rate_init': alpha,
                  'activation':['logistic','relu']}

    net = GridSearchCV(estimator = MLPClassifier(solver='adam',random_state=1),
                       param_grid=param_grid, cv=10)
    net.fit(X_train, y_train)
    print("Per Hyperparameter tuning, best parameters are:")
    print(net.best_params_)
    return net.best_params_['hidden_layer_sizes'], net.best_params_['learning_rate_init'], net.best_params_['activation']

 
d = _x_train.shape[1]
hiddens = [(h,)*l for l in [1,2,3] for h in [d,d//2,d*2 ]]
alphas = [10**-x for x in np.arange(-2,2.0,1)]

hidden_layers, learning_rate, activation = NNGridSearchCV(scale_x_train,
                                                          _y_train, 
                                                          hiddens, 
                                                          alphas)  
# Per Hyperparameter tuning, best parameters are:
# {'activation': 'logistic', 'hidden_layer_sizes': (23, 23, 23), 'learning_rate_init': 0.1}

ANN_credit = MLPClassifier(hidden_layer_sizes = hidden_layers,
                           activation = activation,
                           solver = "adam",
                           random_state = 1)

train_samp_phish, NN_train_score_phish, NN_fit_time_phish, \
    NN_pred_time_phish = plot_learning_curve(ANN_credit, \
    scale_x_train, _y_train,title="Neural Net Credit Data")
final_classifier_evaluation(ANN_credit, scale_x_train, scale_x_test, _y_train, _y_test)
    
# *****************************************************
# Model Training Time (s):   30.40333
# Model Prediction Time (s): 0.03332

# F1 Score:  0.47
# Accuracy:  0.82     AUC:       0.66
# Precision: 0.67     Recall:    0.36
# *****************************************************



#Boosting - more aggresive in pruning
#max_depth of the decision tree: 4
#min_samples_leaf: 204
from sklearn.ensemble import GradientBoostingClassifier
def hyperBoost(X_train, y_train, X_test, y_test, max_depth, min_samples_leaf, title):
    
    f1_test = []
    f1_train = []
    n_estimators = np.linspace(10,200,20).astype('int')
    for i in n_estimators:         
            clf = GradientBoostingClassifier(n_estimators=i, max_depth=int(max_depth/2), 
                                             min_samples_leaf=int(min_samples_leaf/2), random_state=1,)
            clf.fit(X_train, y_train)
            y_pred_test = clf.predict(X_test)
            y_pred_train = clf.predict(X_train)
            f1_test.append(f1_score(y_test, y_pred_test))
            f1_train.append(f1_score(y_train, y_pred_train))
      
    plt.plot(n_estimators, f1_test, 'o-', color='r', label='Test F1 Score')
    plt.plot(n_estimators, f1_train, 'o-', color = 'b', label='Train F1 Score')
    plt.ylabel('Model F1 Score')
    plt.xlabel('No. Estimators')
    
    plt.title(title)
    plt.legend(loc='best')
    plt.tight_layout()
    plt.show()
    
hyperBoost(_x_train, _y_train, _x_test, _y_test, 4, 204, 
           "Model Complexity Curve for Boosted Tree (Credit Data)\nHyperparameter : No. Estimators")

def BoostedGridSearchCV(start_leaf_n, end_leaf_n, X_train, y_train):
    #parameters to search:
    #n_estimators, learning_rate, max_depth, min_samples_leaf
    param_grid = {'min_samples_leaf': np.linspace(start_leaf_n,end_leaf_n,3).round().astype('int'),
                  'max_depth': np.arange(1,4),
                  'n_estimators': np.linspace(10,100,3).round().astype('int'),
                  'learning_rate': np.linspace(.001,.1,3)}

    boost = GridSearchCV(estimator = GradientBoostingClassifier(), param_grid=param_grid, cv=10)
    boost.fit(X_train, y_train)
    print("Per Hyperparameter tuning, best parameters are:")
    print(boost.best_params_)
    return boost.best_params_['max_depth'], boost.best_params_['min_samples_leaf'], boost.best_params_['n_estimators'], boost.best_params_['learning_rate']

start_leaf_n = round(0.005*len(_x_train))
end_leaf_n = round(0.05*len(_x_train))  

max_depth, min_samples_leaf, n_est, learn_rate = BoostedGridSearchCV(start_leaf_n,end_leaf_n,_x_train,_y_train) 

#Per Hyperparameter tuning, best parameters are:
#{'learning_rate': 0.1, 'max_depth': 3, 'min_samples_leaf': 1050, 'n_estimators': 55}

Boost_credit = GradientBoostingClassifier(max_depth=max_depth, min_samples_leaf=min_samples_leaf, 
                                              n_estimators=n_est, learning_rate=learn_rate, random_state=1)

train_samp_phish, BT_train_score_phish, BT_fit_time_phish, BT_pred_time_phish = plot_learning_curve(Boost_credit, _x_train, _y_train,title="Boosted Tree Credit Data")
final_classifier_evaluation(Boost_credit, _x_train, _x_test, _y_train, _y_test)

# *****************************************************
# Model Training Time (s):   8.52702
# Model Prediction Time (s): 0.04931

# F1 Score:  0.47
# Accuracy:  0.82     AUC:       0.66
# Precision: 0.66     Recall:    0.36
# *****************************************************


 #SVM

def hyperSVM(X_train, y_train, X_test, y_test, title):

    f1_test = []
    f1_train = []
    kernel_func = ['linear','poly','rbf','sigmoid']
    for i in kernel_func:         
            if i == 'poly':
                for j in [2,3,4]:
                    clf = SVC(kernel=i, degree=j,random_state=100)
                    clf.fit(X_train, y_train)
                    y_pred_test = clf.predict(X_test)
                    y_pred_train = clf.predict(X_train)
                    f1_test.append(f1_score(y_test, y_pred_test))
                    f1_train.append(f1_score(y_train, y_pred_train))
            else:    
                clf = SVC(kernel=i, random_state=100)
                clf.fit(X_train, y_train)
                y_pred_test = clf.predict(X_test)
                y_pred_train = clf.predict(X_train)
                f1_test.append(f1_score(y_test, y_pred_test))
                f1_train.append(f1_score(y_train, y_pred_train))
                
    xvals = ['linear','poly2','poly3','poly4','rbf','sigmoid']
    plt.plot(xvals, f1_test, 'o-', color='r', label='Test F1 Score')
    plt.plot(xvals, f1_train, 'o-', color = 'b', label='Train F1 Score')
    plt.ylabel('Model F1 Score')
    plt.xlabel('Kernel Function')
    
    plt.title(title)
    plt.legend(loc='best')
    plt.tight_layout()
    plt.show()

hyperSVM(scale_x_train, _y_train, scale_x_test, _y_test, "SVM with different kernels, Credit Data")
    
#RBF is the best

## KNN

from sklearn.neighbors import KNeighborsClassifier as kNN

def hyperKNN(X_train, y_train, X_test, y_test, title):
    
    f1_test = []
    f1_train = []
    klist = np.linspace(10,400,40).astype('int')
    for i in klist:
        clf = kNN(n_neighbors=i,n_jobs=-1)
        clf.fit(X_train,y_train)
        y_pred_test = clf.predict(X_test)
        y_pred_train = clf.predict(X_train)
        f1_test.append(f1_score(y_test, y_pred_test))
        f1_train.append(f1_score(y_train, y_pred_train))
        
    plt.plot(klist, f1_test, 'o-', color='r', label='Test F1 Score')
    plt.plot(klist, f1_train, 'o-', color = 'b', label='Train F1 Score')
    plt.ylabel('Model F1 Score')
    plt.xlabel('No. Neighbors')
    
    plt.title(title)
    plt.legend(loc='best')
    plt.tight_layout()
    plt.show()
    
hyperKNN(scale_x_train, _y_train, scale_x_test, _y_test,title="Model Complexity Curve for kNN (Diabetes Data)\nHyperparameter : No. Neighbors")

