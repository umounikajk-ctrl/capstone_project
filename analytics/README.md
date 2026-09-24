# Module 2 — Analytics Pipeline

## 1. Overview

This module implements an end-to-end analytics and predictive-modeling workflow using the classic **Titanic dataset**.

The pipeline covers:

1. Dataset loading and profiling
2. Missing-value analysis and cleaning
3. Univariate analysis
4. Bivariate analysis
5. Multivariate data-story visualizations
6. Exploratory feature standardization
7. Stratified train/test splitting
8. Training-only preprocessing using `Pipeline` and `ColumnTransformer`
9. Logistic Regression, Decision Tree, and Random Forest classification
10. Model evaluation using multiple classification metrics
11. Class-imbalance comparison
12. Random Forest hyperparameter tuning
13. Multivariate Linear Regression for fare prediction
14. Model comparison
15. Saving and reloading the complete fitted pipeline using `joblib`

The module is organized as a continuation from EDA to modeling rather than as two independent exercises.
---

# 2. Project Structure

analytics/
│
├── 01_eda.ipynb
├── 02_modeling.ipynb
├── titanic.csv
│
├── charts/
│   ├── age_histogram.png
│   ├── age_boxplot.png
│   ├── fare_histogram.png
│   ├── fare_boxplot.png
│   ├── survival_rate_by_sex.png
│   ├── survival_rate_by_pclass.png
│   ├── survival_rate_by_sex_pclass.png
│   ├── correlation_heatmap.png
│   ├── fare_distribution_by_survival.png
│   ├── decision_tree.png
│   ├── residual_plot.png
│   ├── roc_curves.png 
│
├── titanic_survival_pipeline.joblib
│
└── README.md
|__requirements.txt


1. 01_eda.ipynb — loads sns.load_dataset('titanic') once, profiles it, cleans it, saves titanic.csv, produces the full EDA story

2. 02_modeling.ipynb — reads the committed titanic.csv, continues into preprocessing, modeling, tuning, and the regression side-task

3. titanic.csv — committed offline fallback (pd.read_csv("titanic.csv") reproduces the module without network access)

4. titanic_survival_pipeline.joblib — final fitted pipeline (preprocessing + classifier), usable end-to-end on raw input

5. charts/ — all saved chart images#

# 3. Dataset Loading

The Titanic dataset is loaded using Seaborn:

```python
import seaborn as sns

df = sns.load_dataset("titanic")
```

The raw dataset is loaded only once.

Immediately after loading, the original dataset is saved as an offline CSV fallback:

```python
df.to_csv("titanic.csv", index=False)
```

The modeling notebook does not independently call `sns.load_dataset()` again. Instead, it continues from the cleaned dataset / committed `titanic.csv`.

This allows the project to be executed even when internet access is unavailable during grading.

---

# 4. Dataset Profiling

The dataset was profiled using:

```python
df.info()
df.describe()
df.shape
```

The following information was examined:

* Number of rows and columns
* Data types
* Numerical summary statistics
* Missing values
* Distribution of the target variable
* Potential data-quality issues

The Titanic dataset contains the target column:

```text
survived
```

where:

```text
0 = Did not survive
1 = Survived
```

The observed class distribution was approximately:

| Class           | Percentage |
| --------------- | ---------: |
| Did not survive |     `61.8%`|
| Survived        |    `38.2%` |

Because the target classes are not equally distributed, stratification was used during the train/test split.

---

# 5. Missing-Value Analysis

Column : `age`
% Missing : `19.87%`
Strategy : `Impute (mean)`
Justification : `Falls in the 5%–30% band → impute rather than drop`

Column : `deck`
% Missing : `~77%`
Strategy : `Drop column`
Justification : `Missing rate is too high for reliable imputation; dropped rather than encoded as "missing"`

Column : `embarked`
% Missing : `0.22%`
Strategy : `Drop rows`
Justification : `Under 5% missing → row removal has negligible impact`

Column : `embark_town`
% Missing : `0.22%`
Strategy : `Drop rows`
Justification : `Under 5% missing → row removal has negligible impact`

---

# 6. Cleaned Dataset

After missing-value handling, the cleaned dataset was stored in:

```python
df1
```

The cleaned dataset is used for the remaining EDA and modeling workflow.

The modeling features are separated from the target as follows:

```python
X = df1.drop("survived", axis=1)
y = df1["survived"]
```

---

# 7. Univariate Analysis

## 7.1 Age Distribution

A histogram and box plot were created for `age`.

The histogram shows the distribution of passenger ages, while the box plot was used to identify potential outliers using the IQR rule.

### interpretation

The age distribution shows that Titanic passengers were spread across children, young adults, middle-aged adults, and older passengers.

The box plot highlights observations outside the IQR boundaries. These observations were considered potential statistical outliers rather than automatically being removed, because extreme ages can represent genuine passengers.

**Age outlier count:** 65

---

# 8. Fare Distribution

A histogram and box plot were created for `fare`.

The following statistics were calculated:

| Statistic |   Fare  |
| --------- | --------|
| Mean      | 32.1    |
| Median    | 14.45   |
| Mode      | 8.05    |

### interpretation

1. The fare distribution is **right-skewed** becaused Mean > Median > Mode

2. The right tail is influenced by passengers who paid substantially higher fares than most passengers.

**Fare outlier count:** 114

---

# 9. Bivariate Analysis

## 9.1 Survival Rate by Sex

The result shows different survival rates between male and female passengers.

### Interpretation

The survival rate differed substantially by sex. Female passengers had a higher observed survival rate than male passengers in the cleaned Titanic dataset.

This indicates that `sex` is an important predictive feature for the survival target.

|    Sex    |Survival rate|
| --------- | ------------|
| Male      | `18.89%`    |
| Female    | `74.04%`    |


---

# 10. Survival Rate by Passenger Class

### Interpretation

Survival rates varied across passenger classes.

The results indicate an association between passenger class and survival, with higher-class passengers having different observed survival outcomes from lower-class passengers.

| Pclass | Survival rate|
| ------ | -------------|
| 1      | `62.62%`     |
| 2      | `47.28%`     |
| 3      | `24.24%`     |
---

# 11. Survival Rate by Sex and Passenger Class

see "charts/survival_rate_by_sex_and_class.png" for the full breakdown; survival was highest for first-class women and lowest for third-class men.

### Interpretation

Combining `sex` and `pclass` provides a more detailed view than either variable individually.

The results show that survival outcomes varied substantially across combinations of passenger sex and passenger class, demonstrating the usefulness of interaction-style analysis for understanding the Titanic survival pattern.

---

# 12. Correlation Analysis

The correlation matrix was intentionally restricted to exactly these six numerical columns:

```python
corr_columns = [
    "survived",
    "pclass",
    "age",
    "sibsp",
    "parch",
    "fare"
]
```
The following columns were deliberately excluded:

1. adult_male
2. alone

These are derived/boolean flags rather than independent measured numerical features.

### Two strongest correlations

The two feature pairs with the largest absolute off-diagonal correlation coefficients were identified by ranking:

Results:

| Rank | Feature pair              | Correlation |
| ---- | ------------------------- | ----------: |
| 1    | Pclass and Fare           |   `−0.55`   |
| 2    | sibsp and parch           |   `+0.41`   |

### Interpretation

1. pclass ↔ fare (≈ −0.55) — the strongest relationship in the matrix. Higher-numbered (lower) classes paid systematically lower fares; first-class passengers paid the most.

2. sibsp ↔ parch (≈ +0.41) — passengers traveling with more siblings/spouses also tended to travel with more parents/children, i.e. family-group size correlates across both counts.

---

# 13. Multivariate Data Story

At least four different charts were produced to build a combined story about Titanic survival.

## Chart 1 — Survival Rate by Sex

"charts/survival_rate_by_sex.png" Female passengers had a substantially higher survival rate than male passengers — roughly three-quarters of women survived versus under a fifth of men — showing sex was strongly associated with survival.

---

## Chart 2 — Survival Rate by Passenger Class

"charts/survival_rate_by_passenger_class.png" Survival rates fell steadily from first to third class, with first-class passengers surviving at the highest rate, indicating passenger class was an important survival factor.

---

## Chart 3 — Survival by Sex and Passenger Class

"charts/survival_rate_by_sex_and_class.png" Combining sex and class shows both factors act together: women had high survival rates across all classes, while male third-class passengers had especially low survival — evidence of an interaction effect, not two independent effects.

---

## Chart 4 — Age/Fare/Survival Relationship

"charts/fare_distribution_by_survival.png" Survivors generally paid higher fares than non-survivors, though the distributions overlap substantially — consistent with fare acting as a proxy for the class-based survival pattern above, not proof of a direct causal effect

### Overall conclusion: 

Survival on the Titanic was strongly associated with sex and passenger class, with the interaction of the two (male, third class) showing the starkest disadvantage. Fare differences track the same socioeconomic pattern but should not be read as causal on their own.
---

# 14. Standardization sanity check (EDA-stage only)

age_z and fare_z computed as (x − mean) / std on the full cleaned DataFrame.

As an EDA-stage experiment, `age` and `fare` were standardized using the z-score formula:

| Feature | Mean (Before) | Std (Before) | Mean (After, Z-score) | Std (After, Z-score) |
| ------- | ------------: | -----------: | --------------------: | -------------------: |
| `age`   |     29.65     |    12.97     |                  0.00 |                 1.00 |
| `fare`  |     32.1      |    49.7      |                  0.00 |                 1.00 |

# Part B — Predictive Modeling

1. removing 'class' and 'embark_town' from the dataset as they are duplicate columns for 'pclass' and 'embarked'
2. removing 'alive' from the dataset as it is deuplicate column for 'survived' (target column) and causes data leakage and may overfit the data
3. removing 'who' and 'adult_male' columns because these are derived from column 'sex' and 'age'.
4. also to avoid giving the model multiple highly related versions of the same information.

```python
df1 = df1.drop(["class", "embark_town", "alive","who","adult_male"],axis=1)
```

# 15. Train/Test Split

The data was divided into training and testing sets before preprocessing:

```python
X = df1.drop("survived", axis=1)
y = df1["survived"]

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)
```

The test set contains 20% of the data.

## Why stratification was used

The target contains approximately:

```text
61.8% non-survivors
38.2% survivors
```

Therefore, stratification preserves approximately the same target-class proportions in both training and testing datasets.

---

# 16. Modeling Preprocessing Pipeline

Preprocessing was implemented using `ColumnTransformer` and `Pipeline`.

The main preprocessing structure is:

```python
preprocessor = ColumnTransformer(
    transformers=[
        (
            "age",
            Pipeline([
                ("imputer", SimpleImputer(strategy="mean")),
                ("scaler", StandardScaler())
            ]),
            ["age"]
        ),

        (
            "numeric",
            StandardScaler(),
            ["pclass", "sibsp", "parch", "fare"]
        ),

        (
            "encode",
            OneHotEncoder(handle_unknown="ignore"),
            ["sex", "embarked", "alone"]
        )
    ],
    remainder="drop"
)
```

The preprocessing pipeline was then created using:

```python
pipe = Pipeline([
    ("preprocessor", preprocessor)
])
```
Implemented as a ColumnTransformer inside a Pipeline:

1. age → SimpleImputer(strategy='mean') + StandardScaler
2. pclass, sibsp, parch, fare → StandardScaler
3. sex, embarked, alone → OneHotEncoder(handle_unknown='ignore')

All steps are .fit() on X_train only and applied .transform()-only to X_test — no leakage from test data into any fitted preprocessing step.

---

# 17. Classification Models

Three classification algorithms were trained using the same train/test split:

1. Logistic Regression
2. Decision Tree
3. Random Forest

The models were evaluated using:

* Accuracy
* Precision
* Recall
* F1 score
* Confusion matrix
* ROC curve
* AUC

---

# 18. Decision Tree Visualization

The trained Decision Tree was visualized using:

```python
from sklearn.tree import plot_tree

plot_tree(
    decision_tree,
    feature_names=feature_names,
    class_names=["Not Survived", "Survived"],
    filled=True
)
```

Decision tree visualized via plot_tree with labeled feature names and class names (charts/decision_tree.png). ROC curves with AUC for all three models: charts/roc_curves.png.

---

# 19. Classification Model Results

The classification results should be reported in a common comparison table.


| Model                 | Accuracy | Precision | Recall | F1-Score | AUC Score | Confusion Matrix     |
| ----------------------| -------: | --------: | -----: | -------: | --------: | ---------------------|
| `Logistic Regression` |    0.820 |     0.800 |  0.706 |    0.750 |     0.865 | [[98, 12], [20, 48]] |
| `Decision Tree`       |    0.798 |     0.776 |  0.662 |    0.714 |     0.853 | [[97, 13], [23, 45]] |
| `Random Forest`       |    0.787 |     0.742 |  0.676 |    0.708 |     0.820 | [[94, 16], [22, 46]] |


All three models were evaluated on the same test set so that their metrics can be compared consistently.

---

# 20. Class Imbalance Analysis

The target distribution was:

| Target       | Percentage |
| ------------ | ---------: |
| Not Survived |     ~61.8% |
| Survived     |     ~38.2% |

Three approaches were compared:

1. Baseline model
2. `class_weight="balanced"`
3. SMOTE oversampling

The comparison was performed using the same training/test split.

## SMOTE

SMOTE was applied only to the training data.

Conceptually:

```text
Original Training Data
        |
        v
      SMOTE
        |
        v
Balanced Training Data
        |
        v
      Model
        |
        v
Original Test Data
```

The test data was not oversampled.

This prevents synthetic samples generated from test observations from influencing model training.

### Imbalance comparison

| Model                                           | Precision | Recall | F1-Score |
| ------------------------------------------------| --------: | -----: | -------: |
| Logistic Regression (Base Model)                |     0.800 |  0.706 |    0.750 |
| Logistic Regression (`class_weight='balanced'`) |     0.736 |  0.779 |    0.757 |
| Logistic Regression (SMOTE Oversampling)        |     0.754 |  0.765 |    0.759 |


### Interpretation

The three strategies produced different precision, recall, and F1 values.

SMOTE gave the best overall balance between precision and recall, achieving the highest F1-score (0.759). The balanced baseline improved recall at the cost of precision, while the untouched baseline favored precision over recall — SMOTE was the best trade-off for this dataset.

---

# 21. Random Forest Hyperparameter Tuning

`GridSearchCV` was used to tune the Random Forest.

The search included:

```text
n_estimators
max_depth
max_features
```

The Random Forest estimator was created with:

```python
RandomForestClassifier(
    oob_score=True,
    random_state=42
)
```

This is required because the OOB score is only available when:

```python
oob_score=True
```
is enabled.

### Best parameters, Best CV ROC-AUC, OOB Score

Best parameters: {'max_depth': 5, 'max_features': 'sqrt', 'n_estimators': 200}
Best CV ROC-AUC: 0.875
OOB score: 0.827

The OOB score provides an additional estimate of Random Forest generalization using observations not selected in individual bootstrap samples.

---

# 22. Regression Side Task

A multivariate Linear Regression model was developed to predict:

```text
fare
```

from the other available passenger features.

The model was evaluated using:

* Mean Absolute Error (MAE)
* Root Mean Squared Error (RMSE)
* R²
* Adjusted R²

## Regression results

| Metric      |  Value |
| ------------| -----: |
| MAE         |  21.10 |
| RMSE        |  41.70 |
| R²          | 0.3482 |
| Adjusted R² | 0.3008 |

The multivariate linear regression model achieved an MAE of 21.10, an RMSE of 41.70, an R² of 0.3482, and an Adjusted R² of 0.3008. The R² indicates that the model explains approximately 34.82% of the variation in fare. 

---

# 23. Residual Analysis

A residual plot was generated to evaluate the behavior of the regression errors.

Residual:

```text
Residual = Actual Fare - Predicted Fare
```

### Heteroscedasticity interpretation

The residual plot shows evidence of heteroscedasticity because the spread of residuals increases as the predicted fare increases. Several large residuals are also visible at higher predicted fare values, suggesting the presence of outliers and that a simple linear model does not fully capture the variation in fare.

---

# 24. Final Model Comparison

Classification and regression metrics are different types of measurements and therefore are presented as separate metric groups.

## Classification

| Model               | Accuracy| Precision|  Recall |      F1 |     AUC |
| ------------------- | --------| ---------| --------| --------| --------|
| Logistic Regression | `0.820` | `0.800`  | `0.706` | `0.750` | `0.865` |
| Decision Tree       | `0.798` | `0.776`  | `0.662` | `0.714` | `0.853` |
| Random Forest       | `0.787` | `0.742`  | `0.676` | `0.708` | `0.820` |

## Regression

| Model             |     MAE |    RMSE |       R² | Adjusted R²|
| ----------------- | --------| --------| ---------| -----------|
| Linear Regression | `21.10` | `41.70` | `0.3482` |  `0.3008`  |


Classification and regression metrics should not be interpreted as values on one common performance scale.

---

# 25. Final Model Recommendation

Final recommendation: Logistic Regression is recommended for deployment. It achieved the highest accuracy (0.820), precision (0.800), and AUC (0.865) among the three classifiers, along with the highest F1-score (0.750) and a recall (0.706) that exceeded both the Decision Tree (0.662) and Random Forest (0.676). Neither tree-based model outperformed it on any metric that matters for this task, making Logistic Regression the strongest overall choice for predicting Titanic survival.

The selected model achieved:
----------------------|
Accuracy  = 0.820     |
Precision = 0.800     |
Recall    = 0.706     |
F1        = 0.750     |
AUC       = 0.865     |
----------------------|
**Selected deployment model:** `Logistic Regression`

These metrics indicate how effectively the selected model distinguishes between passengers who survived and passengers who did not survive.

The final model was selected based on the observed evaluation results rather than relying on a single metric. The same test split was used for the classifier comparison to ensure a consistent evaluation basis.

---

# 26. Complete Pipeline Saving

The final preprocessing and estimator were combined into a single scikit-learn pipeline.

The important requirement is that the saved object contains both:

```text
Raw input
   |
   v
Imputation
   |
   v
Encoding
   |
   v
Scaling
   |
   v
Final classifier
   |
   v
Prediction
```

The complete pipeline was saved using:

```python
import joblib

joblib.dump(
    full_pipeline,
    "best_pipeline.joblib"
)
```

The bare classifier was not saved separately as the deployment artifact.

This allows the saved model to accept raw input data and perform preprocessing automatically.

---

# 27. Reloading the Saved Pipeline

The saved pipeline can be reloaded using:

```python
import joblib

loaded_pipeline = joblib.load(
    "best_pipeline.joblib"
)
```

The pipeline can then be used directly with raw feature values:

```python
prediction = loaded_pipeline.predict(new_data)

print(prediction)
```

This confirms that preprocessing and prediction are packaged together in one reusable object.

---



