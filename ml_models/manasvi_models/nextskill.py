import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.metrics import accuracy_score
import pickle

# Data read karna
df = pd.read_csv("skills_data.csv")

# Skills column ko string se list mein convert karna
df['Skills'] = df['Skills'].apply(lambda x: x.split(';'))

# Data preprocess karna
mlb = MultiLabelBinarizer()
skills_encoded = mlb.fit_transform(df['Skills'])

# Encoded skills se DataFrame banana
skills_df = pd.DataFrame(skills_encoded, columns=mlb.classes_)

# Next skill ko target variable ke roop mein add karna
df['Next_Skill'] = df['Next_Skill'].astype('category')

# Train-test split
X = skills_df
y = df['Next_Skill'].cat.codes
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Model ko test data par evaluate karna
y_pred = model.predict(X_test)

# Accuracy calculate karna
accuracy = accuracy_score(y_test, y_pred)
print(f"Model Accuracy: {accuracy:.2f}")

# Model aur encoder ko save karna
with open('skill_recommendation_model.pkl', 'wb') as file:
    pickle.dump(model, file)

with open('mlb.pkl', 'wb') as file:
    pickle.dump(mlb, file)

def recommend_next_skill(skills):
    # User ke skills ko encode karna
    skills_encoded = mlb.transform([skills])  
    
    # Convert the encoded skills to DataFrame with correct column names
    skills_encoded_df = pd.DataFrame(skills_encoded, columns=mlb.classes_)
    
    # Predict the next skill
    predicted_skill_code = model.predict(skills_encoded_df)  
    
    # Decode the predicted skill code
    predicted_skill = df['Next_Skill'].cat.categories[predicted_skill_code[0]]
    
    return predicted_skill

# Example usage with partial skills
user_skills = ['C++', 'C#', 'Java', 'Python'] 
recommended_skill = recommend_next_skill(user_skills)
print(f"Recommended Next Skill: {recommended_skill}")

