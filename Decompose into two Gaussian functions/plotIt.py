import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.colors as colors

data = pd.read_csv('output.csv')
fig = plt.figure(figsize=(8, 6))
plt.pcolormesh(data, cmap='gist_rainbow',
               norm=colors.SymLogNorm(linthresh=0.03, linscale=0.03, vmin=400, vmax=406))
plt.title("Plot 2D array")
plt.colorbar()
plt.show()
