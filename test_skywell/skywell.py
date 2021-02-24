import streamlit as st
from os import listdir
import matplotlib.pyplot as plt
import pandas as pd

# List logs in the folders
logs1 = [f for f in listdir("skywell1") if "SkywellDataLog" in f]
logs2 = [f for f in listdir("skywell2") if "SkywellDataLog" in f]

# Get all logs for fist machine and make a single dataframe
logs1_df_list = []
base1 = "skywell1/"
for log in logs1:
    filename = base1 + log
    day_df_full = pd.read_csv(filename, sep="|")
    day_df = day_df_full.filter(
        [
            "DateTime",
            "Ambient Humidity",
            "Ambient Temp Degrees C",
            "Water Type Being Dispensed",
            "Device Key",
        ],
        axis=1,
    )
    logs1_df_list.append(day_df)
skywell1_df = pd.concat(logs1_df_list)

# Split DateTime column and convert date in datetime format
skywell1_df[["Date", "Time"]] = skywell1_df["DateTime"].str.split(" ", expand=True)
skywell1_df["Date"] = pd.to_datetime(skywell1_df["Date"], format="%d/%m/%Y")
skywell1_df["Month"] = skywell1_df["Date"].dt.strftime("%m-%Y")
skywell1_df["Date"] = skywell1_df["Date"].dt.strftime("%Y-%m-%d")

# Make the dispensed water as dummy
skywell1_df = pd.concat(
    [skywell1_df, pd.get_dummies(skywell1_df["Water Type Being Dispensed"])], axis=1
)

# Drop redundant variables
skywell1_df.drop(
    ["DateTime", "Water Type Being Dispensed", "Off"], axis=1, inplace=True
)

# Select month of reporting
st.sidebar.header("Seleziona le impostazioni per il report")
months_list = sorted(skywell1_df["Month"].unique())
selected_months = st.sidebar.multiselect("Mese", months_list, months_list)

# Filter dataframe according to month selection
skywell1_filtered_df = skywell1_df[skywell1_df["Month"].isin(selected_months)]

# Dispensed water figures and plot
water_days_df = skywell1_filtered_df.groupby(by="Date").agg(
    {"Cold": "sum", "Hot": "sum"}
)

# Set conversion from point to liters => 1 point ~ 0.375 liters
point2liter = 0.375
water_days_df["Cold"] = water_days_df["Cold"] * point2liter
water_days_df["Hot"] = water_days_df["Hot"] * point2liter

# Water totals
tot_cold = water_days_df["Cold"].sum()
tot_hot = water_days_df["Hot"].sum()
tot_water = tot_cold + tot_hot

# Environmental variables (temp and humidity)
h_min = skywell1_filtered_df.groupby(by="Date").agg({"Ambient Humidity": "min"})
h_mean = skywell1_filtered_df.groupby(by="Date").agg({"Ambient Humidity": "mean"})
h_max = skywell1_filtered_df.groupby(by="Date").agg({"Ambient Humidity": "max"})
t_min = skywell1_filtered_df.groupby(by="Date").agg({"Ambient Temp Degrees C": "min"})
t_mean = skywell1_filtered_df.groupby(by="Date").agg({"Ambient Temp Degrees C": "mean"})
t_max = skywell1_filtered_df.groupby(by="Date").agg({"Ambient Temp Degrees C": "max"})

h_min.columns = ["Umidità minima"]
h_mean.columns = ["Umidità media"]
h_max.columns = ["Umidità massima"]
t_min.columns = ["Temp minima"]
t_mean.columns = ["Temp media"]
t_max.columns = ["Temp massima"]

temp_df = pd.concat([t_min, t_mean, t_max], axis=1)
hum_df = pd.concat([h_min, h_mean, h_max], axis=1)

# Plots
# Plot liters of water
# water_plt = water_days_df.plot(kind="bar",stacked=True, title="Litri di acqua erogata tramite Skywell", xlabel="Giorno", ylabel="Litri", colormap="winter")
fig, ax = plt.subplots()

ax.bar(water_days_df.index, water_days_df["Cold"], label="Acqua fredda")
ax.bar(
    water_days_df.index,
    water_days_df["Hot"],
    bottom=water_days_df["Cold"],
    label="Acqua calda",
)
ax.set_ylabel("Litri")
ax.set_xlabel("Giorni")
ax.set_title("Litri di acqua erogata tramite Skywell")
ax.legend()
plt.xticks(rotation=90)

# Plot Humidity
# hum_plt = hum_df.plot(title="Umidità", xlabel="Giorno", ylabel="Umidità %", rot=45)
fig_h, ax_h = plt.subplots()

ax_h.plot(hum_df.index, hum_df["Umidità minima"], label="Umidità minima")
ax_h.plot(hum_df.index, hum_df["Umidità media"], label="Umidità media")
ax_h.plot(hum_df.index, hum_df["Umidità massima"], label="Umidità massima")
ax_h.set_ylabel("Umidità %")
ax_h.set_xlabel("Giorni")
ax_h.set_title("Umidità ambientale")
ax_h.legend()
plt.xticks(rotation=90)

# Plot temperature
# temp_plt = temp_df.plot(title="Temperatura", xlabel="Giorno", ylabel="Gradi Celsius", rot=45)
fig_t, ax_t = plt.subplots()

ax_t.plot(temp_df.index, temp_df["Temp minima"], label="Temperatura minima")
ax_t.plot(temp_df.index, temp_df["Temp media"], label="Temperatura media")
ax_t.plot(temp_df.index, temp_df["Temp massima"], label="Temperatura massima")
ax_t.set_ylabel("Gradi Celsius")
ax_t.set_xlabel("Giorni")
ax_t.set_title("Temperatura ambientale")
ax_t.legend()
plt.xticks(rotation=90)
# Streamlit presentation
st.write(
    """
# Skywell - report di utilizzo

In questa pagina puoi monitorare l'utilizzo del tuo Skywell, per vedere quanta acqua stai risparmiando!
Puoi anche vedere le condizioni ambientali in cui Skywell opera, per assicurarti che possa rendere sempre al meglio.

"""
)

st.write(
    """
## Utilizzo Skywell
"""
)
st.pyplot(fig)

st.write("### Litri di acqua fredda erogati da Skywell :", tot_cold)
st.write("### Litri di acqua calda erogati da Skywell :", tot_hot)
st.write("### Litri di acqua erogati da Skywell in totale :", tot_water)

st.write(
    """
## Umidità ambientale
"""
)
st.pyplot(fig_h)

st.write(
    """
## Temperatura ambiente
"""
)
st.pyplot(fig_t)
