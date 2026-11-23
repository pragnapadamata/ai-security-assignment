import requests
import matplotlib.pyplot as plt

# Step 1: get the scores from the API
response = requests.get("https://example.com/api/scores")
students = response.json()

# students look like this:
# [{"name": "Pragna", "score": 85},
#  {"name": "Manogna", "score": 90},
#  {"name": "Mia", "score": 78},
#  {"name": "Sia", "score": 92}]

# Step 2: find the average score
names = []
scores = []
for s in students:
    names.append(s["name"])
    scores.append(s["score"])

average = sum(scores) / len(scores)
print("Average score is", average)

# Step 3: make the bar chart
plt.bar(names, scores, color="skyblue")
plt.axhline(average, color="red", linestyle="--", label="Average")
plt.title("Students Test Scores")
plt.xlabel("Students")
plt.ylabel("Score")
plt.legend()
plt.show()
