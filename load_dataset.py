import pandas as pd
import requests
import io
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import Product, User, Feedback, Base
from config import logger
import random

def download_dataset():
    
    """
Downloads the Online Retail dataset from UCI ML repository and saves it locally as a CSV file.

Returns:
    pd.DataFrame: The loaded Excel dataset as a pandas DataFrame.
"""

    logger.info("Downloading Online Retail Dataset...")
    url = "https://archive.ics.uci.edu/ml/machine-learning-databases/00352/Online%20Retail.xlsx"
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception("Failed to download dataset")
    df = pd.read_excel(io.BytesIO(response.content))
    df.to_csv("online_retail.csv", index=False)
    logger.info("Dataset downloaded and saved as online_retail.csv")
    return df

def preprocess_dataset(df):
    
    """
    Preprocesses the raw dataset to create clean, structured data for Products, Users, and Feedback.

    Steps include:
        - Dropping missing CustomerID and Description
        - Filtering positive quantity transactions
        - Inferring user preferences and randomizing product features

    Args:
        df (pd.DataFrame): Raw dataset

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]: Products, Users, and Feedback dataframes
    """

    logger.info("Preprocessing dataset...")
    
    # Remove rows with missing CustomerID or Description
    df = df.dropna(subset=["CustomerID", "Description"])
    
    # Convert CustomerID to integer safely
    df.loc[:, "CustomerID"] = df["CustomerID"].astype(int)
    
    # Remove negative quantities
    df = df[df["Quantity"] > 0]
    
    # Create Product DataFrame
    products = df[["StockCode", "Description", "UnitPrice"]].drop_duplicates()
    products = products.rename(columns={
        "StockCode": "id",
        "Description": "name",
        "UnitPrice": "price"
    })
    # Ensure id is string and deduplicate
    products["id"] = products["id"].astype(str)
    duplicate_ids = products[products["id"].duplicated(keep=False)]
    if not duplicate_ids.empty:
        logger.warning(f"Found {len(duplicate_ids)} duplicate product IDs: {duplicate_ids['id'].tolist()}")
    products = products.drop_duplicates(subset="id", keep="first")
    
    products["category"] = products["name"].apply(
        lambda x: "Home Decor" if "LIGHT" in x.upper() or "HOLDER" in x.upper() else "Gifts"
    )
    products["features"] = products["name"].apply(
        lambda x: {"material": random.choice(["ceramic", "metal", "plastic"])}
    )
    
    # Create User DataFrame
    users = df[["CustomerID"]].drop_duplicates()
    users = users.rename(columns={"CustomerID": "id"})
    users["username"] = users["id"].apply(lambda x: f"user_{x}")
    users["hashed_password"] = "bcrypt_hashed_placeholder"
    
    # Infer preferences
    user_prefs = df.groupby("CustomerID").agg({
        "Description": lambda x: {"preferred_categories": "Home Decor" if any("LIGHT" in d.upper() or "HOLDER" in d.upper() for d in x) else "Gifts"}
    }).reset_index().rename(columns={"CustomerID": "id", "Description": "preferences"})
    users = users.merge(user_prefs, on="id")
    
    # Create Feedback DataFrame
    feedback = df[["CustomerID", "StockCode", "Quantity"]].copy()
    feedback["rating"] = feedback["Quantity"].apply(lambda x: min(5, max(1, int(x / 2))))
    feedback = feedback.rename(columns={
        "CustomerID": "user_id",
        "StockCode": "product_id",
        "rating": "rating"
    })
    feedback["product_id"] = feedback["product_id"].astype(str)
    feedback["comment"] = None
    
    logger.info("Preprocessing complete: %d products, %d users, %d feedback entries",
                len(products), len(users), len(feedback))
    return products, users, feedback

def load_to_database(products_df, users_df, feedback_df):
    """
    Populates the database tables with the processed Products, Users, and Feedback data.

    Args:
        products_df (pd.DataFrame): Preprocessed product data
        users_df (pd.DataFrame): Preprocessed user data
        feedback_df (pd.DataFrame): Preprocessed feedback data
    """
    logger.info("Loading data into database...")
    db: Session = SessionLocal()
    
    try:
        # Log sample data with types
        sample_product = products_df.iloc[0].to_dict()
        logger.debug(f"Sample product: {sample_product}")
        logger.debug(f"Sample product types: { {k: type(v).__name__ for k, v in sample_product.items()} }")
        
        # Load Products
        for _, row in products_df.iterrows():
            product = Product(
                id=str(row["id"]),
                name=str(row["name"]),
                description=str(row["name"]),
                category=str(row["category"]),
                price=float(row["price"]),
                features=row["features"]
            )
            db.merge(product)
        db.flush()  # Synchronize session
        
        # Load Users
        for _, row in users_df.iterrows():
            user = User(
                id=int(row["id"]),
                username=str(row["username"]),
                hashed_password=str(row["hashed_password"]),
                preferences=row["preferences"]
            )
            db.merge(user)
        db.flush()  # Synchronize session
        
        # Load Feedback
        for _, row in feedback_df.iterrows():
            feedback = Feedback(
                user_id=int(row["user_id"]),
                product_id=str(row["product_id"]),
                rating=float(row["rating"]),
                comment=row["comment"]
            )
            db.add(feedback)
        
        db.commit()
        logger.info("Data loaded successfully")
    except Exception as e:
        db.rollback()
        logger.error(f"Error loading data: {str(e)}")
        raise
    finally:
        db.close()

def main():

    """
    Main function that recreates the DB schema, downloads the dataset, processes it, and loads it.
    """

    # Recreate database schema
    logger.info("Recreating database schema...")
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    
    df = download_dataset()
    products_df, users_df, feedback_df = preprocess_dataset(df)
    load_to_database(products_df, users_df, feedback_df)

if __name__ == "__main__":
    main()