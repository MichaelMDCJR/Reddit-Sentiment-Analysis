import numpy as np
import matplotlib.pyplot as plt
import pandas

df = pandas.DataFrame({
    'Name': ['John', 'Sammy', 'Joe'],
    'Age': [45, 38, 90],
    'Height(in cm)': [150, 180, 160]
})

# plotting graph
#df.plot(x="Name", y=["Age", "Height(in cm)"], kind="bar")
#plt.show()

print(df)
#
new_frame = pandas.read_parquet("libertarian.gzip")

fixed_data = new_frame.drop(['titlerating', 'textpos', 'textneg', 'textneu', 'textrating','commpos', 'comneg', 'comneu', 'comrating', 'date'], axis=1)
print(fixed_data)
fixed_data.plot(y=['titlepos', 'titleneg', 'titleneu'], kind="bar")
plt.show()