import pandas as pd

data = {
            "teacher" : [1],
            "classroom" : [1],
            "toolcode" : [1]
        }
frame = pd.DataFrame(data)
for i in range(10):
    frame.append({
        "teacher" : i//2,
        "classroom" : i + 1,
        "toolcode" :i + 2
    },ignore_index=True)
    # frame.loc[i] = a
print(frame)
value = frame.teacher.value_counts()
print(value)