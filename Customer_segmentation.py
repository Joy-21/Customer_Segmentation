# Step 1: Import required libraries
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import MinMaxScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score


# Step 2: Load the dataset
file_path = "data.csv"  # Adjust the path to match your file's location in Cursors
data = pd.read_csv(file_path, encoding="latin1")

# Step 3: Inspect the data
print("Dataset Overview:")
print(data.head())  # Display the first 5 rows

print("\nColumns in the dataset:")
print(data.columns.tolist())  # List all column names

print("\nMissing values per column:")
print(data.isnull().sum())  # Check for missing values

# Step 1: Drop rows with missing CustomerID
data = data.dropna(subset=["CustomerID"])

print("After cleaning, dataset size:", data.shape)
print("\nMissing values after cleaning:")
print(data.isnull().sum())

# Step 1: Add TotalPrice column
data["TotalPrice"] = data["Quantity"] * data["UnitPrice"]

# Step 2: Verify the new column
print(data[["Quantity", "UnitPrice", "TotalPrice"]].head())

# Step 1: Convert InvoiceDate to datetime format
data["InvoiceDate"] = pd.to_datetime(data["InvoiceDate"])

# Step 2: Create a reference date (e.g., the most recent date in the dataset)
reference_date = data["InvoiceDate"].max()

rfm = data.groupby("CustomerID").agg({
    "InvoiceDate": lambda x: (reference_date - x.max()).days,  # Recency
    "InvoiceNo": "count",  # Frequency
    "TotalPrice": "sum"  # Monetary
})

# Step 4: Rename columns for clarity
rfm.rename(columns={
    "InvoiceDate": "Recency",
    "InvoiceNo": "Frequency",
    "TotalPrice": "Monetary"
}, inplace=True)

# Step 5: Display RFM table
print(rfm.head())

scaler = MinMaxScaler()
rfm_normalized = scaler.fit_transform(rfm)

rfm_normalized = pd.DataFrame(rfm_normalized, columns=["Recency", "Frequency", "Monetary"], index=rfm.index)

print(rfm_normalized.head())

k = 4  # Start with 4 clusters (this can be adjusted)

# Step 2: Apply K-Means
kmeans = KMeans(n_clusters=k, random_state=42)
rfm_normalized["Cluster"] = kmeans.fit_predict(rfm_normalized)

# Step 3: Check cluster assignments
print(rfm_normalized.head())

# Step 4: Add cluster labels to the original RFM DataFrame for analysis
rfm["Cluster"] = rfm_normalized["Cluster"]

# Step 5: View cluster statistics
print(rfm.groupby("Cluster").mean())

score = silhouette_score(rfm_normalized[["Recency", "Frequency", "Monetary"]], rfm_normalized["Cluster"])
print(f"Silhouette Score: {score}")

plt.figure(figsize=(10, 6))
sns.scatterplot(
    x=rfm_normalized["Recency"],
    y=rfm_normalized["Frequency"],
    hue=rfm_normalized["Cluster"],
    palette="viridis"
)
plt.title("Customer Clusters (Recency vs. Frequency)")
plt.xlabel("Recency (Normalized)")
plt.ylabel("Frequency (Normalized)")
plt.legend(title="Cluster")
plt.show()

# Step 2: Create another plot for Monetary vs. Frequency
plt.figure(figsize=(10, 6))
sns.scatterplot(
    x=rfm_normalized["Monetary"],
    y=rfm_normalized["Frequency"],
    hue=rfm_normalized["Cluster"],
    palette="viridis"
)
plt.title("Customer Clusters (Monetary vs. Frequency)")
plt.xlabel("Monetary (Normalized)")
plt.ylabel("Frequency (Normalized)")
plt.legend(title="Cluster")
plt.show()

# Step 1: Analyze the average RFM values for each cluster
cluster_analysis = rfm.groupby("Cluster").mean()
print("Cluster Analysis:")
print(cluster_analysis)

# Step 1: Map cluster numbers to segment names
rfm["Segment"] = rfm["Cluster"].map({
    0: "Loyal Customers",
    1: "Dormant Customers",
    2: "New Customers",
    3: "One-Time Big Spenders"
})

# Step 2: Save the segmented RFM table to a CSV file
rfm.to_csv("customer_segmentation.csv")

# Step 3: Display a preview
print(rfm.head())

 