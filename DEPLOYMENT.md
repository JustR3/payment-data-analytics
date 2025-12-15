# Streamlit Cloud Deployment Guide

## Automatic Data Generation

This app automatically generates synthetic data on first run if the data directory doesn't exist.

## Deployed URL

Once deployed, your app will be available at:
`https://payment-data-analytics-[your-app-id].streamlit.app`

## Manual Deployment Steps

1. Go to https://share.streamlit.io/
2. Sign in with GitHub
3. Click "New app"
4. Select repository: `JustR3/payment-data-analytics`
5. Set branch: `main`
6. Set main file path: `app.py`
7. Click "Deploy"

## First Run

The app will automatically generate data on first load (takes ~30 seconds).
