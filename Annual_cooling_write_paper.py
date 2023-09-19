import pandas as pd
from CoolProp.HumidAirProp import HAPropsSI  #计算湿空气参数

data = pd.read_csv('Beijing.csv') # 读取 CSV 文件
data_path = 'Beijing.csv'  # Specify the path to the data CSV file
percentiles = [0.4, 1, 2]

####################### Function to calculate wet-bulb temperature (WB2M)
def calculate_wb2m(row):
    t2m = row['T2M']+273.15  # Dry-bulb temperature in Celsius
    rh2m = row['RH2M'] / 100  # Convert relative humidity to a ratio (divide by 100)
    ps = row['PS'] * 1000  # Convert atmospheric pressure to Pa (multiply by 1000)
    # Calculate wet-bulb temperature (WB2M) using CoolProp
    wb2m = HAPropsSI('Twb', 'T', t2m, 'R', rh2m, 'P', ps)
    # Convert the result from Kelvin to Celsius
    wb2m_celsius = wb2m - 273.15
    return round(wb2m_celsius, 2)

####################### Function to calculate dew point temperature (DP2M)
def calculate_dp2m(row):
    t2m = row['T2M']+273.15  # Dry-bulb temperature in Celsius
    rh2m = row['RH2M'] / 100  # Convert relative humidity to a ratio (divide by 100)
    ps = row['PS'] * 1000  # Convert atmospheric pressure to Pa (multiply by 1000)
    # Calculate dew point temperature (DP2M) using CoolProp
    dp2m = HAPropsSI('Tdp', 'T', t2m, 'R', rh2m, 'P', ps)
    # Convert the result from Kelvin to Celsius
    dp2m_celsius = dp2m - 273.15
    return round(dp2m_celsius,2)

####################### Function to calculate humidity ratio (HuRadio2M)
def calculate_humidity_ratio(row):
    t2m = row['T2M']+273.15 # Dry-bulb temperature in Celsius
    rh2m = row['RH2M'] / 100  # Convert relative humidity to a ratio (divide by 100)
    ps = row['PS'] * 1000  # Convert atmospheric pressure to Pa (multiply by 1000)
    # Calculate humidity ratio (HuRadio2M) using CoolProp
    h2m = HAPropsSI('H', 'T', t2m, 'R', rh2m, 'P', ps)
    w2m = HAPropsSI('W', 'T', t2m, 'R', rh2m, 'P', ps)
    # Calculate humidity ratio (HuRadio2M) by dividing specific humidity by 1 - specific humidity
    hu_radio_2m = w2m / (1 - w2m)
    return round(hu_radio_2m*1000,2)

####################### Function to calculate Enthalpy2M
def calculate_enthalpy(row):
    t2m = row['T2M']  # Dry-bulb temperature in Celsius
    rh2m = row['RH2M'] / 100  # Convert relative humidity to a ratio (divide by 100)
    ps = row['PS'] * 1000  # Convert atmospheric pressure to Pa (multiply by 1000)
    h2m = row['HuRadio2M']  # Humidity ratio in g/kg
    # Calculate the specific enthalpy (kJ/kg dry-air) using CoolProp
    calculate_enthalpy = HAPropsSI('H', 'T', t2m + 273.15, 'R', rh2m, 'P', ps) / 1000 # Convert to kJ/kg
    # Calculate the enthalpy including the humidity (kJ/kg dry-air)
    return round(calculate_enthalpy , 3)

######################1. Hottest Month
def calculate_avg_temp_extremes(data_path):
    # Load the data from the CSV file to dataframe
    data = pd.read_csv(data_path)
    # Group by month and calculate the average temperature with one decimal place
    monthly_avg_temperature = round(data.groupby('MO')['T2M'].mean(), 1)
    # Find the Month with the minimum and maximum average temperature
    max_avg_temp_month = monthly_avg_temperature.idxmax()
    # Find the minimum and maximum average temperatures
    max_avg_temp = monthly_avg_temperature.max()
    return [max_avg_temp_month, max_avg_temp]
#######################2.Hottest Month DB Range
def hottest_month_db_range(data, target_month):
    # 过滤出目标月份的数据
    target_month_data = data[data['MO'] == target_month]
    # 按日分组并计算每日最大和最小干球温度差，然后计算平均值
    daily_db_ranges = target_month_data.groupby(['YEAR', 'MO', 'DY'])['T2M'].apply(lambda x: x.max() - x.min())
    db_range_avg = daily_db_ranges.mean()
    return db_range_avg
#######################3.Cooling DB / MCWB
def calculate_percentiles_DB(data, percentiles):
    # Step 1: Sort the 'T2M' column in descending order
    sorted_data_t2m = data.sort_values(by='T2M', ascending=False)
    # Step 2: Calculate the values corresponding to the specified percentiles
    percentile_labels = [f"{percentile}%" for percentile in percentiles]
    percentile_values_t2m = {}
    for percentile in percentiles:
        # Calculate the index for the current percentile (rounded to the nearest integer)
        percentile_index = int(len(sorted_data_t2m) * (percentile / 100))
        # Extract the value corresponding to the current percentile
        percentile_values_t2m[f"{percentile}%"] = sorted_data_t2m.iloc[percentile_index]['T2M']
    return percentile_values_t2m
def calculate_average_wb2m(data, percentile_values):
    # Step 3: Find the corresponding 'WB2M' values for each percentile and calculate the average 'WB2M'
    average_wb2m_values = []
    for t2m_percentile in percentile_values.values():
        t2m_data = data[data['T2M'] == t2m_percentile]
        average_wb2m_values.append(t2m_data['WB2M'].mean())
    return average_wb2m_values
####################### 4.Evaporation WB/MCDB
def calculate_percentiles_WB(data, column, percentiles):
    # Step 1: Sort the specified column in descending order
    sorted_data = data.sort_values(by=column, ascending=False)
    # Step 2: Calculate the values corresponding to the specified percentiles
    percentile_labels = [f"{percentile}%" for percentile in percentiles]
    percentile_values = {}
    for percentile in percentiles:
        # Calculate the index for the current percentile (rounded to the nearest integer)
        percentile_index = int(len(sorted_data) * (percentile / 100))
        # Extract the value corresponding to the current percentile
        percentile_values[percentile_labels[percentiles.index(percentile)]] = sorted_data.iloc[percentile_index][column]
    return percentile_values
def calculate_average_t2m(data, percentile_values):
    # Step 3: Find the corresponding 'T2M' values for each percentile and calculate the average 'T2M'
    average_t2m_values = []
    for wb2m_percentile in percentile_values.values():
        wb2m_data = data[data['WB2M'] == wb2m_percentile]
        average_t2m_values.append(wb2m_data['T2M'].mean())
    return average_t2m_values
####################### 5.Calculate MCWS/PCWD to 0.4%
def calculate_percentiles(data, column, percentiles):
    sorted_data = data.sort_values(by=column, ascending=False)
    percentile_values = {}
    for percentile in percentiles:
        percentile_index = int(len(sorted_data) * percentile / 100)
        percentile_values[percentile] = sorted_data.iloc[percentile_index][column]
    return percentile_values
def calculate_average_ws(data, t2m_value):
    t2m_data = data[data['T2M'] == t2m_value]
    return t2m_data['WS10M'].mean()
def calculate_most_frequent_wd(data, t2m_value):
    t2m_data = data[data['T2M'] == t2m_value]
    most_frequent_wd = t2m_data['WD10M'].mode().iloc[0]
    return most_frequent_wd
#######################  6.Dehumidification DP/MCDB and HR
def calculate_percentiles(data, column, percentiles):
    sorted_data = data.sort_values(by=column, ascending=False)
    percentile_values = {percentile: sorted_data[column].iloc[int(len(sorted_data) * (percentile / 100))] for percentile in percentiles}
    return percentile_values
def calculate_average_t2m_for_dp_percentiles(data, percentiles_values_dp):
    average_t2m_for_dp_percentiles = {}
    for percentile, dp_value in percentiles_values_dp.items():
        temp_data = data[data['DP2M'] == dp_value]
        average_t2m = round(temp_data['T2M'].mean(), 2)
        average_t2m_for_dp_percentiles[percentile] = average_t2m
    return average_t2m_for_dp_percentiles
####################### 7. Enthalpy/MCDB
def calculate_average_t2m(data, column, percentiles):
    sorted_data = data.sort_values(by=column, ascending=False)
    average_t2m_values = {}
    for percentile in percentiles:
        column_value = sorted_data[column].quantile(1 - percentile / 100)
        temp_data = data[data[column] >= column_value]
        average_t2m = round(temp_data['T2M'].mean(), 2)
        average_t2m_values[percentile] = (column_value, average_t2m)
    return average_t2m_values
if __name__ == '__main__':
    ###### WB2M
    # Calculate wet-bulb temperature for each row and add it as a new column
    data['WB2M'] = data.apply(calculate_wb2m, axis=1)
    # Save the updated DataFrame back to the CSV file
    data.to_csv('Beijing.csv', index=False)

    ###### DP2M
    # Calculate dew point temperature for each row and add it as a new column
    data['DP2M'] = data.apply(calculate_dp2m, axis=1)
    # Save the updated DataFrame back to the CSV file
    data.to_csv('Beijing.csv', index=False)

    ###### HuRadio2M
    # Calculate humidity ratio for each row and add it as a new column
    data['HuRadio2M'] = data.apply(calculate_humidity_ratio, axis=1)
    # Save the updated DataFrame back to the CSV file
    data.to_csv('Beijing.csv', index=False)

    ######  Enthalpy2M
    # Calculate Enthalpy2M for each row and add it as a new column
    data['Enth2M'] = data.apply(calculate_enthalpy, axis=1)
    # Save the updated DataFrame back to the CSV file
    data.to_csv('Beijing.csv', index=False)
 ###### Calculate Hottest Month
    max_avg_temp_month, max_avg_temp = calculate_avg_temp_extremes(data_path)
    print(f"最大平均温度所在的月份: {max_avg_temp_month}")
    print(f"最大平均温度: {max_avg_temp:.1f} °C")

######## Calculate Hottest Month DB Range
    # target_month= max_avg_temp_month
    # # target_month = 7  # 7代表7月
    # hottest_month_range = hottest_month_db_range(data, target_month)
    # print(f"所有年份的{target_month}月每日最高温度与最低温度之差的平均值是：{hottest_month_range:.1f}°C")
    #
###### Calculate  Cooling DB / MCWB
    # percentile_values = calculate_percentiles_DB(data, percentiles)
    # average_wb2m_values = calculate_average_wb2m(data, percentile_values)
    # percentile_labels = [f"{percentile}%" for percentile in percentiles]
    # # Output the percentile values
    # for percentile_label, t2m_value in percentile_values.items():
    #     print(f"排名为{percentile_label}的T2M值为: {t2m_value:.2f} °C")
    # # Output the average WB2M values
    # for percentile_label, wb2m_value in zip(percentile_labels, average_wb2m_values):
    #     print(f"排名为{percentile_label}的T2M对应的平均湿球温度WB2M为: {wb2m_value:.2f} °C")

###### Calculate Evaporation WB/MCDB
    # percentile_values = calculate_percentiles_WB(data, 'WB2M', percentiles)
    # average_t2m_values = calculate_average_t2m(data, percentile_values)
    # percentile_labels = [f"{percentile}%" for percentile in percentiles]
    # # Output the percentile values
    # for percentile_label, wb2m_value in percentile_values.items():
    #     print(f"排名为{percentile_label}的湿球温度WB2M值为: {wb2m_value:.2f} °C")
    # # Output the average T2M values
    # for percentile_label, t2m_value in zip(percentile_labels, average_t2m_values):
    #     print(f"排名为{percentile_label}的湿球温度WB2M对应的平均干球温度T2M为: {t2m_value:.2f} °C")

###### Calculate MCWS/PCWD to 0.4%
    # percentiles = [0.4]
    # t2m_values = calculate_percentiles(data, 'T2M', percentiles)
    # for percentile, t2m_value in t2m_values.items():
    #     print(f"{percentile:.1f}% percentile of T2M: {t2m_value:.2f} °C")
    #     average_ws = calculate_average_ws(data, t2m_value)
    #     print(f"Average wind speed for T2M = {percentile:.1f}% percentile: {average_ws:.2f} m/s")
    #     most_frequent_wd = calculate_most_frequent_wd(data, t2m_value)
    #     print(f"Most frequent wind direction for T2M = {percentile:.1f}% percentile: {most_frequent_wd}")

###### Dehumidification DP/MCDB and HR
     ## Task 1: Calculate percentiles for 'HuRadio2M' (specific enthalpy)
    # percentiles_hu_radio = [0.4, 1, 2]
    # percentiles_values_hu_radio = calculate_percentiles(data, 'HuRadio2M', percentiles_hu_radio)
    # # Task 2: Calculate percentiles for 'DP2M' (dew point temperature)
    # percentiles_dp = [0.4, 1, 2]
    # percentiles_values_dp = calculate_percentiles(data, 'DP2M', percentiles_dp)
    # # Task 3: Calculate average 'T2M' (dry-bulb temperature) for different percentiles of 'DP2M'
    # average_t2m_for_dp_percentiles = calculate_average_t2m_for_dp_percentiles(data, percentiles_values_dp)
    # # Output results
    # print("Percentiles for HuRadio2M:", percentiles_values_hu_radio)
    # print("Percentiles for DP2M:", percentiles_values_dp)
    # print("Average T2M for different percentiles of DP2M:", average_t2m_for_dp_percentiles)
###### Enthalpy/MCDB
    percentiles = [0.4, 1, 2]
    # Task: Calculate average 'T2M' for different percentiles of 'Enth2M'
    average_t2m_values = calculate_average_t2m(data, 'Enth2M', percentiles)
    # Output results
    for percentile in percentiles:
        column_value, average_t2m = average_t2m_values[percentile]
        print(f"Percentile {percentile}%: Enth2M = {column_value:.2f}, Average T2M = {average_t2m:.2f}")
