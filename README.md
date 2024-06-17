### Connected CSV files:
1. **train.csv** - The training data, comprising time series of features store_nbr, family, and onpromotion as well as the target sales.
2. **stores.csv** - Store metadata, including city, state, type, and cluster.
3. **oil.csv** - Daily oil price. Includes values during both the train and test data timeframes.
4. **holidays_events.csv** - Holidays and Events, with metadata
5. **test.csv** - Test data.
6. **transactions.csv** - data about all transactions for each store during the observed dates.
7. **formodel.csv** - cleared data which is result of executing StoreSales.create_dataset()
All data can be found [here](https://drive.google.com/drive/folders/1GsGW5P7WUz93nP6JpQmecc6UMpfyOsZB)
### Creating dataset: 
*Based on the referenced .csv files, a unified dataset was created, which was used for further processing, filling missing values, and making final predictions. The dataset was obtained by calling the **create_dataset()** method in the [StoreSales.py](https://github.com/zm20200109/Stores-Sales-Prediction/blob/main/code/StoreSales.py) file.*

**To fill missing values**, autocorrelation and lag plot were used. A method was created to isolate the peak of the plot and fill the missing values with the value of the corresponding attribute from the past time with the highest autocorrelation, **considering seasonality observed in attributes** such as transactions.
