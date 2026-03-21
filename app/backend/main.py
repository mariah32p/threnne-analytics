"""
Threnne API Backend (FastAPI)
=============================
Serves the daily-updated Threnne data reports to the React frontend.
Reads directly from the backtester exports directory so data is always fresh.

Run the server:
cd app/backend
uvicorn main:app --reload
"""

import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd

app = FastAPI(title="Threnne Intelligence API", version="1.0.0")

# Allow the React frontend to fetch data (Vite usually runs on 5173, React on 3000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Base path to where your data engine exports the final reports
# Resolved from app/backend/ -> repo root data/exports/
EXPORTS_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "data", "exports")
)


def get_split_report(filename: str):
    """Helper function to load a CSV and split the signal based on baseline volume."""
    filepath = os.path.join(EXPORTS_DIR, filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail=f"Report {filename} not found.")

    df = pd.read_csv(filepath)
    df = df.replace([pd.NA, float("inf"), float("-inf")], None)

    # Split the signal: > 50 baseline = Accelerating, <= 50 baseline = Emerging
    accelerating_df = df[df["baseline_count"] > 50].head(10)
    emerging_df = df[df["baseline_count"] <= 50].head(10)

    return {
        "accelerating": accelerating_df.to_dict(orient="records"),
        "emerging": emerging_df.to_dict(orient="records"),
    }


def load_report(filename: str):
    """Dynamically loads a CSV on request to support daily scraper updates."""
    filepath = os.path.join(EXPORTS_DIR, filename)
    if not os.path.exists(filepath):
        raise HTTPException(
            status_code=404,
            detail=f"Report {filename} not found. Has the data engine run?",
        )

    # Read CSV and replace any NaN/Infinity values with None (null in JSON)
    df = pd.read_csv(filepath)
    df = df.replace([pd.NA, float("inf"), float("-inf")], None)

    # Convert to a list of dictionaries for the frontend
    return df.to_dict(orient="records")


@app.get("/")
def read_root():
    return {"status": "Threnne API is live.", "confidence_rule": "Enforced"}


# --- THE FORECAST ENDPOINTS (The Live Product) ---


@app.get("/api/v1/forecast/tropes")
def get_rising_tropes():
    """Returns the Live Forecast (2024-2026)"""
    return get_split_report("forecast_report.csv")


@app.get("/api/v1/forecast/stacks")
def get_trope_stacks():
    """Returns the combination forecast (Breakout Stacks)"""
    return {"data": load_report("forecast_stacks_report.csv")}


# --- THE BACKTEST ENDPOINTS (The Confidence UI) ---


@app.get("/api/v1/backtest/tropes")
def get_backtested_tropes():
    """Returns the Historical Backtest (2018-2023)"""
    return get_split_report("backtest_report.csv")


@app.get("/api/v1/backtest/stacks")
def get_backtested_stacks():
    return {"data": load_report("backtest_stacks_report.csv")}
