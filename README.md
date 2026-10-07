# EV Intelligence Prediction and Analysis

A data-driven platform for electric vehicle market analysis, sales forecasting, country attractiveness evaluation, and What-If scenario analysis.

## Overview

The **EV Intelligence Prediction and Analysis** system integrates EV sales, economic, energy, financial, and stock market data from multiple sources into a centralized platform. The system uses ETL processing, a Star Schema Data Warehouse, machine learning-based forecasting, country attractiveness analysis, and What-If scenario simulation to provide useful EV market insights.

## Problem Statement

EV-related data is collected from multiple sources and is available in different formats. Manually collecting, cleaning, combining, and analyzing this data is time-consuming and makes it difficult to compare countries, forecast future EV demand, and evaluate market opportunities.

This project provides a centralized solution for collecting, processing, analyzing, and visualizing EV market data.

## Key Features

- Multi-source EV market data collection
- ETL-based data cleaning and standardization
- Star Schema Data Warehouse
- Historical EV sales analysis
- EV sales forecasting for 2025–2030
- Ridge Regression + Bounded CAGR forecasting
- Country Attractiveness Analysis
- Financial and stock market analysis
- What-If scenario simulation
- Interactive EV market dashboard

## Data Sources

| Dataset | Source |
|---|---|
| EV Sales / EV Market Data | International Energy Agency (IEA) |
| GDP | World Bank |
| Population | World Bank |
| Access to Electricity | World Bank |
| Crude Oil Price | World Bank Commodity Markets |
| Company Financial Data | Yahoo Finance |
| Stock Price Data | Yahoo Finance |

## System Workflow

```text
Data Sources
     ↓
Data Collection
     ↓
Data Validation
     ↓
Data Cleaning
     ↓
Data Transformation
     ↓
Star Schema Data Warehouse
     ↓
Data Analysis
     ↓
 ┌─────────────────────┬────────────────────────┐
 │ EV Sales Forecasting│ Country Attractiveness │
 ├─────────────────────┼────────────────────────┤
 │ What-If Simulation  │ Financial & Stock      │
 │                     │ Analysis               │
 └─────────────────────┴────────────────────────┘
     ↓
Generate Results
     ↓
Python Flask REST API
     ↓
React + Vite Dashboard
     ↓
Data Visualization
